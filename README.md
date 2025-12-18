# Bisbot

Bisbot is a Discord bot that role-plays **David Bisbal** inside the *Beat Saber España* Discord server.

It is designed as a **one-day-only bot** (December 28th, *Día de los Santos Inocentes*) and intentionally avoids traditional bot commands. Instead, it behaves like a real user: sometimes speaking, sometimes staying silent, and often just observing the conversation.

The project focuses less on *what* the bot says and more on **when it decides to speak**.

---

## Core idea

Bisbot is not a command-based assistant. It is a conversational agent that:

* Reads the channel like a regular user
* Decides *whether* to intervene before deciding *what* to say
* Can intentionally choose silence
* Uses conversation context instead of single-message reactions

This makes the bot feel closer to a human participant than a traditional Discord bot.

---

## Behavior

Bisbot can react in the following situations:

* **Mention**: when directly mentioned
* **Reply**: when someone replies to one of its messages
* **Keyword**: when specific keywords related to David Bisbal appear
* **Join**: automatically joins an ongoing conversation after a message threshold
* **Inactive**: reacts after a long period of silence

Important design rules:

* Silence is a valid and common outcome
* The LLM may decide *not* to respond even when triggered
* Empty or forced messages are never sent

---

## Architecture

```text
src/
├── DiscordBot.py     # Discord client and event routing
├── Helpers.py        # Message history, counters, timers and handlers
├── GptWrapper.py     # OpenAI / ChatGPT wrapper and memory handling
└ main.py             # Entry point


tests/
├── test_discord_bot.py   # Async behavior tests (pytest)
└── Mocks.py              # Discord mocks for testing
```

---

## Message flow

1. A Discord event occurs (message, mention, inactivity, etc.)
2. The bot determines the **trigger type** in code
3. Recent conversation history is collected
4. A structured payload is sent to the LLM
5. The LLM decides:

   * Whether to reply (`response`)
   * Whether something is worth remembering (`context`)
6. If `response` is `null`, the bot stays silent

---

## Memory model

* The bot keeps a **short rolling message history per channel**
* The LLM can optionally propose small memory updates
* Accepted memory is appended to the internal context
* Silence does not generate memory

---

## Testing

The project includes a full async test suite built with `pytest`.

Tests cover:

* Trigger priority rules
* Silence vs response behavior
* Automatic join logic
* Inactivity timer behavior
* Mocked Discord environment (no network required)

All behavior is validated without connecting to Discord or OpenAI.

---

## Current state

* Core bot behavior implemented
* ChatGPT integration working
* Silence handling correctly enforced
* Inactivity handling tested and stable
* Full test coverage for interaction logic

---

## Next steps

Planned improvements:

* **Periodic context evaluation**: every X seconds, if new messages appeared, send the current conversation to the LLM to decide whether an intervention makes sense
* **External persona context**: move the initial in-character context (David Bisbal persona) to a dedicated text file, loaded at startup
* Keep behavioral rules and interaction logic inside the codebase

These changes aim to further separate *personality* from *behavior*, while keeping the system simple and predictable.
