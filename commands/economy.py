import json
import os
import discord
import time
import logging
import asyncio
import aiofiles  # Asynchronous file handling
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions
from discord.utils import escape_markdown, escape_mentions

# FilePaths
ECONOMY_FILE = "T:/DiscordBot/data/economy.json"
LOG_FILE = "T:/DiscordBot/data/economy_log.txt"

# Threading lock for concurrency safety
economy_lock = asyncio.Lock()
command_lock = asyncio.Lock()  # Global lock for entire command execution

# A dictionary to hold active command states for users
active_commands = {}

# Ensure the JSON file exists and get data
async def ensure_economy_file():
    """Ensure that the economy file exists and is correctly formatted."""
    try:
        async with aiofiles.open(ECONOMY_FILE, "r") as file:
            content = await file.read()
            return json.loads(content)
    except (FileNotFoundError, json.JSONDecodeError):
        logging.warning("Economy file is missing or corrupted, creating a new one.")
        return {"users": {}}

# Save the economy data back to the file
async def save_economy_data(data):
    """Save the updated economy data back to the file."""
    try:
        async with aiofiles.open(ECONOMY_FILE, "w") as file:
            await file.write(json.dumps(data, indent=4))
            logging.debug(f"Economy data saved successfully: {data}")
    except Exception as e:
        logging.error(f"Error saving economy data: {e}")
        raise

# Log transactions to a file
def log_transaction(username, change, new_balance):
    with open(LOG_FILE, "a") as log_file:
        log_file.write(f"{time.ctime()} - {username} -> Change: {change}, New Balance: {new_balance}\n")

# Add a user to the economy if they don't already exist and update their balance
async def add_user_to_economy(username, amount=0):
    """Ensure user exists in economy and update their balance."""
    data = await ensure_economy_file()
    
    if username not in data["users"]:
        logging.debug(f"User {username} not found in economy data, adding...")
        data["users"][username] = {"balance": amount}
    else:
        logging.debug(f"User {username} already exists in economy data. Updating balance...")
        # Increase balance by the provided amount
        data["users"][username]["balance"] += amount

    await save_economy_data(data)

# Get the user's balance
async def get_balance(username):
    data = await ensure_economy_file()
    return data["users"].get(username, {}).get("balance", 0)

# Update the user's balance
async def update_balance(username, amount):
    async with economy_lock:  # Make sure to hold the lock when modifying the file
        data = await ensure_economy_file()
        current_balance = data["users"].get(username, {}).get("balance", 0)

        # Prevent negative balance
        new_balance = current_balance + amount
        if new_balance < 0:
            return False  # Cannot have a negative balance

        # Update the balance and save data
        if username in data["users"]:
            data["users"][username]["balance"] = new_balance
        else:
            data["users"][username] = {"balance": new_balance}
        await save_economy_data(data)

        # Log transaction
        log_transaction(username, amount, new_balance)
        return True

# Command: Balance
@commands.command()
async def balance(ctx):
    """Check your balance"""
    username = str(ctx.author)
    await add_user_to_economy(username)
    balance = await get_balance(username)
    await ctx.send(f"{username}, your balance is ${balance}.")

# Command: Give money to another user
@commands.command()
async def give(ctx, member: discord.Member, amount: int):
    """Give money to another user"""
    username = str(ctx.author)
    receiver = str(member)

    logging.debug(f"User {username} is executing the 'give' command.")

    # Ensure that the user isn't already in an active command process
    if active_commands.get(username, False):
        await ctx.send(f"{username}, please wait until your previous command finishes.")
        return

    # Mark the user as active to prevent simultaneous commands
    active_commands[username] = True

    logging.debug(f"Command locked for user {username}.")

    await add_user_to_economy(username)
    await add_user_to_economy(receiver)

    if amount <= 0:
        await ctx.send("You can't give negative or zero money!")
        logging.debug(f"Invalid amount specified by {username}.")
        del active_commands[username]
        return

    if await get_balance(username) < amount:
        await ctx.send("You don't have enough money to give!")
        logging.debug(f"{username} has insufficient funds.")
        del active_commands[username]
        return

    # Perform the transaction
    if await update_balance(username, -amount) and await update_balance(receiver, amount):
        await ctx.send(f"💸 {username} gave ${amount} to {receiver}!\n"
                       f"New balances:\n"
                       f"  {username}: ${await get_balance(username)}\n"
                       f"  {receiver}: ${await get_balance(receiver)}.")
        logging.debug(f"Transaction successful for {username} to {receiver}.")
    else:
        await ctx.send("Transaction failed due to an unexpected error.")
        logging.debug(f"Transaction failed for {username} to {receiver}.")

    # Mark the user as not active after the command is done
    logging.debug(f"Releasing command lock for user {username}.")
    del active_commands[username]

