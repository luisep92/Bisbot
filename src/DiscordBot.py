import discord
from Helpers import MessageCounter, MessageHistory, InactiveTimer, DiscordMessageHandler, ConversationWatcher

class DiscordBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.message_counter = MessageCounter()
        self.message_history = MessageHistory()
        self.message_handler = DiscordMessageHandler()
        self.conversation_watcher = ConversationWatcher(seconds=30, callback=self.on_conversation_activity)
        self.inactive_timer = InactiveTimer(seconds = 30 * 60, callback = self.on_inactive)

    async def on_conversation_activity(self, active_channels: set[int]):
        await self.message_handler.handle_conversation_activity(self, active_channels)

    async def on_inactive(self):
        await self.message_handler.handle_inactive(self)
        self.inactive_timer.reset()

    async def on_ready(self):
        print(f"Connected as {self.user}")
        self.inactive_timer.init()
        self.conversation_watcher.start()

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            channel = message.channel.id
            self.message_counter.reset(channel)
            self.message_history.add(message)
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
        keywords = [
            "david", "bisbal",
            "buleria", "bulería",
            "camina",
            "babel",
            "almeria", "almería",
            "maquinas", "máquinas", "makinas",
            "latino"
        ]
        return any(keyword in text for keyword in keywords)
        