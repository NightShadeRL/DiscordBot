import discord
import os
from dotenv import load_dotenv
import asyncio
import time
import random
import re
from discord.ext import commands
from discord.ext.commands import CheckFailure, check
from discord.utils import escape_markdown
from commands.economy import add_user_to_economy, update_balance, get_balance
import audioop
import warnings
import tracemalloc
# from shared.py
from commands.shared import ALLOWED_CHANNEL_SLOTS


def in_allowed_channel(channel_id):
    async def predicate(ctx):
        if ctx.channel.id != channel_id:
            raise CheckFailure("You cannot use this command in this channel.")
        return True
    return check(predicate)

# Slot machine symbols
symbols = ["🍒", "🔔", "7️⃣"]

# Dictionary to track the time of the last command usage
user_last_used = {}

# Set the soft slowmode time (in seconds)
SLOWMODE_TIME = 3  # users need to wait 3 seconds between command usages

file_path = r"T:/DiscordBot/data/jackpot_data.txt"

def read_jackpot_data():
    try:
        with open(file_path, "r") as file:
            data = {}
            for line in file:
                username, count = line.strip().split(":")
                data[username] = int(count)
            return data
    except FileNotFoundError:
        return {}
    except Exception as e:
        print(f"Error reading jackpot data: {e}")
        return {}

def write_jackpot_data(data):
    with open(file_path, "w") as file:
        for username, count in data.items():
            file.write(f"{username}:{count}\n")

# Command to spin the slot machine
@commands.command()
@in_allowed_channel(ALLOWED_CHANNEL_SLOTS)
async def slots(ctx):

    #Economy Integration
    username = str(ctx.author)
    add_user_to_economy(username) #Ensure user is in economy.json

    # Can bot func be used in specified channel

    if not in_allowed_channel(ctx):
        await ctx.send("This command cannot be used in this chat!")
        return

    if random.randint(1, 1000000) == 127569:
        spin_result = ["🛡️", "🛡️", "🛡️"]

        username = str(ctx.author)
        jackpot_data = read_jackpot_data()

        if username in jackpot_data:
            jackpot_data[username] += 1
        else:
            jackpot_data[username] = 1

        reward = 10000
        update_balance(username, reward)

        write_jackpot_data(jackpot_data)

        await ctx.send(f"🛡️ | 🛡️ | 🛡️ \nYou hit the 🛡️HIDDEN JACKPOT!🛡️ You've hit the 🛡️HIDDEN JACKPOT🛡️ {jackpot_data[username]} times! \nYou earned **${reward}** for hitting the hidden jackpot! Your new balance is ${get_balance(username)}.")
        return
    
    if random.randint(1, 500000) == 69420:
        spin_result = ["❌", "❌", "❌"]

        reward = 1
        update_balance(username, reward)

        surprise_message = ""
        await ctx.send(f"❌ | ❌ | ❌ \n❌Aww dang it!❌ How unlucky! **You now have to play 1 game of [Forbidden Game] (This only affects you)**! \nYou earned **${reward}** for hitting the hidden jackpot! Your new balance is ${get_balance(username)}.")
        return

    # Randomly select three symbols
    spin_result = [random.choice(symbols) for _ in range(3)]
    
    # Format the result as a slot machine string
    result_str = " | ".join(spin_result)

    # Check if all three symbols are cherries
    if spin_result == ["🍒", "🍒", "🍒"]:
        reward = 20
        update_balance(username, reward)
        await ctx.send(f"{result_str}\n🎉 **JACKPOT!** 🎉 You got all cherries! Here's a surprise: **You are a cherry! 🍒** Keep being sweet and awesome! 😄 \nYou earned **${reward}** for hitting the jackpot! Your new balance is ${get_balance(username)}.")
    elif spin_result == ["7️⃣", "7️⃣", "7️⃣"]:
        reward = 45
        update_balance(username, reward)
        await ctx.send(f"{result_str}\n🎰 **SEVEN'S A WINNER!** 🎰 You got all sevens! Here's your reward: **Lucky you! 🍀** \nYou earned **${reward}** for hitting the jackpot! Your new balance is ${get_balance(username)}.")
    elif spin_result == ["🔔", "🔔", "🔔"]:
        reward = 20
        update_balance(username, reward)
        await ctx.send(f"{result_str}\n🔔 **BELL BINGO!** 🔔 You got all bells! Here's a reward: **You’ve rung the jackpot bell! 🛎️** \nYou earned **${reward}** for hitting the jackpot! Your new balance is ${get_balance(username)}.")
    else:
        # Regular message when not a jackpot
        await ctx.send(f"{result_str}\nBetter luck next time! Try again! 🍀")


# Function to add the command to the bot
def setup(bot):
    bot.add_command(slots)