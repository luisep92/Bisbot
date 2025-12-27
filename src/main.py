import os
from DiscordBot import DiscordBot
from GptWrapper import BisbalWrapper
from  Config import Config

TOKEN = os.getenv("BISBOT_DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError("BISBOT_DISCORD_TOKEN not set")

bot = DiscordBot(BisbalWrapper(Config().read()))
bot.run(TOKEN)
