import discord
import asyncio
import json
from collections import deque # ring buffer


class MessageHistory:
    """
    Stores a limited rolling history of messages per Discord channel.

    The history is maintained as a fixed-size queue (FIFO) per channel,
    keeping only the most recent messages up to a configured limit.
    """

    def __init__(self, max_messages: int = 20):
        """
        Initialize the message history container.

        Args:
            max_messages: Maximum number of messages to keep per channel.
        """
        self.max_messages = max_messages
        # channel_id -> deque[(author, content)]
        self.history: dict[int, deque[tuple[str, str]]] = {}

    def add(self, message: discord.Message, is_self: bool = False) -> None:
        """
        Add a message to the history of its channel.

        If the channel does not yet have a history, it is created.
        When the maximum size is reached, older messages are discarded.

        Args:
            message: Discord message to store.
        """
        channel_id = message.channel.id
        if channel_id not in self.history:
            self.history[channel_id] = deque(maxlen=self.max_messages)

        author = (
            f"{message.author.display_name} (you)"
            if is_self
            else message.author.display_name
        )

        self.history[channel_id].append(
            (author, message.content)
        )

    def get_formatted(self, channel_id: int) -> str:
        """
        Retrieve the formatted message history for a channel.

        Messages are returned as a single string in chronological order,
        formatted as '<author>: <message>' per line.

        Args:
            channel_id: Discord channel identifier.

        Returns:
            A formatted string containing the message history,
            or an empty string if no history exists for the channel.
        """
        if channel_id not in self.history:
            return ""

        return "\n".join(
            f"{author}: {message}"
            for author, message in self.history[channel_id]
        )


class MessageCounter:
    """
    Counts messages per channel and signals when a threshold is reached.

    Intended for rate limiting or triggering actions after a certain
    number of messages have been received.
    """

    def __init__(self, max_messages: int = 10):
        """
        Initialize the message counter.

        Args:
            max_messages: Number of messages required to trigger the limit.
        """
        self.max_messages = max_messages
        # channel_id -> count
        self.counter: dict[int, int] = {}

    def increment(self, channel_id: int) -> bool:
        """
        Increment the message count for a channel.

        Args:
            channel_id: Discord channel identifier.

        Returns:
            True if the message count has reached or exceeded the limit,
            False otherwise.
        """
        self.counter[channel_id] = self.counter.get(channel_id, 0) + 1
        return self.counter[channel_id] >= self.max_messages

    def reset(self, channel_id: int) -> None:
        """
        Reset the message count for a channel.

        Args:
            channel_id: Discord channel identifier.
        """
        self.counter[channel_id] = 0


class InactiveTimer:
    """
    Executes an asynchronous callback after a period of inactivity.

    The timer can be reset or cancelled. Resetting restarts the countdown.
    Only one timer task is active at any given time.
    """

    def __init__(self, seconds: int, callback):
        """
        Initialize the inactivity timer.

        Args:
            seconds: Duration of inactivity before triggering the callback.
            callback: Asynchronous callable executed when the timer expires.
        """
        self.seconds = seconds
        self.callback = callback
        self._task: asyncio.Task | None = None

    def init(self):
        self.reset()

    def reset(self):
        """
        Reset the timer and restart the inactivity countdown.

        Any existing timer task is cancelled before starting a new one.
        """
        self.cancel()
        self._task = asyncio.create_task(self._run())

    def cancel(self):
        """
        Cancel the currently running timer task, if any.
        """
        if self._task and not self._task.done():
            self._task.cancel()

    async def _run(self):
        """
        Internal coroutine that waits for the inactivity period
        and executes the callback if not cancelled.
        """
        try:
            await asyncio.sleep(self.seconds)
            await self.callback()
        except asyncio.CancelledError:
            pass

class DiscordMessageHandler:
    """
    Handles incoming messages and sends the bot's response back to Discord.
    """
    def __init__(self, llm):
        self.llm = llm

    async def handle(self,message: discord.Message, trigger: str, history: str):
        content = message.content
        for user in message.mentions:
            content = content.replace(f"<@{user.id}>", "").replace(f"<@!{user.id}>", "")

        content = content.strip()
        payload = {
            "trigger": trigger,
            "channel_name": message.channel.name,
            "author": message.author.display_name,
            "message": content,
            "history": history
        }

        prompt = json.dumps(payload, indent=2, ensure_ascii=False)
        print("Send: " + prompt)
        try:
            response = self.llm.get_response(prompt)
        except Exception as e:
            print("⚠️ LLM error:", e)
            return

        print(f"Response context: {response.memory_proposal}")
        print(f"\033[92mResponse message: {response.message}\033[0m")
        
        if response.message:
            await message.channel.send(response.message)

    async def handle_inactive(self, bot):
        """
        Sends an inactivity message to a predefined channel.
        If the channel does not exist, nothing is sent.

        Args:
            bot: is expected to be a DiscordBot instance.
        """
        channel = discord.utils.get(bot.get_all_channels(), name="meme-bot") # TODO configurable
        if not channel:
            print(f"Channel not found.")
            return

        history = bot.message_history.get_formatted(channel.id)

        payload = {
            "trigger": "inactive",
            "history": history
        }

        prompt = json.dumps(payload, indent=2, ensure_ascii=False)
        try:
            response = self.llm.get_response(prompt)
        except Exception as e:
            print("⚠️ LLM error:", e)
            return

        if response.message:
            await channel.send(response.message)

    async def handle_conversation_activity(self, bot, active_channels: set[int]):
        """
        Handles detected conversation activity in a channel.
        """
        for channel_id in active_channels:
            channel = discord.utils.get(bot.get_all_channels(), id=channel_id)
            if not channel:
                continue

            history = bot.message_history.get_formatted(channel_id)

            payload = {
                "trigger": "conversation_activity",
                "history": history
            }

            prompt = json.dumps(payload, indent=2, ensure_ascii=False)
            try:
                response = self.llm.get_response(prompt)
            except Exception as e:
                print("⚠️ LLM error:", e)
                return

            if response.message:
                await channel.send(response.message)

class ConversationWatcher:
    """
    Periodically evaluates whether there has been new activity
    in any channel since the last check.
    """

    def __init__(self, seconds: int, callback):
        self.seconds = seconds
        self.callback = callback
        self._active_channels: set[int] = set()
        self._task: asyncio.Task | None = None

    def mark_activity(self, channel_id: int):
        self._active_channels.add(channel_id)

    def reset(self, channel_id: int):
        self._active_channels.discard(channel_id)

    def is_active(self, channel_id: int) -> bool:
        return channel_id in self._active_channels

    def start(self):
        if not self._task:
            self._task = asyncio.create_task(self._run())

    def cancel(self):
        if self._task and not self._task.done():
            self._task.cancel()

    async def _run(self):
        try:
            while True:
                await asyncio.sleep(self.seconds)
                if self._active_channels:
                    await self.callback(self._active_channels.copy())
                    self._active_channels.clear()
        except asyncio.CancelledError:
            pass
