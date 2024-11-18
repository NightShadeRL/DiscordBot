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
import audioop
import warnings
import tracemalloc

# from shared.py

from commands.shared import ALLOWED_CHANNEL_ROLL

def in_allowed_channel(channel_id):
    async def predicate(ctx):
        if ctx.channel.id != channel_id:
            raise CheckFailure("You cannot use this command in this channel.")
        return True
    return check(predicate)

@commands.command()
@in_allowed_channel(ALLOWED_CHANNEL_ROLL)
async def roll(ctx, dice: str = "1d6"):
    """
    Rolls dice with the format NdS where:
    N = number of dice
    S = number of sides of the dice
    Default is 1d6 (1 six-sided dice).
    Max 5 dice at a time.
    """
    # Regular expression to match the dice format (e.g., 3d6, 2d20)
    dice_pattern = r'(\d+)d(\d+)'
    match = re.match(dice_pattern, dice)

    if not match:
        await ctx.send("Invalid dice format! Please use NdS (e.g., 3d6 for 3 six-sided dice).")
        return
    
    # Extract the number of dice and sides
    num_dice = int(match.group(1))
    sides = int(match.group(2))

    # Limit the number of dice to 5
    if num_dice > 5:
        await ctx.send("You can only roll a maximum of 5 dice at a time!")
        return

    if num_dice < 1 or sides < 2:
        await ctx.send("Please specify a valid number of dice and sides (at least 1 die and 2 sides).")
        return

    # Roll the dice
    rolls = [random.randint(1, sides) for _ in range(num_dice)]

    # Return the results
    total = sum(rolls)
    roll_results = ', '.join(map(str, rolls))
    await ctx.send(f"{ctx.author.mention} rolled {num_dice}d{sides}:\n{roll_results}\nTotal: **{total}**")

# Function to add the command to the bot
def setup(bot):
    bot.add_command(roll)
