from dotenv import load_dotenv
import discord
import random
import re
from discord.ext import commands
from discord.ext.commands import CheckFailure, check
from discord.utils import escape_markdown, escape_mentions

from commands.shared import TARGET_CHANNEL_ID, ALLOWED_CHANNEL_RANDOM

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

    # Fetch the last 100 messages from the target channel
    messages = [msg async for msg in channel.history(limit=100)]

    if not messages:
        await ctx.send("No messages found in the channel.")
        return

    # Pick a random message
    random_message = random.choice(messages)
    content = random_message.content

    async def replace_mention(match):
        user_id = int(match.group(1))
        member = ctx.guild.get_member(user_id)  # Try to get from cache
        if not member:  # If not cached, try to fetch
            try:
                member = await ctx.guild.fetch_member(user_id)
            except discord.NotFound:
                return "[Unknown User]"
        return member.display_name

    # Use re.finditer to find all matches and then replace them
    mention_pattern = re.compile(r"<@!?(\d+)>")
    matches = list(mention_pattern.finditer(content))
    
    # Process each match and replace mentions with member names
    for match in matches:
        member_name = await replace_mention(match)
        content = content.replace(match.group(0), member_name)

    # Escape markdown to prevent formatting abuse
    content = escape_markdown(content)

    # Format the response
    quoted_message = f'**{random_message.author.display_name}** said: "{content}"'

    # Send the quoted message
    await ctx.send(quoted_message)

# Function to add the command to the bot
def setup(bot):
    bot.add_command(randomquote)