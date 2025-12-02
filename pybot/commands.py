"""
File: commands.py
Maintainer: Vintage Warhawk
Last Edit: 2025-11-30

Description:
This file contains all custom command classes for the Discord bot framework.
Commands are registered with a central HookManager instance. Each command
class must implement an asynchronous `run` method that handles the logic
when the command is invoked.
"""

import io
import datetime
import time
import discord
from discord import ui

from library.command_manager import CommandManager
from library.config_manager import SetConfig
from library.config_manager import GetConfig
from library.response_manager import ResponseManager
from library.emoji_converter import EmojiConverter

# Create a CommandManager, ReponseManager and TaskManager instance for registering commands
manager = CommandManager()
response = ResponseManager()
response.set_command_manager(manager)
from tasks import manager as task_manager

# -----------------------------
# Example Command: !help
# -----------------------------
class HelpCommand:

	async def run(self, client, message, args):

		embed = discord.Embed(title="PyBot Commands", color=0xF39C12)

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
# Example Command: !defaultrole
# -----------------------------
class DefaultRoleCommand:
	"""
	Command for admins to set the default role for the server.
	Usage: !home
	"""
	async def run(self, client, message, args):
		"""
		Sets the default role in the persistent config.
		Only users with administrator permissions can run this command.
		"""
		if not message.author.guild_permissions.administrator:
			await message.channel.send("Only admins can set the home channel.")
			return

		role_name = message.content.replace("!role", "", 1).strip()

		role = discord.utils.get(message.guild.roles, name=role_name)

		if role is None:
			await message.channel.send(f"Invalid role: '{role_name}' doesn't exist.")
			return

		# Store the channel ID for this guild in the config system
		SetConfig("default_role", role_name, guild_id=message.guild.id)
		print(f"\033[33m[Config]\033[0m new default role set: \033[33m{role_name} ({message.channel.id})\033[0m")
		await message.channel.send(f"{role_name} is now the default role when joining!")

# Register the !role command
manager.register_command("!defaultrole", DefaultRoleCommand(), "@role | Sets the default role for the server.")


# -----------------------------
# Example Command: !home
# -----------------------------
class HomeCommand:
	"""
	Command for admins to set the 'home' channel for the server.
	Usage: !home
	"""
	async def run(self, client, message, args):
		"""
		Saves the current channel as the home channel in the persistent config.
		Only users with administrator permissions can run this command.
		"""
		if not message.author.guild_permissions.administrator:
			await message.channel.send("Only admins can set the home channel.")
			return

		# Store the channel ID for this guild in the config system
		SetConfig("home_channels", str(message.channel.id), guild_id=message.guild.id)
		print(f"\033[33m[Config]\033[0m new home directory set: \033[33m{message.channel.name} \033[34m({message.channel.id})\033[0m")
		await message.channel.send("This channel is now set as the home channel for this server!")

# Register the !home command
manager.register_command("!home", HomeCommand(), "| Sets the current channel as PyBot's message board.")


# -----------------------------
# Example Command: !announcement
# -----------------------------
class AccouncementCommand:
	async def run(self, client, message, args):
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
	async def run(self, client, message, args):
		if not message.author.guild_permissions.administrator:
			await message.channel.send("Only admins can use !embed.")
			return

		home_channel_id = GetConfig("home_channels", guild_id=message.guild.id).value()

		if home_channel_id:
			channel = message.guild.get_channel(int(home_channel_id))
			if channel:

				embed = discord.Embed(title="discord.Embed")
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
# Example Command: !tickethome
# -----------------------------
# Sends a message with a button to close the ticket.
class AdminTicketButton(ui.View):
	def __init__(self):
		super().__init__(timeout=None)

	@ui.button(label="Close", style=discord.ButtonStyle.danger, custom_id="ticket-close")
	async def open(self, interaction: discord.Interaction, button):
		guild_tickets = GetConfig("tickets", guild_id=interaction.guild.id).value() or []

		for entry in list(guild_tickets):
			if entry["channel_id"] != interaction.channel.id:
				continue
			await interaction.response.send_message("Ticket Closed.", ephemeral=True)

			guild = interaction.guild
			user = guild.get_member(entry["user_id"])
			if user:
				try:
					await user.send(f"Your submission `{entry["ticket_id"]}` in {guild.name} has been closed.")
				except:
					pass
	
			await interaction.channel.delete(reason=f"{entry["ticket_id"]} closed.")

			guild_tickets.remove(entry)
			SetConfig("tickets", guild_tickets, guild_id=guild.id)
			print(f"\033[33m[Ticket]\033[0m Ticket Closed by \033[33m{interaction.user.name} \033[34m({entry["ticket_id"]})\033[0m")


