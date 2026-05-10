# Bisbot

An LLM-driven Discord bot that listens, decides when to speak — and **often chooses not to**. Not a command-only bot: it watches conversation context, evaluates social cues (mentions, replies, keywords, join thresholds, ambient activity, prolonged silence), and stays quiet when speaking up wouldn't add anything. Silence is a first-class outcome of the LLM call, not a fallback.

The current personality is a humorous take on **David Bisbal** running in the *Beat Saber España* Discord server, but the architecture is generic — drop a different `context.txt` and a different `keywords` list and it's a different bot.

---

## What happened in the wild

Built and deployed for **December 28th 2025 — Spain's "Día de los Inocentes" (the equivalent of April Fools')** in the *Beat Saber España* community I admin. Designed as a one-day live experiment in a real server, not a long-running production system.

Notes from the day:

- **It started too talkative.** The first hour or two showed the LLM was over-eager, initiating even when the channel was already lively. I tuned it live: tightened the prompt rules in `config/context.txt` ("messages can be short", "don't force beat saber topics into every reply", "asking is better than guessing") and made the trigger thresholds harder to cross. The commit log on 2025-12-28 reads like it sounds: `Make bot respond less`, `Sharpen LLM behavior`.
- **People started talking to it directly.** Once a few users figured out it was an LLM, mentions and replies dominated over the ambient triggers. Worked as designed — the priority chain (mention > reply > keyword > join > activity > inactive) keeps direct interaction in front.
- **It steered toward Beat Saber too often.** Personality bias from the prompt — David Bisbal in a Beat Saber server, with seed context about specific community maps and `keywords: ["bisbal", "buleria", "camina", "mapa", ...]`. Funny in moderation, fatiguing past it. The fix is closer to prompt design than to code.
- **It worked reliably.** Caught people by surprise, generated real interaction, and ran the full day without crashing or burning the API budget.

The technical foundation held. The personality scope didn't. Both lessons.

---

## Core design principles

- 🧠 **Context-driven** — full recent conversation is sent to the LLM
- 🧍 **Acts like a human** — may choose *not* to reply
- 🔕 **Non-intrusive** — avoids interrupting or repeating itself
- 🧪 **Free to test** — Discord is mocked and the LLM is stubbed, so the unit suite costs **zero** in API calls
- 🧩 **Modular** — Discord, LLM, config, and helpers are cleanly separated

---

## What Bisbot actually does

Bisbot observes conversations and may respond when:

- It is **mentioned**
- Someone **replies** to one of its messages
- A **keyword** appears
- A conversation reaches a **message threshold** ("join")
- There is **ongoing activity** without intervention (periodic evaluation)
- The server has been **inactive** for a long time

The key idea is that **Bisbot decides whether to speak**, instead of replying mechanically.

---

## Project structure

```bash
.
├── config/
│   ├── config.json       # Runtime configuration
│   └── context.txt       # Initial personality & memory context
│
├── src/
│   ├── Config.py         # Config loading + defaults
│   ├── DiscordBot.py     # Discord client & event logic
│   ├── GptWrapper.py     # LLM wrapper + memory handling
│   ├── Helpers.py        # Counters, timers, history, handlers
│   └── main.py           # Entry point
│
├── tests/
│   ├── Mocks.py
│   ├── test_config.py
│   ├── test_behavior.py  # Manual test against the real LLM (gated)
│   └── test_discord_bot.py
│
├── pytest.ini
└── README.md
```

---

## Configuration

Configuration is split into **behavior** and **personality**, two text files.

### `config/config.json`

Controls how the bot behaves:

- `allowed_channels`: where the bot can speak
- `test_channels`: channels where slash commands are allowed
- `keywords`: words that trigger interaction
- `max_context_length`: memory limit
- `max_tokens_response`: LLM output size
- `response_use_llm`: disable LLM for dry runs
- `context_file`: external personality file

Example:

```json
{
  "allowed_channels": ["general"],
  "test_channels": ["muted-lobby"],
  "keywords": ["bisbal", "buleria", "camina"],
  "context_file": "context.txt"
}
```

### `config/context.txt`

This file defines **who the bot is**. It's appended to over time as memory proposals are accepted. Keeping it external lets you iterate on personality without touching code — the live tuning during the December 28 deployment was done entirely here.

---

## LLM interaction model

Bisbot always sends the LLM a **structured JSON payload** containing:

- Trigger reason (`mention`, `join`, `inactive`, etc.)
- Recent formatted conversation history

The LLM **must** reply in strict JSON:

```json
{
  "response": "string or null",
  "context": "string or null"
}
```

- `response = null` → bot stays silent
- `context` → optional memory proposal (appended to `context.txt` if accepted)

Invalid JSON or LLM errors **never crash the bot**.

---

## Conversation control

Several mechanisms prevent spam and awkward behavior:

- **MessageCounter** — joins only after N messages
- **MessageHistory** — rolling per-channel context
- **ConversationWatcher** — periodic evaluation of active chats (default 30s)
- **InactiveTimer** — tries to keep the conversation alive in a specified channel if the entire server has been silent (default 30 min)

Priority rules are enforced in `DiscordBot.on_message`:

1. Mention / reply
2. Keyword
3. Join threshold
4. Conversation activity

---

## Slash command

From a `test_channel`, you can write `/bisbot 'channel' 'prompt'`. This makes the bot respond in the specified channel with the rules you provide in the prompt.

Example: `/bisbot "general" "introduce yourself to the server"`

---

## Testing philosophy

The bot is designed to be testable **without Discord or OpenAI**:

- **Discord API is mocked.** `tests/Mocks.py` provides fake `discord.Client`, channel, message, and author objects, plus a `MockMessageHandler` that records what would have been sent.
- **The LLM is stubbed.** Tests inject a `SimpleNamespace`-based fake whose `get_response` returns a canned `message`/`memory_proposal`. The default pytest run makes **zero** real API calls.
- **One behaviour test is gated as manual.** `tests/test_behavior.py` opens with `pytest.skip("manual test", allow_module_level=True)` so it's never collected by accident — it's there for opt-in validation against the real LLM when you're iterating on prompt changes, and it's the only place real API calls happen.

Tests validate:

- Trigger priority (mention > reply > keyword > join)
- Silence conditions (don't double-reply, don't echo bot messages)
- Activity resets (counters and timers under real timing)
- Inactivity behavior (long-silence path)
- Channel permissions
- Error resilience (invalid JSON from the LLM never crashes the bot)

---

## Running the bot

```bash
export BISBOT_DISCORD_TOKEN=...
export BISBOT_API_KEY=...
python src/main.py
```

If `response_use_llm` is `false`, the bot prints payloads instead of calling OpenAI.

---

## Status

The bot ran its day. The deployment validated the design (silence as a valid action, trigger priority, JSON-only LLM contract, prompt-driven personality) and exposed the parts that lean on the prompt rather than the code (over-talkativeness, topic bias). Now it sits.

Honest follow-ups, not committed:

- **Per-server configuration.** Right now it's one Discord token, one config, one personality. Multi-server would need scoping per guild.
- **Selective memory persistence.** The LLM can propose new context lines via the response JSON; they get appended to `context.txt` if accepted, but there's no review queue or rollback.
- **Logging / replay.** No instrumentation of the trigger decisions over time — would help future prompt tuning.
- **Configurable inactivity target channel.** Currently fixed.

---

## Final notes

This project intentionally avoids overengineering. It focuses on **behavior correctness**, **social realism**, and **clean boundaries** between Discord logic, decision logic, and LLM interaction.
