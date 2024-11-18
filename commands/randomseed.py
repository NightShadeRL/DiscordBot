import random
import string
from discord.ext import commands

# Command to generate a random map seed
@commands.command()
async def randomseed(ctx, seed_type="alphanumeric", seed_length=16):
    """
    Generates a random map seed.
    Usage:
        !randomseed alphanumeric <length> - Generates a seed with letters and numbers
        !randomseed numeric <length> - Generates a seed with only numbers
    Default is alphanumeric with a length of 16 characters.
    """

    # Validate seed_length input (ensure it's a positive integer)
    if seed_length < 1:
        await ctx.send("Please provide a valid length greater than 0.")
        return
    if seed_length > 32:
        await ctx.send("The maximum seed length is 32 characters.")
        return
    
    if seed_type == "numeric":
        # Generate a random numeric seed
        seed = ''.join(random.choices(string.digits, k=seed_length))
    elif seed_type == "alphanumeric":
        # Generate a random alphanumeric seed (letters + digits)
        seed = ''.join(random.choices(string.ascii_letters + string.digits, k=seed_length))
    else:
        await ctx.send("Invalid seed type! Please use 'alphanumeric' or 'numeric'.")
        return

    # Send the generated seed back to the user
    await ctx.send(f"Your random map seed is: `{seed}`")

# Function to add the command to the bot
def setup(bot):
    bot.add_command(randomseed)