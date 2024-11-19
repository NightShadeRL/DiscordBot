import discord
import os
import time
from dotenv import load_dotenv
from discord.ext import commands
from discord.ext.commands import CheckFailure, check
from discord.utils import escape_markdown

# Configures intents to the bot.
# Should be allowed to grab usernames from <userid>
intents = discord.Intents.default()
intents.members = True # Enable access to Member Username/Nickname
intents.message_content = True # Enables access to message content (Required for reading messages)

# Create a bot instance (one bot for both functionalities)
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, case_insensitive=True)

#bot token
load_dotenv(dotenv_path="T:/DiscordBot/bot_token.env")
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("No bot token found in the .env file.")

# From commands
from commands.quote import setup as setup_quotes
from commands.slots import setup as setup_slots
from commands.dice import setup as setup_roll
from commands.points import setup as setup_points
from commands.randomseed import setup as setup_seed
from commands.coinflip import setup as setup_coin
from commands.germany import setup as setup_germany
from commands.economy import setup as setup_economy
from commands.work import setup as setup_work

# From features
async def load_extensions():
    try:
        await bot.load_extension('features.ping')
        time.sleep(1)
        print("Ping feature loaded.")
        time.sleep(1)
    except Exception as e:
        print(f"Failed to load ping: {e}")
    try:
        await bot.load_extension('features.autorole')
        time.sleep(1)
        print("autorole feature loaded.")
        time.sleep(1)
    except Exception as e:
        print(f"Failed to load autorole: {e}")

# Import commands
setup_quotes(bot)
setup_slots(bot)
setup_roll(bot)
setup_points(bot)
setup_seed(bot)
setup_coin(bot)
setup_germany(bot)
setup_economy(bot)
setup_work(bot)

# Event to signal when the bot is ready
@bot.event
async def on_ready():
    await load_extensions()
    print(f"Bot is ready as {bot.user}")
# Run the bot with your token
if __name__ == "__main__":
    import asyncio

    async def main():
        await bot.start(BOT_TOKEN)

    asyncio.run(main())