import discord
import asyncio
import time
from collections import deque # ring buffer

class MessageHistory:
    def __init__(self, max_messages: int = 10):
        self.max_messages = max_messages
        # channel_id -> deque[(author, content)]
        self.history: dict[int, deque[tuple[str, str]]] = {}

    def add(self, message: discord.Message) -> None:
        channel_id = message.channel.id
        if channel_id not in self.history:
            self.history[channel_id] = deque(maxlen=self.max_messages)

        self.history[channel_id].append(
            (message.author.display_name, message.content)
        )

    def get_formatted(self, channel_id: int) -> str:
        if channel_id not in self.history:
            return ""

        return "\n".join(
            f"{author}: {message}"
            for author, message in self.history[channel_id]
        )


class MessageCounter:
    def __init__(self, max_messages: int = 10):
        self.max_messages = max_messages
        # channel_id -> count
        self.counter: dict[int, int] = {}

    def increment(self, channel_id: int) -> bool:
        self.counter[channel_id] = self.counter.get(channel_id, 0) + 1
        return self.counter[channel_id] >= self.max_messages


    def reset(self, channel_id: int) -> None:
        self.counter[channel_id] = 0


class InactiveTimer:
    def __init__(self, seconds: int, callback):
        self.seconds = seconds
        self.callback = callback
        self._task: asyncio.Task | None = None
        self.reset()

    def reset(self):
        self.cancel()
        self._task = asyncio.create_task(self._run())

    def cancel(self):
        if self._task and not self._task.done():
            self._task.cancel()

    async def _run(self):
        try:
            await asyncio.sleep(self.seconds)
            await self.callback()
        except asyncio.CancelledError:
            pass


        
class DiscordMessageHandler:
    async def handle(self, message: discord.Message, content: str):
        await message.channel.send(content)
        
    async def handle_inactive(self):
        pass
