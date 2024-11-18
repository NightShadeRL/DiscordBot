from discord.ext import commands

class PingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        """Ping command to check latency."""
        await ctx.send(f'My latency is at {self.bot.latency * 1000:.2f}ms')

async def setup(bot):
    await bot.add_cog(PingCog(bot))  # Add cog asynchronously