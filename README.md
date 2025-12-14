# Bisbot

Bisbot is a **meme Discord bot** that uses ChatGPT to role‑play *David Bisbal* inside the **Beat Saber España** Discord server.

The goal is simple: instead of behaving like a classic command‑based bot, Bisbot tries to behave like a regular user — sometimes talking, sometimes staying silent.

---

## What it does

* Uses ChatGPT to generate in‑character responses
* Decides **when to speak**, not just what to say
* Joins conversations after some activity
* Responds to mentions, replies and specific keywords
* Stays passive most of the time

No commands, no utilities — just presence.

---

## Why this structure

Even though this is a meme project, the code is intentionally structured:

* Bot logic is separated from Discord I/O
* State is tracked per channel (message count, history, inactivity)
* ChatGPT access is wrapped behind a small adapter
* The bot can be tested **without connecting to Discord**

This makes it easier to experiment, refactor and extend without breaking behavior.

---

## Project structure

```
src/
├── DiscordBot.py       # Core bot logic (when to respond)
├── Helpers.py          # Counters, history and inactivity timer
├── GptWrapper.py      # ChatGPT wrapper + context handling
├── Mocks.py           # Discord mocks for testing
└── Test_DiscordBot.py # Basic behavior test
```

---

## Testing

The project includes a basic async test that:

* Mocks Discord messages, users and channels
* Simulates the bot user (since `discord.Client.user` is read‑only)
* Verifies that the bot only responds when expected

The goal is not full coverage, but **behavior validation**.

---

## Current state

* Core Discord bot logic implemented
* Message‑based interaction rules working
* ChatGPT wrapper ready but not fully wired into the bot flow
* Testable without Discord

---

## Possible next steps

* Plug `GptWrapper` into real responses
* Improve interaction rules and thresholds
* Add long‑term memory or summarization
* Expand tests

---

## Notes

This is a small personal project built for fun, but treated with enough technical care to keep it clean, testable and easy to evolve.
