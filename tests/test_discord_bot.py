import asyncio
import sys
from types import SimpleNamespace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pytest
from Mocks import (
    MockAuthor,
    MockChannel,
    MockMessage,
    MockMessageHandler,
    MockDiscordBot,
)


@pytest.fixture
async def server():
    """
    Default fixture for testing containing:
    - bot: Mockup for the discord client class (MockDiscordBot)
    - channel: The channel where the conversation takes place (MockChannel)
    - sender: The user who sent the message (MockAuthor)
    """
    bot = MockDiscordBot()
    bot._test_user = MockAuthor("BisbalBot", bot=True, id=999)
    bot.message_handler = MockMessageHandler()

    return SimpleNamespace(
        bot=bot,
        channel=MockChannel(),
        sender=MockAuthor("Pepe", bot=False, id=1),
    )


@pytest.mark.asyncio
async def test_bot_responds_on_keyword(server):
    msg = MockMessage("me flipa bisbal", server.sender, server.channel)
    await server.bot.on_message(msg)
    assert len(server.bot.message_handler.handled_messages) == 1

@pytest.mark.asyncio
async def test_bot_responds_on_mention(server):
    msg = MockMessage("Messaje", server.sender, server.channel, mentions=[server.bot.user])
    await server.bot.on_message(msg)
    assert len(server.bot.message_handler.handled_messages) == 1

@pytest.mark.asyncio
async def test_bot_responds_on_reply(server):
    replied = MockMessage("previous message", server.bot.user, server.channel)
    server.channel._replied_message = replied
    msg = MockMessage("response", server.sender, server.channel, reference=SimpleNamespace(message_id=1))
    await server.bot.on_message(msg)
    assert len(server.bot.message_handler.handled_messages) == 1

@pytest.mark.asyncio
async def test_bot_joins_after_threshold(server):
    for _ in range(10):
        msg = MockMessage("spam", server.sender, server.channel)
        assert len(server.bot.message_handler.handled_messages) == 0
        await server.bot.on_message(msg)

    assert len(server.bot.message_handler.handled_messages) == 1
    
@pytest.mark.asyncio
async def test_bot_stays_silent(server):
    msg = MockMessage("hola que tal", server.sender, server.channel)
    await server.bot.on_message(msg)

    assert len(server.bot.message_handler.handled_messages) == 0

@pytest.mark.asyncio
async def test_bot_ignores_self_messages(server):
    msg = MockMessage("me hablo a mi mismo", server.bot.user, server.channel)
    await server.bot.on_message(msg)
    assert server.bot.message_handler.handled_messages == []
    
@pytest.mark.asyncio
async def test_on_inactive(server):
    server.bot.inactive_timer.cancel()
    assert server.bot.message_handler.inactive_calls == 0
    await server.bot.on_inactive()
    assert server.bot.message_handler.inactive_calls == 1

@pytest.mark.asyncio
async def test_inactive_timer_triggers(server):
    # Override default 30m timer for a 500ms one
    server.bot.inactive_timer.cancel()
    server.bot.inactive_timer = server.bot.inactive_timer.__class__(
        seconds=0.5,
        callback=server.bot.on_inactive
    )
    server.bot.inactive_timer.init()
    assert server.bot.message_handler.inactive_calls == 0
    await asyncio.sleep(0.6)
    assert server.bot.message_handler.inactive_calls == 1

@pytest.mark.asyncio
async def test_bot_ignores_other_bots(server):
    other_bot = MockAuthor("OtherBot", bot=True, id=2)
    msg = MockMessage("bisbal", other_bot, server.channel)
    await server.bot.on_message(msg)
    assert server.bot.message_handler.handled_messages == []

@pytest.mark.asyncio
async def test_mention_has_priority_over_join(server):
    for _ in range(9):
        await server.bot.on_message(MockMessage("spam", server.sender, server.channel))

    msg = MockMessage("message", server.sender, server.channel, mentions=[server.bot.user])
    await server.bot.on_message(msg)
    assert len(server.bot.message_handler.handled_messages) == 1

@pytest.mark.asyncio
async def test_reply_to_other_user_is_ignored(server):
    other_user = MockAuthor("Juan", bot=False, id=3)
    replied = MockMessage("prev", other_user, server.channel)
    server.channel._replied_message = replied

    msg = MockMessage("respuesta", server.sender, server.channel, reference=SimpleNamespace(message_id=1))
    await server.bot.on_message(msg)
    assert server.bot.message_handler.handled_messages == []

@pytest.mark.asyncio
async def test_mention_has_priority_over_keyword(server):
    msg = MockMessage("bisbal", server.sender, server.channel, mentions=[server.bot.user],)
    await server.bot.on_message(msg)
    assert len(server.bot.message_handler.handled_messages) == 1

@pytest.mark.asyncio
async def test_empty_message_is_ignored(server):
    msg = MockMessage(None, server.sender, server.channel)
    await server.bot.on_message(msg)
    assert server.bot.message_handler.handled_messages == []

@pytest.mark.asyncio
async def test_bot_triggers_conversation_activity(server):
    # Reduce interval for test speed
    server.bot.conversation_watcher.cancel()
    server.bot.conversation_watcher = server.bot.conversation_watcher.__class__(
        seconds=0.05,
        callback=server.bot.on_conversation_activity
    )
    server.bot.conversation_watcher.start()

    msg = MockMessage("message", server.sender, server.channel)
    await server.bot.on_message(msg)
    assert server.bot.message_handler.handled_messages == []
    await asyncio.sleep(0.1)
    assert "conversation_activity" in server.bot.message_handler.handled_messages

@pytest.mark.asyncio
async def test_conversation_activity_is_reset_after_bot_intervention(server):
    server.bot.conversation_watcher.cancel()
    server.bot.conversation_watcher = server.bot.conversation_watcher.__class__(
        seconds=0.05,
        callback=server.bot.on_conversation_activity
    )
    server.bot.conversation_watcher.start()
    msg = MockMessage("bisbal", server.sender, server.channel) #keyword
    await server.bot.on_message(msg)
    msg = MockMessage("dime", server.bot.user, server.channel)
    await server.bot.on_message(msg)
    assert not server.bot.conversation_watcher.is_active(server.channel.id)
    await asyncio.sleep(0.1)
    assert server.bot.message_handler.handled_messages.count("conversation_activity") == 0

@pytest.mark.asyncio
async def test_conversation_activity_is_reset_after_join(server):
    server.bot.conversation_watcher.cancel()
    server.bot.conversation_watcher = server.bot.conversation_watcher.__class__(
        seconds=0.05,
        callback=server.bot.on_conversation_activity
    )
    server.bot.conversation_watcher.start()

    for _ in range(9):
        msg = MockMessage("spam", server.sender, server.channel)
        await server.bot.on_message(msg)

    assert server.bot.conversation_watcher.is_active(server.channel.id)
    await server.bot.on_message(msg) # Trigger join
    assert "join" in server.bot.message_handler.handled_messages
    assert not server.bot.conversation_watcher.is_active(server.channel.id)


@pytest.mark.asyncio
async def test_invalid_llm_json_does_not_crash(server, monkeypatch):

    class FakeResponse:
        message = None
        memory_proposal = None

    def fake_get_response(_):
        raise ValueError("LLM exploded")

    monkeypatch.setattr(
        "Helpers.LLM.get_response",
        fake_get_response
    )

    msg = MockMessage("bisbal", server.sender, server.channel)
    await server.bot.on_message(msg)

    assert "keyword" in server.bot.message_handler.handled_messages