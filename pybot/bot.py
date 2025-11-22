"""
File: bot.py
Maintainer: Vintage Warhawk
Last Edit: 2025-11-21

Description:
This is the main entry point for the Discord bot framework. It sets up the Discord client,
handles incoming messages, and schedules hourly, daily, and test tasks using asyncio.
It now includes proper task tracking and graceful shutdown for container environments.
"""

import os
import signal
import discord
import asyncio
from datetime import datetime, timedelta
import pytz

from schedules import manager as schedule_manager # ScheduleManager instance managing registered schedules
from tasks import manager as task_manager  # TaskManager instance managing registered tasks
from commands import manager as command_manager  # CommandManager instance handling command hooks
from commands import response as response_manager # ResponseManager instance handling response hooks

# Set the timezone for scheduled tasks
TIMEZONE = pytz.timezone("America/Chicago")

# Discord client intents configuration
intents = discord.Intents.default()
intents.message_content = True


class MyClient(discord.Client):
	"""
	Custom Discord client class that handles:
	- Bot readiness
	- Incoming messages
	- Scheduled task loops (hourly, daily, test)
	- Graceful shutdown
	"""

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.running_tasks = []  # store created tasks for later cancellation

	async def on_ready(self):
		"""
		Called when the bot is fully connected and ready.
		Starts scheduled task loops.
		"""
		print(f"Logged in as \033[32m{self.user}\033[0m")
		self.start_scheduled_tasks()

	async def on_message(self, message):
		"""
		Called when a new message is sent.
		Ignores other bots. Checks for waiting responses.
		Passes content to the command manager.
		"""
		if message.author.bot:
			return

		# Check message waiters
		for entry in list(response_manager.awaiting_messages):
			if entry["channel_id"] != message.channel.id:
				continue
			if entry["user_id"] not in (0, message.author.id):
				continue

			# Trigger callback
			await response_manager.handle_message(message, entry["callback"])
			response_manager.awaiting_messages.remove(entry)
			return  # Only one waiter per message

		await command_manager.handle_message(message)

	async def on_reaction_add(self, reaction, user):
		"""
		Called when a new reaction is added.
		Ignores other bots. Checks for waiting responses.
		"""
		if user.bot:
			return

		 # Check message waiters
		for entry in list(response_manager.awaiting_reactions):
			if entry["message_id"] != reaction.message.id:
				continue
			if entry["user_id"] not in (0, user.id):
				continue

			# Trigger callback
			await response_manager.handle_reaction(reaction, user, entry["callback"])
			response_manager.awaiting_reactions.remove(entry)
			return # Only one waiter per message

	def start_scheduled_tasks(self):
		"""
		Starts asynchronous loops for schedules.
		Each loop waits until its next scheduled run time before executing tasks.
		"""

		async def schedule_loop(interval_name, schedule):
			try:
				while True:
					seconds = await schedule.get(self)
					await asyncio.sleep(seconds)
					for name, task in task_manager.get_tasks(interval_name).items():
						print(f"\033[33m[Task]\033[36m [{interval_name}]\033[0m Running task: {name}")
						asyncio.create_task(task.run(self))
			except asyncio.CancelledError:
				return

		for name, schedule in schedule_manager.schedules.items():
			self.running_tasks.append(asyncio.create_task(schedule_loop( name, schedule )))


		# Loop to clean up responses that have hit their timeout limit. (15 second accuracy)
		async def response_cleanup():
			try:
				while True:
					await asyncio.sleep(15)
					response_manager.check_timeouts(self)
					
			except asyncio.CancelledError:
				# Cleanup pending response requests, and send time out message

				# Time out all pending message responses.
				for entry in response_manager.awaiting_messages:
					channel = self.get_channel(entry["channel_id"])
					if channel:
						print(f"[--- ] \033[31m[Shutdown]\033[36m [Response]\033[0m {entry["timeout_message"]}")
						await channel.send(entry["timeout_message"])

				# Time out all pending reaction responses.
				for entry in response_manager.awaiting_reactions:
					channel = self.get_channel(entry["channel_id"])
					if channel:
						print(f"[--- ] \033[31m[Shutdown]\033[36m [Response]\033[0m {entry["timeout_message"]}")
						await channel.send(entry["timeout_message"])

				return

		# create & store the cleanup task
		self.running_tasks.append(asyncio.create_task(response_cleanup()))

	async def shutdown(self):
		"""
		Cancels scheduled tasks and cleanly shuts down Discord client.
		Add additional shutdown procedures here in the future.
		"""

		print("\033[33mShutting down PyBot...\033[0m")

		# cancel running task loops
		print("Stopping all tasks.")

		task_count = len(self.running_tasks)

		for task in self.running_tasks:
			task.cancel()

		# wait for cancellation to finish
		for i, task in enumerate(self.running_tasks, 1):
			try:
				await task
				print(f"[{'-' * i}{' ' * (task_count - i)}] Task cancelled cleanly.\033[0m")
			except asyncio.CancelledError:
				print(f"[{'-' * i}{' ' * (task_count - i)}] Task cancelled \033[31m(CancelledError)\033[0m")
			except Exception as e:
				print(f"[{'-' * i}{' ' * (task_count - i)}] Task raised exception \033[31m{e}\033[0m")  # Log but continue

		print("All tasks stopped.")

		# close discord connection
		print("\033[31mPyBot shutdown complete.\033[0m")
		await self.close()


async def main():
	"""
	Main async entry point.
	Uses asyncio.run to start the client asynchronously.
	"""

	print(f"\n\033[33mStarting PyBot...\033[0m")

	loop = asyncio.get_running_loop()
	client = MyClient(intents=intents)

	stop_event = asyncio.Event()

	# signal handler
	def handle_sigterm():
		stop_event.set()

	loop.add_signal_handler(signal.SIGTERM, handle_sigterm)
	loop.add_signal_handler(signal.SIGINT, handle_sigterm)

	# start bot
	client_task = asyncio.create_task(client.start(os.getenv("DISCORD_TOKEN")))

	# wait until SIGTERM/SIGINT
	await stop_event.wait()

	# shutdown sequence
	await client.shutdown()

	# ensure discord.py task ends
	client_task.cancel()
	try:
		await client_task
	except asyncio.CancelledError:
		pass


if __name__ == "__main__":
	asyncio.run(main())
