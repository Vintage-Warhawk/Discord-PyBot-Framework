"""
File: tasks.py
Maintainer: Vintage Warhawk
Last Edit: 2025-11-21
"""

from library.task_manager import TaskManager
from library.config_manager import GetConfig

# Create a TaskManager instance to register tasks
manager = TaskManager()

# -----------------------------
# Example Task: Minutely
# -----------------------------
class MinutelyTask:
	"""
	Task that runs every minute.
	Sends a message to the configured home channel for each guild.
	"""

	async def run(self, client):
		"""
		Executes the minutely task for all guilds the bot is in.

		Args:
			client (discord.Client): The bot instance, used to access guilds and channels.
		"""
		for guild in client.guilds:
			home_channel_id = GetConfig("home_channels", guild_id=guild.id).value()
			if home_channel_id:
				channel = guild.get_channel(int(home_channel_id))
				if channel:
					await channel.send("Minutely task executed!")

# Register the hourly task
manager.register_task("minutely", "Example Task", MinutelyTask())

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
manager.register_task("hourly", "Example Task", HourlyTask())

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

# Register the noon task
manager.register_task("noon", "Example Task", DailyTask())

# -----------------------------
# Example Task: Test
# -----------------------------
# Uncomment to enable a test task that runs every 10 seconds
#class TestTask:
#    """
#    Task that runs every 10 seconds for testing purposes.
#    """
#    async def run(self, client):
#        for guild in client.guilds:
#            home_channel_id = GetConfig("home_channels", guild_id=guild.id).value()
#            if home_channel_id:
#                channel = guild.get_channel(int(home_channel_id))
#                if channel:
#                    await channel.send("Test task executed!")
#
#manager.register_task("test", "Example Task", TestTask())
