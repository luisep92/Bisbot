import discord
import json
from GptWrapper import BisbalWrapper
from Config import Config
from discord import app_commands
from Helpers import MessageCounter, MessageHistory, InactiveTimer, DiscordMessageHandler, ConversationWatcher

class DiscordBot(discord.Client):
    def __init__(self, llm):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.config = Config()
        self.message_counter = MessageCounter()
        self.message_history = MessageHistory()
        self.message_handler = DiscordMessageHandler(llm)
        self.conversation_watcher = ConversationWatcher(seconds=30, callback=self.on_conversation_activity)
        self.inactive_timer = InactiveTimer(seconds = 30 * 60, callback = self.on_inactive)
        self.permitted_channels: set[int] = set()  # If empty, all channels are permitted
        self.test_channels: set[int] = set()
        self.keywords: list[str] = []

    async def on_conversation_activity(self, active_channels: set[int]):
        await self.message_handler.handle_conversation_activity(self, active_channels)

    async def on_inactive(self):
        await self.message_handler.handle_inactive(self)
        self.inactive_timer.reset()

    async def on_slash_command(self, interaction: discord.Interaction, channel_name: str, prompt: str):
        # Only allow from test channels
        if interaction.channel_id not in self.test_channels:
            await interaction.response.send_message(f"Channel '{channel_name}' is not a test channel.", ephemeral=True)
            return

        target_channel = discord.utils.get(self.get_all_channels(), name=channel_name)
        if not target_channel:
            await interaction.response.send_message(f"Channel '{channel_name}' not found.", ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        response = await self.message_handler.handle_command(self, target_channel, prompt)
        await interaction.followup.send(f"Response: {response}", ephemeral=True)

    async def on_ready(self):
        print(f"Connected as {self.user}")
        self.config = self.config.read()
        self._load_config(self.config)
        tree = app_commands.CommandTree(self)

        @tree.command(name="bisbot")
        async def bisbot(interaction: discord.Interaction, channel: str, prompt: str):
            await self.on_slash_command(interaction, channel, prompt)

        await tree.sync()
        self.inactive_timer.init()
        self.conversation_watcher.start()

    async def on_message(self, message: discord.Message):
        if not self.is_allowed_channel(message.channel.id):
            return

        if message.channel.id in self.test_channels:
            pass # TODO Slash commands private testing

        if message.author == self.user:
            channel = message.channel.id
            self.message_counter.reset(channel)
            self.message_history.add(message, is_self=True)
            self.inactive_timer.reset()
            self.conversation_watcher.reset(channel)
            return

        elif message.author.bot:
            return
        
        channel = message.channel.id
        should_join = self.message_counter.increment(channel)
        self.message_history.add(message)
        self.inactive_timer.reset()
        history = self.message_history.get_formatted(channel)
        self.conversation_watcher.mark_activity(channel)
        
        if self._is_mention_to_me(message):
            await self.message_handler.handle(message, trigger="mention", history=history)
            return

        if await self._is_reply_to_me(message):
            await self.message_handler.handle(message, trigger="reply", history=history)
            return

        if self._contains_keywords(message):
            await self.message_handler.handle(message, trigger="keyword", history=history)
            return

        if should_join:
            self.message_counter.reset(channel)
            self.conversation_watcher.reset(channel)
            await self.message_handler.handle(message, trigger="join", history=history)
            return

    def _is_mention_to_me(self, message: discord.Message) -> bool:
        return self.user in message.mentions
        
    async def _is_reply_to_me(self, message: discord.Message) -> bool:
        ref = message.reference
        if ref is None or ref.message_id is None:
            return False

        try:
            replied = await message.channel.fetch_message(ref.message_id)
        except (discord.NotFound, discord.Forbidden):
            return False

        return replied.author.id == self.user.id
    
    def _contains_keywords(self, message: discord.Message) -> bool:
        if not message.content:
            return False

        text = message.content.lower()
        return any(keyword in text for keyword in self.keywords)

    def _load_config(self, config: Config):
        self.permitted_channels = {
            ch.id
            for ch in self.get_all_channels()
            if ch.name in config.allowed_channels
        }

        self.test_channels = {
            ch.id
            for ch in self.get_all_channels()
            if ch.name in config.test_channels
        }
        self.keywords = [k.lower() for k in config.keywords]

    def is_allowed_channel(self, channel_id: int) -> bool:
        # Empty list mean all channels are allowed
        if not self.permitted_channels:
            return True

        if channel_id in self.test_channels:
            return True

        if channel_id not in self.permitted_channels:
            return False

        return True
