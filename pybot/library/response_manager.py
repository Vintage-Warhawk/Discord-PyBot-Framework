"""
File: response_manager.py
Maintainer: Vintage Warhawk
Last Edit: 2025-11-23
"""

import datetime
import asyncio

from library.config_manager import SetConfig
from library.config_manager import GetConfig


class ResponseManager:
	"""
	Central manager for tracking awaited user responses (messages and reactions)
	and dispatching them to command handler classes.

	Responsibilities:
		- Store pending message/reaction waits.
		- Route incoming messages/reactions to the appropriate handler class.
		- Handle timeout expiration and notify channels.
	"""

	def __init__(self):
		self.command_manager = None

		# Each entry contains:
		#   channel_id, user_id, timeout_message, timeout_datetime, command
		self.awaiting_messages = []

		# Each entry contains:
		#   message_id, channel_id, user_id, timeout_message, timeout_datetime, command
		self.awaiting_reactions = []

		# Each entry contains:
		#   message_id, channel_id, user_id, timeout_message, timeout_datetime, command
		self.static_reactions = []

		all_reactions = GetConfig("response_reactions").all()
		for guild_id, reactions in all_reactions.items():
			if not isinstance(reactions, list):
				reactions = []
			for reaction in reactions:

				reaction = {
					"message_id": int(reaction.get("message_id", 0)),
					"guild_id": int(reaction.get("guild_id", 0)),
					"channel_id": int(reaction.get("channel_id", 0)),
					"user_id": int(reaction.get("user_id", 0)),
					"timeout_message": str(reaction.get("timeout_message", "")),
					"timeout_datetime": str(reaction.get("timeout_datetime", "")),
					"command": str(reaction.get("command", "")),
				}

				self.static_reactions.append(reaction)

	def set_command_manager(self, cm):
		self.command_manager = cm

	# ======================================================================
	#  Incoming Event Handlers
	# ======================================================================

	async def handle_message(self, client, message, command):
		"""
		Dispatch an incoming message to the command class's on_response() method.

		Args:
			message (discord.Message)
			command: Command to grab the callback from.

		Notes:
			- Validates the command class.
			- Errors are caught and logged to avoid breaking the loop.
		"""

		callback = self.command_manager.hooks.get(command.lower())

		if not hasattr(callback, "on_response"):
			print("[ResponseManager] Callback missing on_response()")
			return

		try:
			print(f"\033[33m[Response]\033[32m [{message.author.name}]\033[0m Responded: \033[33m{message.content}\033[0m")
			await callback.on_response(client, message)
		except Exception as e:
			print(f"[ResponseManager] Error in message callback: {e}")

	async def handle_reaction(self, client, reaction, user, command):
		"""
		Dispatch an incoming reaction event to the command class's on_reaction() method.

		Args:
			reaction (discord.Reaction)
			user (discord.User)
			command: Command to grab the callback from.
		"""

		callback = self.command_manager.hooks.get(command.lower())

		if not hasattr(callback, "on_reaction"):
			print("[ResponseManager] Callback missing on_reaction()")
			return

		try:
			print(f"\033[33m[Response]\033[32m [{user.name}]\033[0m Reacted: \033[33m{reaction.emoji}\033[0m")
			await callback.on_reaction(client, reaction, user)
		except Exception as e:
			print(f"[ResponseManager] Error in reaction callback: {e}")

	# ======================================================================
	#  Registration of Awaited Responses
	# ======================================================================

	def await_message(self, channel_id, user_id, timeout_message,
					  timeout_datetime, command):
		"""
		Register a pending awaited message.

		Args:
			channel_id (int)
			user_id (int) — If 0, any user may respond.
			timeout_message (str)
			timeout_datetime (datetime)
			command: Command to grab callback from.
		"""
		self.awaiting_messages.append({
			"channel_id": channel_id,
			"user_id": user_id,
			"timeout_message": timeout_message,
			"timeout_datetime": timeout_datetime.isoformat(),
			"command": command,
		})

	def await_reaction(self, message_id, user_id, channel_id,
					   timeout_message, timeout_datetime, command):
		"""
		Register a pending awaited reaction.

		Args:
			message_id (int)
			user_id (int) — If 0, any user may respond.
			channel_id (int)
			timeout_message (str)
			timeout_datetime (datetime)
			command: Command to grab callback from.
		"""
		self.awaiting_reactions.append({
			"message_id": message_id,
			"channel_id": channel_id,
			"user_id": user_id,
			"timeout_message": timeout_message,
			"timeout_datetime": timeout_datetime.isoformat(),
			"command": command,
		})

	def static_reaction(self, message_id, user_id, channel_id, guild_id,
					   timeout_message, timeout_datetime, command):
		"""
		Register a static reaction.

		Args:
			message_id (int)
			user_id (int) — If 0, any user may respond.
			channel_id (int)
			timeout_message (str)
			timeout_datetime (datetime)
			command: Command to grab callback from.
		"""

		reaction = {
			"message_id": message_id,
			"guild_id": guild_id,
			"channel_id": channel_id,
			"user_id": user_id,
			"timeout_message": timeout_message,
			"timeout_datetime": timeout_datetime.isoformat(),
			"command": command,
		}

		self.static_reactions.append(reaction)

		print(self.static_reactions)

		guild_reactions = GetConfig("response_reactions", guild_id=guild_id).value()
		if guild_reactions is None:
			guild_reactions = []

		guild_reactions.append(reaction)

		SetConfig("response_reactions", guild_reactions, guild_id=guild_id)



	# ======================================================================
	#  Timeout Processing
	# ======================================================================

	def check_timeouts(self, client):
		"""
		Process timeout expiration for message and reaction waits.

		Args:
			client (discord.Client)
				Used for sending timeout notifications.

		Behavior:
			- If timeout reached, notify channel with timeout_message.
			- Remove expired entries.
			- Preserve active entries.
		"""
		now = datetime.datetime.utcnow()

		# ------------------------------
		#  Message timeouts
		# ------------------------------
		active = []
		for entry in self.awaiting_messages:
			entry["timeout_datetime"] = datetime.datetime.fromisoformat(entry["timeout_datetime"])
			if now >= entry["timeout_datetime"]:
				channel = client.get_channel(entry["channel_id"])
				if channel:
					print(f"\033[33m[Cleanup]\033[36m [Response]\033[0m {entry["timeout_message"]}")
					asyncio.create_task(channel.send(entry["timeout_message"]))
			else:
				active.append(entry)

		self.awaiting_messages = active

		# ------------------------------
		#  Reaction timeouts
		# ------------------------------
		active = []
		for entry in self.awaiting_reactions:
			entry["timeout_datetime"] = datetime.datetime.fromisoformat(entry["timeout_datetime"])
			if now >= entry["timeout_datetime"]:
				channel = client.get_channel(entry["channel_id"])
				if channel:
					print(f"\033[33m[Cleanup]\033[36m [Response]\033[0m {entry["timeout_message"]}")
					asyncio.create_task(channel.send(entry["timeout_message"]))
			else:
				active.append(entry)

		self.awaiting_reactions = active

		# ------------------------------
		#  Static Reaction timeouts
		# ------------------------------
		active = []
		for entry in self.static_reactions:
			print(type(entry["timeout_datetime"]))
			entry["timeout_datetime"] = datetime.datetime.fromisoformat(entry["timeout_datetime"])
			if now >= entry["timeout_datetime"]:
				reactions = GetConfig("response_reactions", guild_id=entry["guild_id"]).value()
				if reactions is None:
					reactions = []
				reactions = [r for r in reactions if r["message_id"] != entry["message_id"]]
				
				SetConfig("response_reactions", reactions, guild_id=entry["guild_id"])

				channel = client.get_channel(entry["channel_id"])
				if channel:
					print(f"\033[33m[Cleanup]\033[36m [Response]\033[0m {entry["timeout_message"]}")
					asyncio.create_task(channel.send(entry["timeout_message"]))
			else:
				active.append(entry)

		self.static_reactions = active