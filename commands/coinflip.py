import random
from discord.ext import commands

@commands.command()
async def coinflip(ctx):
    result = random.choices(
        ["Heads", "Tails", "It landed on it's edge! 😲"],
        weights=[49.5, 49.5, 1],
        k=1
    )[0]

    await ctx.send(f"The coin landed on **{result}**!")

def setup(bot):
    bot.add_command(coinflip)