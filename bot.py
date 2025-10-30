"""
Bisbot - Discord voice bot with David Bisbal's personality.

Main bot implementation that integrates voice synthesis, speech recognition,
and conversational AI to create an interactive voice bot.
"""

import os
import asyncio
import discord
from discord.ext import commands
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime

from bisbal_personality import BisbalPersonality
from voice_handler import XTTSVoiceHandler
from stt_handler import WhisperSTTHandler


class BisbalBot(commands.Bot):
    """
    Discord bot that speaks with David Bisbal's voice and personality.

    Features:
    - Joins voice channels on command
    - Listens to voice chat and transcribes speech
    - Generates responses in Bisbal's personality
    - Speaks responses using cloned voice
    """

    def __init__(self):
        """Initialize Bisbal bot with required components."""
        # Discord intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.voice_states = True

        super().__init__(command_prefix="!", intents=intents)

        # Component handlers
        self.ai_handler: Optional[BisbalPersonality] = None
        self.voice_handler: Optional[XTTSVoiceHandler] = None
        self.stt_handler: Optional[WhisperSTTHandler] = None

        # State tracking
        self.voice_clients: Dict[int, discord.VoiceClient] = {}
        self.conversation_history: Dict[int, list] = {}  # Per-guild history
        self.is_listening: Dict[int, bool] = {}
        self.temp_dir = Path("temp_audio")
        self.temp_dir.mkdir(exist_ok=True)

        # Configuration
        self.max_history_length = 10  # Keep last 10 messages per guild

    async def setup_hook(self):
        """Initialize all components when bot starts."""
        print("Initializing Bisbal Bot components...")

        # Initialize AI personality
        self.ai_handler = BisbalPersonality()
        if not await self.ai_handler.initialize():
            print("ERROR: Failed to initialize AI handler")
            return

        # Initialize voice synthesis
        reference_audio = os.getenv("BISBAL_VOICE_SAMPLE", "data/bisbal_voice_sample.wav")
        self.voice_handler = XTTSVoiceHandler()
        if not await self.voice_handler.initialize(Path(reference_audio)):
            print("WARNING: Voice handler initialization failed")
            print("Voice synthesis will not work without reference audio")

        # Initialize speech-to-text
        whisper_model = os.getenv("WHISPER_MODEL", "base")
        self.stt_handler = WhisperSTTHandler(model_size=whisper_model)
        if not await self.stt_handler.initialize():
            print("ERROR: Failed to initialize STT handler")
            return

        print("All components initialized successfully!")

    async def on_ready(self):
        """Called when bot is ready and connected to Discord."""
        print(f"Bisbal Bot logged in as {self.user}")
        print(f"Bot is in {len(self.guilds)} guild(s)")
        print("Ready to join voice channels!")

    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState
    ):
        """
        Handle voice state changes (users joining/leaving voice channels).

        This allows the bot to automatically respond when users join.
        """
        # Ignore bot's own voice state changes
        if member == self.user:
            return

        guild_id = member.guild.id

        # Check if bot is in a voice channel in this guild
        if guild_id not in self.voice_clients:
            return

        # User joined the voice channel where bot is
        if after.channel and after.channel == self.voice_clients[guild_id].channel:
            # Optionally greet the user
            # For now, we'll wait for them to speak first
            pass

    async def process_voice_message(self, guild_id: int, user_name: str, audio_path: Path):
        """
        Process a voice message: transcribe, generate response, and speak.

        Args:
            guild_id: Discord guild ID
            user_name: Name of user who spoke
            audio_path: Path to recorded audio file
        """
        try:
            # Transcribe audio
            transcribed_text = await self.stt_handler.transcribe(audio_path)

            if not transcribed_text:
                print("No speech detected in audio")
                return

            print(f"{user_name} said: {transcribed_text}")

            # Get conversation history for this guild
            if guild_id not in self.conversation_history:
                self.conversation_history[guild_id] = []

            history = self.conversation_history[guild_id]

            # Generate Bisbal's response
            response = await self.ai_handler.generate_response(
                transcribed_text,
                conversation_history=history
            )

            print(f"Bisbal responds: {response}")

            # Update conversation history
            history.append({"role": "user", "content": transcribed_text})
            history.append({"role": "assistant", "content": response})

            # Trim history if too long
            if len(history) > self.max_history_length * 2:
                history[:] = history[-self.max_history_length * 2:]

            # Synthesize response to audio
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            response_audio = self.temp_dir / f"response_{guild_id}_{timestamp}.wav"

            if await self.voice_handler.synthesize_speech(response, response_audio):
                # Play in voice channel
                await self.play_audio(guild_id, response_audio)

        except Exception as e:
            print(f"Error processing voice message: {e}")

    async def play_audio(self, guild_id: int, audio_path: Path):
        """
        Play audio file in voice channel.

        Args:
            guild_id: Discord guild ID
            audio_path: Path to audio file to play
        """
        if guild_id not in self.voice_clients:
            print("Not in a voice channel")
            return

        voice_client = self.voice_clients[guild_id]

        # Wait if already playing
        while voice_client.is_playing():
            await asyncio.sleep(0.1)

        # Play audio
        audio_source = discord.FFmpegPCMAudio(str(audio_path))
        voice_client.play(audio_source)

        # Wait for playback to finish
        while voice_client.is_playing():
            await asyncio.sleep(0.1)

        # Clean up temp file
        try:
            audio_path.unlink()
        except:
            pass

    @commands.command(name="join")
    async def join_voice(self, ctx: commands.Context):
        """
        Command: !join
        Makes Bisbal join your voice channel.
        """
        if not ctx.author.voice:
            await ctx.send("Ayyy, tienes que estar en un canal de voz primero!")
            return

        channel = ctx.author.voice.channel
        guild_id = ctx.guild.id

        # Leave current channel if in one
        if guild_id in self.voice_clients:
            await self.voice_clients[guild_id].disconnect()

        # Join new channel
        voice_client = await channel.connect()
        self.voice_clients[guild_id] = voice_client
        self.is_listening[guild_id] = True

        await ctx.send(f"Lo primero de todo, como estan los makinas? Ya estoy aqui en {channel.name}!")

        # Start listening for voice
        await self.start_listening(guild_id, voice_client)

    @commands.command(name="leave")
    async def leave_voice(self, ctx: commands.Context):
        """
        Command: !leave
        Makes Bisbal leave the voice channel.
        """
        guild_id = ctx.guild.id

        if guild_id not in self.voice_clients:
            await ctx.send("No estoy en ningun canal de voz!")
            return

        self.is_listening[guild_id] = False
        await self.voice_clients[guild_id].disconnect()
        del self.voice_clients[guild_id]

        if guild_id in self.conversation_history:
            del self.conversation_history[guild_id]

        await ctx.send("Hasta luego, makinas! Que vaya bien!")

    async def start_listening(self, guild_id: int, voice_client: discord.VoiceClient):
        """
        Start listening to voice channel and processing speech.

        Args:
            guild_id: Discord guild ID
            voice_client: Voice client connection
        """
        # Note: Discord.py voice receiving is complex and requires additional setup
        # This is a simplified placeholder. Full implementation would need:
        # 1. Voice receive setup (discord.py 2.0+ with voice receiving enabled)
        # 2. Audio sink to capture voice data
        # 3. Audio processing to detect speech and save to files

        # For a working implementation, you would use discord.py's voice receive:
        # See: https://github.com/Rapptz/discord.py/blob/master/examples/voice_receive.py

        print(f"Listening started in guild {guild_id}")
        print("NOTE: Voice receiving requires additional setup - see README.md")

        # Placeholder: In real implementation, you would:
        # - Set up voice sink to receive audio
        # - Detect voice activity
        # - Save audio chunks to files
        # - Call process_voice_message() with the audio files

    async def close(self):
        """Clean up resources when bot shuts down."""
        print("Shutting down Bisbal Bot...")

        # Disconnect from all voice channels
        for voice_client in self.voice_clients.values():
            await voice_client.disconnect()

        # Clean up handlers
        if self.ai_handler:
            await self.ai_handler.cleanup()
        if self.voice_handler:
            await self.voice_handler.cleanup()
        if self.stt_handler:
            await self.stt_handler.cleanup()

        # Clean up temp files
        for temp_file in self.temp_dir.glob("*"):
            try:
                temp_file.unlink()
            except:
                pass

        await super().close()


def main():
    """Main entry point for the bot."""
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    # Get Discord token
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        print("ERROR: DISCORD_BOT_TOKEN not found in environment variables")
        print("Please set it in your .env file")
        return

    # Check for required API keys
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("WARNING: ANTHROPIC_API_KEY not found")
        print("AI responses will not work without an API key")
        print("See README.md for alternatives (Ollama)")

    # Create and run bot
    bot = BisbalBot()

    try:
        bot.run(token)
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error running bot: {e}")


if __name__ == "__main__":
    main()