# Command: Spend money
@commands.command()
async def spend(ctx, amount: int):
    """Spend your money"""
    username = str(ctx.author)

    logging.debug(f"User {username} is executing the 'spend' command.")

    # Ensure that the user isn't already in an active command process
    if active_commands.get(username, False):
        await ctx.send(f"{username}, please wait until your previous command finishes.")
        return

    # Mark the user as active to prevent simultaneous commands
    active_commands[username] = True

    logging.debug(f"Command locked for user {username}.")

    await add_user_to_economy(username)

    if amount <= 0:
        await ctx.send("You can't spend negative or zero money!")
        logging.debug(f"Invalid amount specified by {username}.")
        del active_commands[username]
        return

    if await get_balance(username) < amount:
        await ctx.send("You don't have enough money to spend!")
        logging.debug(f"{username} has insufficient funds.")
        del active_commands[username]
        return

    # Perform spending
    if await update_balance(username, -amount):
        await ctx.send(f"🛍️ {username}, you spent ${amount}. Your new balance is ${await get_balance(username)}.")
        logging.debug(f"Transaction successful for {username} spending {amount}.")
    else:
        await ctx.send("An error occurred while processing your transaction.")
        logging.debug(f"Transaction failed for {username} spending {amount}.")

    # Mark the user as not active after the command is done
    logging.debug(f"Releasing command lock for user {username}.")
    del active_commands[username]

# Admin Command: Set balance for a user
@commands.command()
@has_permissions(administrator=True)
async def setbalance(ctx, member: discord.Member, amount: int):
    """Set a user's balance (admin-only)"""
    username = str(member)

    logging.debug(f"Admin {str(ctx.author)} is executing the 'setbalance' command for {username}.")

    # Ensure that the user isn't already in an active command process
    if active_commands.get(username, False):
        await ctx.send(f"{username}, please wait until your previous command finishes.")
        return

    # Mark the user as active to prevent simultaneous commands
    active_commands[username] = True

    logging.debug(f"Command locked for user {username}.")

    await add_user_to_economy(username)

    # Update and save the balance
    async with economy_lock:
        data = await ensure_economy_file()
        if username not in data["users"]:
            data["users"][username] = {"balance": 0}
        data["users"][username]["balance"] = amount
        await save_economy_data(data)

    await ctx.send(f"💰 {str(ctx.author)} has set {username}'s balance to ${amount}.")
    logging.debug(f"Admin {str(ctx.author)} set {username}'s balance to ${amount}.")

    # Mark the user as not active after the command is done
    logging.debug(f"Releasing command lock for user {username}.")
    del active_commands[username]

@setbalance.error
async def setbalance_error(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.send("You don't have permission to use this command.")

# !baltop command
@commands.command()
async def baltop(ctx, count: int = 10):
    """
    Display the top users with the highest balances.
    :param count: Number of top users to display (default: 10)
    """
    async with economy_lock:
        data = await ensure_economy_file()

    # Extract users and balances, sort by balance in descending order
    sorted_users = sorted(
        data["users"].items(),
        key=lambda user: user[1]["balance"],
        reverse=True
    )

    # Limit to the specified count
    top_users = sorted_users[:count]

    # Format the output
    if top_users:
        baltop_message = "**🏆 Balance Leaderboard 🏆**\n"
        for rank, (username, details) in enumerate(top_users, start=1):
            baltop_message += f"**{rank}.** {escape_markdown(username)}: ${details['balance']:,}\n"
    else:
        baltop_message = "No users found in the leaderboard."

    await ctx.send(baltop_message)

# Add commands to bot
async def setup(bot):
    bot.add_command(balance)
    bot.add_command(give)
    bot.add_command(spend)
    bot.add_command(setbalance)
    bot.add_command(baltop)