# Bisbot

Bisbot is a Discord bot that simulates a *real participant* in a server conversation using an LLM (OpenAI).
It is intentionally **not** a command-only bot: it listens, waits, and decides *when it makes sense to talk*, based on context, activity, and social cues.

The current personality is a humorous version of **David Bisbal** integrated into the *Beat Saber España* Discord server, but the architecture is generic, reusable and easily adaptable through configuration.

---

## What Bisbot Actually Does

Bisbot observes conversations and may respond when:

* It is **mentioned**
* Someone **replies** to one of its messages
* A **keyword** appears
* A conversation reaches a **message threshold** ("join")
* There is **ongoing activity** without intervention (periodic evaluation)
* The server has been **inactive** for a long time

The key idea is that **Bisbot decides whether to speak**, instead of replying mechanically.

---

## Core Design Principles

* 🧠 **Context-driven** — full recent conversation is sent to the LLM
* 🧍 **Acts like a human** — may choose *not* to reply
* 🔕 **Non-intrusive** — avoids interrupting or repeating itself
* 🧪 **Fully testable** — Discord logic is covered by unit tests, LLM can be manually tested
* 🧩 **Modular** — Discord, LLM, config, and helpers are cleanly separated

---

## Project Structure

```bash
.
├── config/
│   ├── config.json      # Runtime configuration
│   └── context.txt      # Initial personality & memory context
│
├── src/
│   ├── Config.py        # Config loading + defaults
│   ├── DiscordBot.py   # Discord client & event logic
│   ├── GptWrapper.py   # LLM wrapper + memory handling
│   ├── Helpers.py      # Counters, timers, history, handlers
│   └── main.py         # Entry point
│
├── tests/
│   ├── Mocks.py
│   ├── test_config.py
│   ├── test_behavior.py   # Manual test against the real LLM
│   └── test_discord_bot.py
│
├── pytest.ini
└── README.md
```

---

## Configuration

Configuration is split into **behavior** and **personality**.

### `config/config.json`

Controls how the bot behaves:

* `allowed_channels`: where the bot can speak
* `test_channels`: channels where slash commands are allowed
* `keywords`: words that trigger interaction
* `max_context_length`: memory limit
* `max_tokens_response`: LLM output size
* `response_use_llm`: disable LLM for dry runs
* `context_file`: external personality file

Example:

```json
{
  "allowed_channels": ["meme-bot"],
  "test_channels": ["muted-lobby-pepe"],
  "keywords": ["bisbal", "buleria", "camina"],
  "context_file": "context.txt"
}
```

### `config/context.txt`

This file defines **who the bot is**.
It is appended to over time as memory proposals are accepted.

Keeping it external allows iteration without touching code.

---

## LLM Interaction Model

Bisbot always sends the LLM a **structured JSON payload** containing:

* Trigger reason (`mention`, `join`, `inactive`, etc.)
* Recent formatted conversation history

The LLM **must** reply in strict JSON:

```json
{
  "response": "string or null",
  "context": "string or null"
}
```

* `response = null` → bot stays silent
* `context` → optional memory proposal

Invalid JSON or LLM errors **never crash the bot**.

---

## Conversation Control

Several mechanisms prevent spam and awkward behavior:

* **MessageCounter** — joins only after N messages
* **MessageHistory** — rolling per-channel context
* **ConversationWatcher** — periodic evaluation of active chats
* **InactiveTimer** — reactivates dead channels carefully

Priority rules are enforced:

1. Mention / reply
2. Keyword
3. Join threshold
4. Conversation activity

---

## Slash command

From a test_channel, you can write the slash command /bisbot 'channel' 'prompt'.
This will make the bot respond in the specified channel, with the rules you specified in the prompt.
Example: /bisbot "general" "introduce yourself to the server"

---

## Testing Philosophy

The bot is designed to be testable **without Discord or OpenAI**.

* Discord API is mocked
* LLM is stubbed
* Timers and async behavior are verified

Tests validate:

* Trigger priority
* Silence conditions
* Activity resets
* Inactivity behavior
* Channel permissions
* Error resilience

---

## Running the Bot

```bash
export BISBOT_DISCORD_TOKEN=...
export BISBOT_API_KEY=...
python src/main.py
```

If `response_use_llm` is `false`, the bot will print payloads instead of calling OpenAI.

---

## Current State

* Core behavior implemented
* LLM interaction stable
* Conversation logic validated by tests
* Personality externalized
* Ready for real Discord deployment

---

## Possible Next Steps

* Make inactivity target channel configurable
* Persist memory proposals selectively
* Add per-server configuration
* Add logging / replay tools

---

## Final Notes

This project intentionally avoids overengineering.

It focuses on **behavior correctness**, **social realism**, and **clean boundaries** between:

* Discord logic
* Decision logic
* LLM interaction
