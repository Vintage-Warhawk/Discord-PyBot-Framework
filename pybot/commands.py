"""
File: commands.py
Maintainer: Vintage Warhawk
Last Edit: 2025-11-24

Description:
This file contains all custom command classes for the Discord bot framework.
Commands are registered with a central HookManager instance. Each command
class must implement an asynchronous `run` method that handles the logic
when the command is invoked.
"""

import io
import datetime
import discord
from discord import Embed

from library.command_manager import CommandManager
from library.config_manager import SetConfig
from library.config_manager import GetConfig
from library.response_manager import ResponseManager

# Create a CommandManager and ReponseManager instance for registering commands
manager = CommandManager()
response = ResponseManager()
response.set_command_manager(manager)


# -----------------------------
# Example Command: !help
# -----------------------------
class HelpCommand:

	async def run(self, message, args):

		embed = Embed(title="PyBot Commands", color=0xF39C12)

		for command, desc in manager.helps.items():
			desc = desc.split('|')
			embed.add_field(
				name=f"{command} {desc[0]}",
				value=desc[1],
				inline=False
			)

		await message.channel.send(embed=embed)

# Register the !help command
manager.register_command("!help", HelpCommand(), "| Displays a list of commands.")


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
manager.register_command("!home", HomeCommand(), "| Sets the current channel as PyBot's message board.")


# -----------------------------
# Example Command: !announcement
# -----------------------------
class AccouncementCommand:
	async def run(self, message, args):
		if not message.author.guild_permissions.administrator:
			await message.channel.send("Only admins can use !announcement.")
			return

		home_channel_id = GetConfig("home_channels", guild_id=message.guild.id).value()

		attachments = []

		for att in message.attachments:
			data = await att.read()
			file = discord.File(io.BytesIO(data), filename=att.filename)
			attachments.append(file)

		if home_channel_id:
			channel = message.guild.get_channel(int(home_channel_id))
			if channel:
				content = message.content.replace("!announcement", "", 1).strip()
				await channel.send(content=content, files=attachments)
			else:
				await message.channel.send("Home channel could not be found.")
		else:
			await message.channel.send("No home channel set. use !home to set the current channel as home.")

# Register the !home command
manager.register_command("!announcement", AccouncementCommand(), "@message ~attachment | Sends the following message to the message board.")


# -----------------------------
# Example Command: !embed
# -----------------------------
class EmbedCommand:
	async def run(self, message, args):
		if not message.author.guild_permissions.administrator:
			await message.channel.send("Only admins can use !embed.")
			return

		home_channel_id = GetConfig("home_channels", guild_id=message.guild.id).value()

		if home_channel_id:
			channel = message.guild.get_channel(int(home_channel_id))
			if channel:

				embed = Embed(title="Embed")
				if message.attachments:
					if message.attachments[0]:
						embed.set_image(url=message.attachments[0].url)

				content = message.content.replace("!embed", "", 1).strip()
				embed.description = content

				await channel.send(embed=embed)
			else:
				await message.channel.send("Home channel could not be found.")
		else:
			await message.channel.send("No home channel set. use !home to set the current channel as home.")

# Register the !home command
manager.register_command("!embed", EmbedCommand(), " @message ~attachment | Sends the following message and attachemnt to the message board as an embed.")


