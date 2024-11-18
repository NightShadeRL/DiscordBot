import discord
import os
from dotenv import load_dotenv
import random
import re
from discord.ext import commands
from discord.ext.commands import CheckFailure, check
from discord.utils import escape_markdown, escape_mentions

from commands.shared import TARGET_CHANNEL_ID
from commands.shared import ALLOWED_CHANNEL_RANDOM

# Check channelID if allowed
def in_allowed_channel(channel_id):
    async def predicate(ctx):
        if ctx.channel.id != channel_id:
            raise CheckFailure("You cannot use this command in this channel.")
        return True
    return check(predicate)

# The command actual shit
@commands.command()
@in_allowed_channel(ALLOWED_CHANNEL_RANDOM)
async def randomquote(ctx):
    # Fetch the target channel object
    channel = ctx.bot.get_channel(TARGET_CHANNEL_ID)
    
    if not channel:
        await ctx.send("Couldn't find the specified channel.")
        return

    # Fetch the last 100 messages from that channel
    messages = [msg async for msg in channel.history(limit=100) if msg.content]

    if not messages:
        await ctx.send("No messages found in the channel.")
        return

    # Choose a random message
    random_message = random.choice(messages)

    # Replace user mentions with their usernames
    content = random_message.content
    content = re.sub(r"<@!?(\d+)>", lambda m: random_message.guild.get_member(int(m.group(1))).display_name, content)

    # Format the response with the user's name and the modified content
    quoted_message = f'**{random_message.author.display_name}** said: "{content}"'

    # Send the quoted message
    await ctx.send(quoted_message)

# Function to add the command to the bot
def setup(bot):
    bot.add_command(randomquote)