import discord
from DiscordBot import DiscordBot
  
class MockMessageHandler:
    async def handle(self, message: discord.Message, content: str):
        print("{" + content + "}")
        
    async def handle_inactive(self):
        print("Inactivo!")
        
class MockAuthor:
    def __init__(self, name, bot=False, id=1):
        self.display_name = name
        self.bot = bot
        self.id = id


class MockChannel:
    def __init__(self, id=123):
        self.id = id

    async def fetch_message(self, message_id):
        return None  # no replies por ahora


class MockMessage:
    def __init__(
        self,
        content: str,
        author: MockAuthor,
        channel: MockChannel,
        mentions=None,
        reference=None
    ):
        self.content = content
        self.author = author
        self.channel = channel
        self.mentions = mentions or []
        self.reference = reference
        
class MockDiscordBot(DiscordBot):
    @property
    def user(self):
        return self._test_user