# -----------------------------
# Example Command: !autorole
# -----------------------------
class AutoRoleCommand:
    async def run(self, message, args):
        """
        Triggered when a user runs !autorole.
        Handles permission checking, sets up a temporary message listener,
        and prompts the admin with instructions for configuring the autorole.
        """
        # Only allow administrators to use this command
        if not message.author.guild_permissions.administrator:
            await message.channel.send("Only admins can use !autorole.")
            return

        # Set a timeout for the response (here, 2 minutes)
        timeout_at = datetime.datetime.utcnow() + datetime.timedelta(seconds=120)

        # Register this user/message with the response manager so we can capture
        # their follow-up message with role setup information.
        # This avoids using blocking input and lets the bot continue running.
        response.await_message(
            channel_id=message.channel.id,
            user_id=message.author.id,
            timeout_message="Auto Role timed out.",
            timeout_datetime=timeout_at,
            command=args[0]
        )

        # Prompt the admin with instructions and the expected message format
        # Using a formatted string helps admins understand how to structure roles
        prompt = """## Reaction Role Setup

Reply using the following format:

$Title Your title here
$Description A short description here

$Roles
:emoji: Role Name
:emoji: Role Name
:emoji: Role Name

[roles] in the description will display a list of all available roles."""

        await message.channel.send(prompt)

    async def on_response(self, client, message):
        """
        Handles the message the admin sends in response to the prompt.
        Parses the $Title, $Description, and $Roles sections and creates
        the embedded message with reaction roles.
        """
        content = message.content.splitlines()

        title = ""
        description = ""
        roles = []
        section = None

        # Iterate through each line and determine which section it belongs to
        for line in content:
            line = line.strip()
            if line.startswith("$Title"):
                title = line[len("$Title"):].strip()
            elif line.startswith("$Description"):
                description = line[len("$Description"):].strip()
            elif line.startswith("$Roles"):
                section = "roles"
            elif section == "roles" and line:
                # Split line into emoji and role name
                # maxsplit=1 ensures that role names with spaces are handled correctly
                parts = line.split(maxsplit=1)
                if len(parts) == 2:
                    emoji, role_name = parts
                    # Use discord.utils.get to safely retrieve the Role object
                    role = discord.utils.get(message.guild.roles, name=role_name)
                    if role is None:
                        await message.channel.send(f"Invalid role: {role_name} doesn't exist.")
                        return
                    # Store as tuple to keep emoji and role name linked
                    roles.append((emoji, role_name))

        # Ensure all required fields are present
        if title == "" or description == "" or roles == []:
            await message.channel.send(
                "Invalid format. Make sure you include $Title, $Description, and at least one role under $Roles."
            )
            return

        # Replace placeholder [roles] with actual formatted list
        role_list = '\n\n '.join(f"{emoji}  {name}" for emoji, name in roles)
        description = description.replace("[roles]", "\n\n" + role_list)

        # Create an embed for nicer formatting in Discord
        embed = Embed(title=title, color=0x9CF312)
        embed.description = description
        sent = await message.channel.send(embed=embed)

        # Add reaction emojis for users to click
        # This allows users to self-assign roles by reacting
        for emoji, _ in roles:
            await sent.add_reaction(emoji)

        # Set a long-term reaction listener for this message
        # The timeout is extremely long to keep the message "permanent"
        timeout_at = datetime.datetime.utcnow() + datetime.timedelta(days=36500)
        response.static_reaction(
            message_id=sent.id,
            guild_id=sent.guild.id,
            channel_id=sent.channel.id,
            user_id=0,
            timeout_message="Timed out.",
            timeout_datetime=timeout_at,
            command="!autorole"
        )

        # Save the autorole setup in config for persistence across restarts
        autorole = {"message_id": sent.id, "roles": roles}
        guild_autoroles = GetConfig("autorole", guild_id=message.guild.id).value() or []
        guild_autoroles.append(autorole)
        SetConfig("autorole", guild_autoroles, guild_id=sent.guild.id)

    async def on_reaction(self, client, reaction, user):
        """
        Triggered when a user reacts to an autorole message.
        Adds the corresponding role to the user.
        """
        guild_autoroles = GetConfig("autorole", guild_id=reaction.message.guild.id).value()

        for entry in list(guild_autoroles):
            if entry["message_id"] != reaction.message.id:
                continue

            # Map emojis to role names for this message
            roles = {emoji: role for emoji, role in entry["roles"]}
            role_name = roles.get(reaction.emoji)
            role = discord.utils.get(reaction.message.guild.roles, name=role_name)
            if role:
                await user.add_roles(role)
                # Print colored console log for debugging
                print(f"\033[33m[Autorole]\033[32m [{user.name}]\033[0m Added role: \033[33m{role_name} \033[34m({reaction.message.id}) \033[0m")
            else:
                print(f"\033[33m[Autorole]\033[0m {role_name} role doesn't exist.\033[0m")

    async def on_reaction_remove(self, client, reaction, user):
        """
        Triggered when a user removes a reaction.
        Removes the corresponding role from the user.
        """
        guild_autoroles = GetConfig("autorole", guild_id=reaction.message.guild.id).value()

        for entry in list(guild_autoroles):
            if entry["message_id"] != reaction.message.id:
                continue

            roles = {emoji: role for emoji, role in entry["roles"]}
            role_name = roles.get(reaction.emoji)
            role = discord.utils.get(reaction.message.guild.roles, name=role_name)
            if role:
                await user.remove_roles(role)
                print(f"\033[33m[Autorole]\033[32m [{user.name}]\033[0m Removed role: \033[33m{role_name} \033[34m({reaction.message.id}) \033[0m")
            else:
                print(f"\033[33m[Autorole]\033[0m {role_name} role doesn't exist.\033[0m")


# Register the !autorole command
manager.register_command("!autorole", AutoRoleCommand(), "| Initiates the autorole setup process.")





















# ----------------------------------------------------------
# 
# Example Command section.
# These commands are for demonstration purposes
# and serve no real function.
#
# ----------------------------------------------------------


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
#manager.register_command("!response", ResponseCommand(), "")


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
#manager.register_command("!reaction", ReactionCommand(), "")


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
#manager.register_command("!react", ReactCommand(), "")