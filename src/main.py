import os
from DiscordBot import DiscordBot

TOKEN = os.getenv("BISBOT_DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError("BISBOT_DISCORD_TOKEN not set")

bot = DiscordBot()
bot.run(TOKEN)