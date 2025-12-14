import discord
from Helpers import MessageCounter, MessageHistory, InactiveTimer, DiscordMessageHandler

class DiscordBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.message_counter = MessageCounter()
        self.message_history = MessageHistory()
        self.message_handler = DiscordMessageHandler()
        self.inactive_timer = InactiveTimer(
            seconds = 30 * 60, # 30 minutes
            callback = self.on_inactive
        )

    async def on_inactive(self):
        await self.message_handler.handle_inactive()
        self.inactive_timer.reset()

    async def on_ready(self):
        print(f"Conectado como {self.user}")

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            channel = message.channel.id
            self.message_counter.reset(channel)
            self.message_history.add(message)
            self.inactive_timer.reset()
            return

        elif message.author.bot:
            return
        
        channel = message.channel.id
        should_join = self.message_counter.increment(channel)
        self.message_history.add(message)
        self.inactive_timer.reset()
        
        if self._is_mention_to_me(message):
            await self.message_handler.handle(message, "¡Me han llamado!")
            return
            
        if await self._is_reply_to_me(message):
            await self.message_handler.handle(message, "Me han respondido!")
            return
            
        if self._contains_keywords(message):
            await self.message_handler.handle(message, "Contiene keywords!")
            return

        if should_join:
            self.message_counter.reset(channel)
            await self.message_handler.handle(message, "Han pasado 10 mensajes desde mi ultima interaccion en este canal")
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
        keywords = [
            "david", "bisbal",
            "buleria", "bulería",
            "camina y",
            "babel",
            "almeria", "almería",
            "maquinas", "máquinas", "makinas",
            "latino"
        ]
        return any(keyword in text for keyword in keywords)
        