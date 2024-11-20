import random
import time
import json
import os
import aiofiles  # Ensure this import is included for async file handling
from discord.ext import commands
from commands.economy import get_balance, update_balance  # Ensure these are awaited

# I will never have to look at this file (tm)
COOLDOWN_FILE = "T:/DiscordBot/data/work_cooldowns.json"

# Function to read cooldowns from a file
async def read_cooldowns():
    if os.path.exists(COOLDOWN_FILE):
        async with aiofiles.open(COOLDOWN_FILE, "r") as file:
            content = await file.read()  # Read file asynchronously
            return json.loads(content) if content else {}  # Parse JSON string
    return {}

# Function to write cooldowns to a file
async def write_cooldowns(cooldowns):
    async with aiofiles.open(COOLDOWN_FILE, "w") as file:
        await file.write(json.dumps(cooldowns, indent=4))  # Write JSON data

# Command to work and earn money
@commands.command()
async def work(ctx):
    user_id = str(ctx.author.id)
    username = ctx.author.name
    cooldowns = await read_cooldowns()  # Ensure this is awaited

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

    # Update user's balance (ensure it's awaited)
    current_balance = await get_balance(username)  # Await get_balance
    new_balance = current_balance + earned_money
    success = await update_balance(username, earned_money)  # Await update_balance

    if not success:
        await ctx.send("There was an error while updating your balance!")
        return

    # Save the current time to the cooldowns (ensure it's awaited)
    cooldowns[user_id] = current_time
    await write_cooldowns(cooldowns)  # Await write_cooldowns

    # Respond to the user
    await ctx.send(f"💼 You worked hard and earned ${earned_money}! Your new balance is ${new_balance}.")

# Setup function to add the command to the bot
async def setup(bot):
    bot.add_command(work)
