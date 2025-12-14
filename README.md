# Bisbot

Bisbot is a Discord bot that uses ChatGPT to role-play *David Bisbal* inside the **Beat Saber España** Discord server.

The bot is intended to be used only on **December 28th (Día de los Santos Inocentes)**.

Instead of using commands, Bisbot behaves like a regular user:
sometimes it speaks, sometimes it stays silent, and most of the time it just reads.

---

## Behavior

- Generates in-character responses using ChatGPT
- Decides **when to speak**, not just what to say
- Responds to:
  - Mentions
  - Replies to its own messages
  - Specific keywords
- Joins conversations automatically after a message threshold
- Remains passive by default
- Triggers an inactivity callback after long silence

---

## Structure

```text
src/
├── DiscordBot.py   # Core behavior logic
├── Helpers.py      # Counters, history and inactivity timer
├── GptWrapper.py   # ChatGPT wrapper
└── Mocks.py        # Discord mocks
tests/
└── test_discord_bot.py   # Behavior tests (pytest + asyncio)
```

---

## Testing

The project includes a full behavior-driven test suite using pytest.
All branches of the message handling logic are covered, including:

- Positive and negative interaction cases
- Priority rules between triggers
- Inactivity handling using a real async timer
- Tests run without Discord or network access

---

## Current state

- Core bot behavior implemented
- ChatGPT wrapper ready
- Message handling logic fully covered by tests
- Deterministic async test suite