# Creates a Modal so the user can submit a ticket.
class TicketModal(ui.Modal, title="Ticket Submission"):
	def __init__(self, view):
		super().__init__()
		self.view_message = view
		self.reason = ui.TextInput(label="Reason:")
		self.desc = ui.TextInput(label="Description:", style=discord.TextStyle.paragraph)
		self.add_item(self.reason)
		self.add_item(self.desc)

	async def on_submit(self, interaction: discord.Interaction):
		ticket_id = f"ticket-{int(time.time() * 1000)}"
		print(f"\033[33m[Ticket]\033[0m New Ticket Submission: \033[33m{self.reason.value} \033[34m({ticket_id})\033[0m")

		guild = interaction.guild
		user = interaction.user
		category = interaction.channel.category

		admin_roles = [r for r in guild.roles if r.permissions.administrator]
		overwrites = {
			guild.default_role: discord.PermissionOverwrite(
				view_channel=False,
				send_messages=False
			),
			user: discord.PermissionOverwrite(
				view_channel=True,
				send_messages=True
			),
			guild.me: discord.PermissionOverwrite(
				view_channel=True,
				send_messages=True,
				manage_channels=True
			)
		}

		for role in admin_roles:
			overwrites[role] = discord.PermissionOverwrite(
				view_channel=True,
				send_messages=True
			)

		channel = await guild.create_text_channel(
			ticket_id,
			overwrites=overwrites,
			category=category
		)

		embed = discord.Embed(
		    title=self.reason.value,
		    description=self.desc.value,
		    color=0x3498db
		)

		await channel.send(
			f"{user.mention} opened {ticket_id}",
			embed=embed,
			view=AdminTicketButton()
		)

		ticket = {"user_id": user.id, "ticket_id": ticket_id, "channel_id": channel.id}

		guild_tickets = GetConfig("tickets", guild_id=guild.id).value() or []
		guild_tickets.append(ticket)
		SetConfig("tickets", guild_tickets, guild_id=guild.id)

		await interaction.response.send_message("Ticket Submitted.", ephemeral=True)

# Sends a message with a button to open the Modal.
class TicketButton(ui.View):
	def __init__(self):
		super().__init__(timeout=None)

	@ui.button(label="Submit", style=discord.ButtonStyle.primary, custom_id="ticket_submission")
	async def open(self, interaction: discord.Interaction, button):
		await interaction.response.send_modal(TicketModal(interaction.message))

class TicketTask:
	"""
	Task that re-registers the ticket button.
	"""

	async def run(self, client):
		client.add_view(TicketButton()) # registers persistent button
		client.add_view(AdminTicketButton())
		print("\033[33m[Ticket]\033[0m Registered Ticket Buttons.")

task_manager.register_task("on_ready", "Ticket Submit", TicketTask())

