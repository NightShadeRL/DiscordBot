import json
from discord.ext import commands
from discord.utils import escape_markdown

# File path for storing points data
POINTS_FILE = "T:/DiscordBot/data/points.json"

# Function to load points data from file
def load_points_data():
    try:
        with open(POINTS_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        print("Error decoding JSON file. Starting with an empty points database.")
        return {}

# Function to save points data to file
def save_points_data(data):
    with open(POINTS_FILE, "w") as file:
        json.dump(data, file, indent=4)

# Command to add points to a user
@commands.command()
async def addpoints(ctx, user: commands.MemberConverter, points: int):
    """
    Adds points to a mentioned user.
    Usage: !addpoints @user <points>
    """
    # Check if the user has admin permissions
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("You do not have permission to use this command. Only admins can add points.")
        return

    if points <= 0:
        await ctx.send("Please specify a positive number of points.")
        return

    # Load the points data
    points_data = load_points_data()

    # Update the user's points (using their username instead of user ID)
    username = user.name
    if username not in points_data:
        points_data[username] = {"name": username, "points": 0}

    points_data[username]["points"] += points
    save_points_data(points_data)

    await ctx.send(f"Added {points} points to {escape_markdown(user.display_name)}! They now have {points_data[username]['points']} points.")

# Command to check a user's points
@commands.command()
async def checkpoints(ctx, user: commands.MemberConverter = None):
    """
    Checks points for a mentioned user. If no user is mentioned, it shows the command issuer's points.
    Usage: !checkpoints [@user]
    """
    # Use command issuer if no user is specified
    if user is None:
        user = ctx.author

    # Load the points data
    points_data = load_points_data()

    username = user.name
    if username in points_data:
        points = points_data[username]["points"]
        await ctx.send(f"{escape_markdown(user.display_name)} has {points} points.")
    else:
        await ctx.send(f"{escape_markdown(user.display_name)} has no points.")

# Take away (subtract | minus) points for a user
@commands.command()
async def minuspoints(ctx, user: commands.MemberConverter, points: int):
    """
    Subtracts points from a mentioned user.
    Usage: !subtractpoints @user <points>
    """
    # Check if the user has admin permissions
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("You do not have permission to use this command. Only admins can subtract points.")
        return

    if points <= 0:
        await ctx.send("Please specify a positive number of points to subtract.")
        return

    # Load the points data
    points_data = load_points_data()

    username = user.name
    if username not in points_data:
        points_data[username] = {"name": username, "points": 0}

    # Subtract points but ensure points don't go below zero
    new_points = points_data[username]["points"] - points
    points_data[username]["points"] = max(new_points, 0)  # Prevent negative points
    save_points_data(points_data)

    await ctx.send(f"Subtracted {points} points from {escape_markdown(user.display_name)}! They now have {points_data[username]['points']} points.")


# Command to reset points for a user
@commands.command()
async def resetpoints(ctx, user: commands.MemberConverter):
    """
    Resets points for a mentioned user.
    Usage: !resetpoints @user
    """
    # Check if the user has admin permissions
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("You do not have permission to use this command. Only admins can reset points.")
        return

    # Load the points data
    points_data = load_points_data()

    username = user.name
    if username in points_data:
        points_data[username]["points"] = 0
        save_points_data(points_data)
        await ctx.send(f"Points for {escape_markdown(user.display_name)} have been reset.")
    else:
        await ctx.send(f"{escape_markdown(user.display_name)} has no points to reset.")

# Function to add the commands to the bot
def setup(bot):
    bot.add_command(addpoints)
    bot.add_command(checkpoints)
    bot.add_command(resetpoints)
    bot.add_command(minuspoints)