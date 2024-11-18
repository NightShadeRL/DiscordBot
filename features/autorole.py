import discord
from discord.ext import commands
from features.shared import AUTO_ROLE_ID

class AutoRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Automatically assign a role when a user joins."""
        role = member.guild.get_role(AUTO_ROLE_ID)
        if role:
            await member.add_roles(role)
            print(f"Assigned {role.name} to {member.name}")
        else:
            print("Role not found.")

async def setup(bot):
    await bot.add_cog(AutoRole(bot))  # Add cog asynchronously