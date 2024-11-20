import json
import os
import discord
import random
import time
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions

# Path to the JSON file
ECONOMY_FILE = "T:/DiscordBot/data/economy.json"

# Ensure the JSON file exists
def ensure_economy_file():
    try:
        with open(ECONOMY_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        with open(ECONOMY_FILE, "w") as file:
            json.dump({"users": {}}, file)
        return {"users": {}}

# Save changes to the JSON file
def save_economy_data(data):
    with open(ECONOMY_FILE, "w") as file:
        json.dump(data, file, indent=4)

# Add a user to the economy file if they don't already exist
def add_user_to_economy(username):
    data = ensure_economy_file()
    if username not in data["users"]:
        data["users"][username] = {"balance": 0}
        save_economy_data(data)

# Get user balance
def get_balance(username):
    data = ensure_economy_file()
    return data["users"].get(username, {}).get("balance", 0)

# Update user balance
def update_balance(username, amount):
    data = ensure_economy_file()
    if username in data["users"]:
        data["users"][username]["balance"] += amount
    else:
        data["users"][username] = {"balance": amount}
    save_economy_data(data)

# Bot commands
@commands.command()
async def balance(ctx):
    """Check your balance"""
    username = str(ctx.author)
    add_user_to_economy(username)
    balance = get_balance(username)
    await ctx.send(f"{username}, your balance is ${balance}.")

@commands.command()
async def give(ctx, member: discord.Member, amount: int):
    """Give money to another user"""
    giver = str(ctx.author)
    receiver = str(member)
    
    add_user_to_economy(giver)
    add_user_to_economy(receiver)

    if amount <= 0:
        await ctx.send("You can't give negative or zero money!")
        return
    
    if get_balance(giver) < amount:
        await ctx.send("You don't have enough money to give!")
        return
    
    update_balance(giver, -amount)
    update_balance(receiver, amount)
    await ctx.send(f"💸 {giver} gave ${amount} to {receiver}! New balances: {giver}: ${get_balance(giver)}, {receiver}: ${get_balance(receiver)}.")

@commands.command()
async def spend(ctx, amount: int):
    """Spend your money"""
    username = str(ctx.author)
    add_user_to_economy(username)

    if amount <= 0:
        await ctx.send("You can't spend negative or zero money!")
        return
    
    if get_balance(username) < amount:
        await ctx.send("You don't have enough money to spend!")
        return
    
    update_balance(username, -amount)
    await ctx.send(f"🛍️ {username}, you spent ${amount}. Your new balance is ${get_balance(username)}.")

@commands.command()
@has_permissions(administrator=True)
async def setbalance(ctx, member: discord.Member, amount: int):
    """Set a user's balance (admin-only)"""
    username = str(member)
    add_user_to_economy(username)

    data = ensure_economy_file()
    data["users"][username]["balance"] = amount
    save_economy_data(data)

    await ctx.send(f"Admin has set {username}'s balance to ${amount}.")

@setbalance.error
async def setbalance_error(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.send("You don't have permission to use this command.")

# Add commands to the bot
def setup(bot):
    bot.add_command(balance)
    bot.add_command(give)
    bot.add_command(spend)
    bot.add_command(setbalance)