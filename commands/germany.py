import discord
from discord.ext import commands
import json
import os
from discord.ext.commands import CheckFailure, check
from commands.shared import ALLOWED_CHANNEL_GERMANY

# File to store the counter
counter_file = "T:/DiscordBot/data/germany.json"

# Replace these with the IDs of the two users allowed to use the commands
AUTHORIZED_USERS = [499359880335982593, 186305059011690496]  # Replace with actual user IDs

#in_allowed_channel
def in_allowed_channel(channel_id):
    async def predicate(ctx):
        if ctx.channel.id != channel_id:
            raise CheckFailure("You cannot use this command in this channel.")
        return True
    return check(predicate)

# Function to read the counter from the file
def read_counter():
    if not os.path.exists(counter_file):
        return 0
    try:
        with open(counter_file, "r") as file:
            return json.load(file).get("count", 0)
    except Exception as e:
        print(f"Error reading counter: {e}")
        return 0

# Function to write the counter to the file
def write_counter(value):
    try:
        with open(counter_file, "w") as file:
            json.dump({"count": value}, file)
    except Exception as e:
        print(f"Error writing counter: {e}")

# Command to increment the counter
@commands.command()
@in_allowed_channel(ALLOWED_CHANNEL_GERMANY)
async def germany(ctx):
    if ctx.author.id not in AUTHORIZED_USERS:
        await ctx.send("You are not authorized to use this command!")
        return

    current_count = read_counter()
    current_count += 1
    write_counter(current_count)
    await ctx.send(f"Congrats on getting fucked by having germany on your team! You've been fucked {current_count} times because of them!")

# Command to check the current counter value
@commands.command()
async def thanksgermany(ctx):
    if ctx.author.id not in AUTHORIZED_USERS:
        await ctx.send("You are not authorized to use this command!")
        return

    current_count = read_counter()
    await ctx.send(f"German Teammates have fucked you {current_count}!")

# Function to add the commands to the bot
def setup(bot):
    bot.add_command(germany)
    bot.add_command(thanksgermany)