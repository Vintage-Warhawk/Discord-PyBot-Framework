"""
File: tasks.py
Maintainer: Vintage Warhawk
Last Edit: 2025-11-17

Description:
This file defines task classes for the Discord bot framework.
Tasks are scheduled operations that run on a defined interval (hourly, daily, test).
Each task class must implement an async `run(client)` method, where `client` is the
Discord client instance. Tasks can access guild-specific configuration to send messages
to designated channels.
"""

from tasks_manager import TaskManager
from config import GetConfig

# Create a TaskManager instance to register tasks
manager = TaskManager()

# -----------------------------
# Example Task: Hourly
# -----------------------------
class HourlyTask:
    """
    Task that runs every hour.
    Sends a message to the configured home channel for each guild.
    """

    async def run(self, client):
        """
        Executes the hourly task for all guilds the bot is in.

        Args:
            client (discord.Client): The bot instance, used to access guilds and channels.
        """
        for guild in client.guilds:
            home_channel_id = GetConfig("home_channels", guild_id=guild.id).value()
            if home_channel_id:
                channel = guild.get_channel(int(home_channel_id))
                if channel:
                    await channel.send("Hourly task executed!")

# Register the hourly task
manager.register_task("hourly", HourlyTask())

# -----------------------------
# Example Task: Daily
# -----------------------------
class DailyTask:
    """
    Task that runs daily (e.g., at noon).
    Sends a message to the configured home channel for each guild.
    """

    async def run(self, client):
        """
        Executes the daily task for all guilds the bot is in.

        Args:
            client (discord.Client): The bot instance, used to access guilds and channels.
        """
        for guild in client.guilds:
            home_channel_id = GetConfig("home_channels", guild_id=guild.id).value()
            if home_channel_id:
                channel = guild.get_channel(int(home_channel_id))
                if channel:
                    await channel.send("Daily task executed!")

# Register the daily task
manager.register_task("daily", DailyTask())

# -----------------------------
# Example Task: Test
# -----------------------------
# Uncomment to enable a test task that runs every 10 seconds
# class TestTask:
#     """
#     Task that runs every 10 seconds for testing purposes.
#     """
#     async def run(self, client):
#         for guild in client.guilds:
#             home_channel_id = GetConfig("home_channels", guild_id=guild.id).value()
#             if home_channel_id:
#                 channel = guild.get_channel(int(home_channel_id))
#                 if channel:
#                     await channel.send("Test task executed!")
#
# manager.register_task("test", TestTask())
