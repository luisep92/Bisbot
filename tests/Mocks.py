import discord
from DiscordBot import DiscordBot
  
class MockMessageHandler:
    def __init__(self):
        self.handled_messages = []
        self.inactive_calls = 0
        
    async def handle(self, message: discord.Message, trigger: str, history: str = []):
        self.handled_messages.append(trigger)
        
    async def handle_inactive(self):
        self.handled_messages.append("inactive")
        self.inactive_calls += 1
        
class MockAuthor:
    def __init__(self, name, bot=False, id=1):
        self.display_name = name
        self.bot = bot
        self.id = id


class MockChannel:
    def __init__(self, id=123, replied_message=None):
        self.id = id
        self._replied_message = replied_message

    async def fetch_message(self, message_id):
        """
        Mock implementation of discord.TextChannel.fetch_message().

        In the real Discord API, this method retrieves a message by its ID.
        The bot uses it to determine whether an incoming message is a reply
        to one of its own messages.

        For testing purposes, we do not need real message lookup or network
        access. Instead, this mock returns a preconfigured message
        (`_replied_message`) that simulates the original message being replied to.
        """
        return self._replied_message


class MockMessage:
    def __init__(self, content: str, author: MockAuthor, channel: MockChannel, mentions=None, reference=None):
        self.content = content
        self.author = author
        self.channel = channel
        self.mentions = mentions or []
        self.reference = reference
        
class MockDiscordBot(DiscordBot):
    @property
    def user(self):
        return self._test_user