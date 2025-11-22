"""
File: response_manager.py
Maintainer: Vintage Warhawk
Last Edit: 2025-11-21
"""

import datetime
import asyncio


class ResponseManager:
	"""
	Central manager for tracking awaited user responses (messages and reactions)
	and dispatching them to callback handler classes.

	Responsibilities:
		- Store pending message/reaction waits.
		- Route incoming messages/reactions to the appropriate handler class.
		- Handle timeout expiration and notify channels.
	"""

	def __init__(self):
		# Each entry contains:
		#   channel_id, user_id, timeout_message, timeout_datetime, callback
		self.awaiting_messages = []

		# Each entry contains:
		#   message_id, channel_id, user_id, timeout_message, timeout_datetime, callback
		self.awaiting_reactions = []

	# ======================================================================
	#  Incoming Event Handlers
	# ======================================================================

	async def handle_message(self, message, callback):
		"""
		Dispatch an incoming message to the callback class's on_response() method.

		Args:
			message (discord.Message)
			callback: Instance of a handler class that defines on_response(message)

		Notes:
			- Validates the callback class.
			- Errors are caught and logged to avoid breaking the loop.
		"""
		if not hasattr(callback, "on_response"):
			print("[ResponseManager] Callback missing on_response()")
			return

		try:
			print(f"\033[33m[Response]\033[32m [{message.author.name}]\033[0m Responded: \033[33m{message.content}\033[0m")
			await callback.on_response(message)
		except Exception as e:
			print(f"[ResponseManager] Error in message callback: {e}")

	async def handle_reaction(self, reaction, user, callback):
		"""
		Dispatch an incoming reaction event to the callback class's on_reaction() method.

		Args:
			reaction (discord.Reaction)
			user (discord.User)
			callback: Instance of a handler class that defines on_reaction(reaction, user)
		"""
		if not hasattr(callback, "on_reaction"):
			print("[ResponseManager] Callback missing on_reaction()")
			return

		try:
			print(f"\033[33m[Response]\033[32m [{user.name}]\033[0m Reacted: \033[33m{reaction.emoji}\033[0m")
			await callback.on_reaction(reaction, user)
		except Exception as e:
			print(f"[ResponseManager] Error in reaction callback: {e}")

	# ======================================================================
	#  Registration of Awaited Responses
	# ======================================================================

	def await_message(self, channel_id, user_id, timeout_message,
					  timeout_datetime, callback):
		"""
		Register a pending awaited message.

		Args:
			channel_id (int)
			user_id (int) — If 0, any user may respond.
			timeout_message (str)
			timeout_datetime (datetime)
			callback: Handler instance
		"""
		self.awaiting_messages.append({
			"channel_id": channel_id,
			"user_id": user_id,
			"timeout_message": timeout_message,
			"timeout_datetime": timeout_datetime,
			"callback": callback,
		})

	def await_reaction(self, message_id, user_id, channel_id,
					   timeout_message, timeout_datetime, callback):
		"""
		Register a pending awaited reaction.

		Args:
			message_id (int)
			user_id (int) — If 0, any user may respond.
			channel_id (int)
			timeout_message (str)
			timeout_datetime (datetime)
			callback: Handler instance
		"""
		self.awaiting_reactions.append({
			"message_id": message_id,
			"channel_id": channel_id,
			"user_id": user_id,
			"timeout_message": timeout_message,
			"timeout_datetime": timeout_datetime,
			"callback": callback,
		})

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
			if now >= entry["timeout_datetime"]:
				channel = client.get_channel(entry["channel_id"])
				if channel:
					print(f"\033[33m[Cleanup]\033[36m [Response]\033[0m {entry["timeout_message"]}")
					asyncio.create_task(channel.send(entry["timeout_message"]))
			else:
				active.append(entry)

		self.awaiting_reactions = active
