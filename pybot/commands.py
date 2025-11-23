"""
File: commands.py
Maintainer: Vintage Warhawk
Last Edit: 2025-11-23

Description:
This file contains all custom command classes for the Discord bot framework.
Commands are registered with a central HookManager instance. Each command
class must implement an asynchronous `run` method that handles the logic
when the command is invoked.
"""

import datetime

from library.command_manager import CommandManager
from library.config_manager import SetConfig
from library.config_manager import GetConfig
from library.response_manager import ResponseManager

# Create a CommandManager and ReponseManager instance for registering commands
manager = CommandManager()
response = ResponseManager()
response.set_command_manager(manager)

# -----------------------------
# Example Command: !test
# -----------------------------
class TestCommand:
	"""
	Example command demonstrating argument handling.
	Usage: !test arg1 arg2 ...
	"""
	async def run(self, message, args):
		"""
		Runs when the !test command is invoked.
		- args[0] is the command itself.
		- args[1:] contains additional parameters provided by the user.
		"""
		if len(args) < 2:
			await message.channel.send("No arguments provided!")
			return
		await message.channel.send(f"{message.author.name} ran !test with args: {args[1:]}")

# Register the !test command with the manager
manager.register_command("!test", TestCommand())

# -----------------------------
# Example Command: !name
# -----------------------------
class NameCommand:
	"""
	Command that echoes what the user typed.
	Usage: !name <message>
	"""
	async def run(self, message, args):
		"""
		Sends a message to the channel showing the user's name and the message.
		"""
		await message.channel.send(f"{message.author.name} said: {' '.join(args[1:])}")

# Register the !name command
manager.register_command("!name", NameCommand())

# -----------------------------
# Example Command: !home
# -----------------------------
class HomeCommand:
	"""
	Command for admins to set the 'home' channel for the server.
	Usage: !home
	"""
	async def run(self, message, args):
		"""
		Saves the current channel as the home channel in the persistent config.
		Only users with administrator permissions can run this command.
		"""
		if not message.author.guild_permissions.administrator:
			await message.channel.send("Only admins can set the home channel.")
			return

		# Store the channel ID for this guild in the config system
		SetConfig("home_channels", str(message.channel.id), guild_id=message.guild.id)
		print(f"\033[33m[Config]\033[0m new home directory set: \033[33m{message.channel.name} ({message.channel.id})\033[0m")
		await message.channel.send("This channel is now set as the home channel for this server!")

# Register the !home command
manager.register_command("!home", HomeCommand())

# -----------------------------
# Example Command: !announcement
# -----------------------------
class AccouncementCommand:
	async def run(self, message, args):
		if not message.author.guild_permissions.administrator:
			await message.channel.send("Only admins can set the home channel.")
			return

		home_channel_id = GetConfig("home_channels", guild_id=message.guild.id).value()

		if home_channel_id:
			channel = message.guild.get_channel(int(home_channel_id))
			if channel:
				await channel.send(message.content.replace("!announcement", "", 1))
			else:
				await message.channel.send("Home channel could not be found.")
		else:
			await message.channel.send("No home channel set. use !home to set the current channel as home.")

# Register the !home command
manager.register_command("!announcement", AccouncementCommand())

# -----------------------------
# Example Command: !response
# -----------------------------
class ResponseCommand:

	async def run(self, message, args):

		# Adds response to the manager to await a user response.
		timeout_at = datetime.datetime.utcnow() + datetime.timedelta(seconds=30)

		response.await_message(
			channel_id=message.channel.id,
			user_id=message.author.id,
			timeout_message="Timed out.",
			timeout_datetime=timeout_at,
			command=args[0]
		)

		await message.channel.send("Waiting for your response...")

	async def on_response(self, client, message):
		await message.channel.send(f"{message.author.name} responded: {message.content}")

# Register the !response command
manager.register_command("!response", ResponseCommand())

# -----------------------------
# Example Command: !reaction
# -----------------------------
class ReactionCommand:

	async def run(self, message, args):

		# Adds response to the manager to await a user reaction.
		timeout_at = datetime.datetime.utcnow() + datetime.timedelta(seconds=30)

		confirm = await message.channel.send("React to this message!")

		response.await_reaction(
			message_id=confirm.id,
			channel_id=message.channel.id,
			user_id=message.author.id,
			timeout_message="Timed out.",
			timeout_datetime=timeout_at,
			command=args[0]
		)

	async def on_reaction(self, client, reaction, user):
		await reaction.message.channel.send(f"{user.name} reacted: {reaction.emoji}")

# Register the !response command
manager.register_command("!reaction", ReactionCommand())

# -----------------------------
# Example Command: !react
# -----------------------------
class ReactCommand:

	async def run(self, message, args):

		# Adds response to the manager to await a user reaction.
		timeout_at = datetime.datetime.utcnow() + datetime.timedelta(days=36500)

		confirm = await message.channel.send("React to this message!")

		response.static_reaction(
			message_id=confirm.id,
			guild_id=message.guild.id,
			channel_id=message.channel.id,
			user_id=0,
			timeout_message="Timed out.",
			timeout_datetime=timeout_at,
			command=args[0]
		)

	async def on_reaction(self, client, reaction, user):
		await reaction.message.channel.send(f"{user.name} reacted: {reaction.emoji}")

# Register the !response command
manager.register_command("!react", ReactCommand())