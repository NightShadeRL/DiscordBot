import random
import time
import json
import os
from discord.ext import commands
from commands.economy import get_balance, update_balance

# I will never have to look at this file (tm)
COOLDOWN_FILE = "T:/DiscordBot/data/work_cooldowns.json"

# Function to read cooldowns from a file
def read_cooldowns():
    if os.path.exists(COOLDOWN_FILE):
        with open(COOLDOWN_FILE, "r") as file:
            return json.load(file)
    return {}

# Function to write cooldowns to a file
def write_cooldowns(cooldowns):
    with open(COOLDOWN_FILE, "w") as file:
        json.dump(cooldowns, file)

# Command to work and earn money
@commands.command()
async def work(ctx):
    user_id = str(ctx.author.id)
    username = ctx.author.name
    cooldowns = read_cooldowns()

    # Check for cooldown
    cooldown_time = 1800  # in seconds
    current_time = int(time.time())
    last_work_time = cooldowns.get(user_id, 0)

    if current_time - last_work_time < cooldown_time:
        remaining_time = cooldown_time - (current_time - last_work_time)
        minutes, seconds = divmod(remaining_time, 60)
        await ctx.send(f"⏳ You need to wait {minutes}m {seconds}s before working again!")
        return

    # Generate a random amount of money earned
    earned_money = random.randint(50, 200)  # Earn between $50 and $200

    # Update user's balance
    current_balance = get_balance(username)
    new_balance = current_balance + earned_money
    update_balance(username, new_balance)

    # Save the current time to the cooldowns
    cooldowns[user_id] = current_time
    write_cooldowns(cooldowns)

    # Respond to the user
    await ctx.send(f"💼 You worked hard and earned ${earned_money}! Your new balance is ${new_balance}.")

# Setup function to add the command to the bot
def setup(bot):
    bot.add_command(work)