# TicketHome Command
class TicketHomeCommand:
	"""
	Command for admins to set the 'home' channel for tickets.
	Usage: !home
	"""

	async def run(self, client, message, args):
		"""
		Saves the current channel as the ticket home channel in the persistent config.
		Only users with administrator permissions can run this command.
		"""
		if not message.author.guild_permissions.administrator:
			await message.channel.send("Only admins can set the ticket home channel.")
			return

		# Store the channel ID for this guild in the config system
		SetConfig("ticket_channels", str(message.channel.id), guild_id=message.guild.id)
		print(f"\033[33m[Config]\033[0m new ticket directory set: \033[33m{message.channel.name} \033[34m({message.channel.id})\033[0m")
		await message.channel.send("This channel is now set as the ticket channel for this server!")

		await message.channel.send(
			"Want to submit a ticket?",
			view=TicketButton()
		)

# Register the !tickethome command
manager.register_command("!tickethome", TicketHomeCommand(), "| Sets the current channel as PyBot's ticket board.")

# -----------------------------
# Example Command: !autorole
# -----------------------------
class AutoRoleCommand:

	async def run(self, client, message, args):
		"""
		Triggered when a user runs !autorole.
		Handles permission checking, uses discord Modal to set up autoroles.
		"""
		# Only allow administrators to use this command
		if not message.author.guild_permissions.administrator:
			await message.channel.send("Only admins can use !autorole.")
			return

		# Creates a Modal so the admin can setup autoroles.
		class AutoRoleModal(ui.Modal, title="AutoRole Setup"):
			def __init__(self, view, message):
				super().__init__()
				self.view_message = view
				self.sender_message = message
				self.embedtitle = ui.TextInput(label="Title:")
				self.embeddesc = ui.TextInput(label="Description: (use [roles] to list roles)", style=discord.TextStyle.paragraph)
				self.embedroles = ui.TextInput(label="Roles (:emoji: Role Name)", style=discord.TextStyle.paragraph)
				self.add_item(self.embedtitle)
				self.add_item(self.embeddesc)
				self.add_item(self.embedroles)

			async def on_submit(self, interaction: discord.Interaction):

				await interaction.response.send_message("Creating AutoRole...", ephemeral=True)

				roles = []
				title = self.embedtitle.value
				description = self.embeddesc.value

				# Parse lines for roles.
				for line in self.embedroles.value.splitlines():
					line = line.strip()
					if not line:
						continue

					# Loop through the line until no more emoji-role pairs remain
					while line:
						if line.startswith(":") and ":" in line[1:]:
							end_emoji = line.find(":", 1) + 1
							emoji_name = line[:end_emoji]
							line = line[end_emoji:].lstrip()
						else:
							break

						next_emoji_index = line.find(" :")
						if next_emoji_index == -1:
							role_name = line.strip()
							line = ""
						else:
							role_name = line[:next_emoji_index].strip()
							line = line[next_emoji_index+1:].lstrip()

						if emoji_name and role_name:
							
							# Get the Role object from the guild
							role = discord.utils.get(interaction.guild.roles, name=role_name)
							if role is None:
								await interaction.followup.send(f"Invalid role: '{role_name}' doesn't exist.", ephemeral=True)
								try:
									await interaction.delete_original_response()
								except:
									pass
								return

							emoji = EmojiConverter.convert_emoji(emoji_name, interaction.guild)

							if emoji is None:
								await interaction.followup.send(f"Invalid emoji: `{emoji_name}` doesn't exist.", ephemeral=True)
								try:
									await interaction.delete_original_response()
								except:
									pass
								return

							roles.append((str(emoji), role_name))

				if len(roles) == 0:
					await interaction.followup.send("No roles provided.", ephemeral=True)
					try:
						await interaction.delete_original_response()
					except:
						pass
					return

				for emoji, role_name in roles:
					print(f"{emoji} {role_name}")

				for _, role_name in roles:
					if [r for e, r in roles].count(role_name) > 1:
						await interaction.followup.send("Duplicate Roles.", ephemeral=True)
						try:
							await interaction.delete_original_response()
						except:
							pass
						return

				for emoji, _ in roles:
					if [e for e, r in roles].count(emoji) > 1:
						await interaction.followup.send("Duplicate Emojis.", ephemeral=True)
						try:
							await interaction.delete_original_response()
						except:
							pass
						return

				# Replace placeholder [roles] with actual formatted list
				role_list = '\n '.join(f"{emoji}  {name}" for emoji, name in roles)
				description = description.replace("[roles]", "\n\n" + role_list)

				# Create an embed for nicer formatting in Discord
				embed = discord.Embed(title=title, color=0x9CF312)
				embed.description = description
				sent = await interaction.channel.send(embed=embed)

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
				guild_autoroles = GetConfig("autorole", guild_id=sent.guild.id).value() or []
				guild_autoroles.append(autorole)
				SetConfig("autorole", guild_autoroles, guild_id=sent.guild.id)

				try:
					await self.sender_message.delete()
					await self.view_message.delete()
				except:
					pass

				try:
					await interaction.delete_original_response()
				except:
					pass

		# Sends a message with a button to open the Modal.
		class AutoRoleButton(ui.View):
			def __init__(self, message):
				super().__init__()
				self.sender_message = message

			@ui.button(label="Setup", style=discord.ButtonStyle.primary)
			async def open(self, interaction: discord.Interaction, button):
				if interaction.user != self.sender_message.author:
					await interaction.response.send_message(
						"You can't use this button.", ephemeral=True
					)
					return
				try:
					await interaction.response.send_modal(AutoRoleModal(interaction.message, self.sender_message))
				except Exception as e:
					print(e)
		await message.channel.send(
			"Do you want to setup autoroles?",
			view=AutoRoleButton(message)
		)

	async def on_reaction(self, client, message, reaction, user):
		"""
		Triggered when a user reacts to an autorole message.
		Adds the corresponding role to the user.
		"""

		guild_autoroles = GetConfig("autorole", guild_id=message.guild.id).value()

		for entry in list(guild_autoroles):
			if entry["message_id"] != message.id:
				continue

			# Map emojis to role names for this message
			roles = {emoji: role for emoji, role in entry["roles"]}

			role_name = roles.get(str(reaction))
			if role_name is None:
				print(f"\033[33m[Autorole]\033[0m {reaction} has no role.\033[0m")
				return

			role = discord.utils.get(message.guild.roles, name=role_name)
			if role:
				await user.add_roles(role)
				# Print colored console log for debugging
				print(f"\033[33m[Autorole]\033[32m [{user.name}]\033[0m Added role: \033[33m{role_name} \033[34m({message.id}) \033[0m")
			else:
				print(f"\033[33m[Autorole]\033[0m {role_name} role doesn't exist.\033[0m")

	async def on_reaction_remove(self, client, message, reaction, user):
		"""
		Triggered when a user removes a reaction.
		Removes the corresponding role from the user.
		"""
		guild_autoroles = GetConfig("autorole", guild_id=message.guild.id).value()

		for entry in list(guild_autoroles):
			if entry["message_id"] != message.id:
				continue

			roles = {emoji: role for emoji, role in entry["roles"]}

			role_name = roles.get(str(reaction))
			if role_name is None:
				print(f"\033[33m[Autorole]\033[0m {reaction} has no role.\033[0m")
				return

			role = discord.utils.get(message.guild.roles, name=role_name)
			if role:
				await user.remove_roles(role)
				print(f"\033[33m[Autorole]\033[32m [{user.name}]\033[0m Removed role: \033[33m{role_name} \033[34m({message.id}) \033[0m")
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

	async def run(self, client, message, args):

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

	async def run(self, client, message, args):

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

	async def on_reaction(self, client, message, reaction, user):
		await message.channel.send(f"{user.name} reacted: {reaction}")

# Register the !response command
#manager.register_command("!reaction", ReactionCommand(), "")


# -----------------------------
# Example Command: !react
# -----------------------------
class ReactCommand:

	async def run(self, client, message, args):

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

	async def on_reaction(self, client, message, reaction, user):
		await message.channel.send(f"{user.name} reacted: {reaction}")

# Register the !response command
#manager.register_command("!react", ReactCommand(), "")