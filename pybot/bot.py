"""
File: bot.py
Maintainer: Vintage Warhawk
Last Edit: 2025-11-18

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
from tasks import manager  # TaskManager instance managing registered tasks
from commands import manager as command_manager  # CommandManager instance handling command hooks

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
        Ignores other bots. Passes content to the command manager.
        """
        if message.author.bot:
            return
        await command_manager.handle_message(message)

    def start_scheduled_tasks(self):
        """
        Starts asynchronous loops for hourly, daily, and test tasks.
        Each loop waits until its next scheduled run time before executing tasks.
        """

        async def hourly_loop():
            try:
                while True:
                    now = datetime.now(TIMEZONE)
                    next_hour = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
                    await asyncio.sleep((next_hour - now).total_seconds())

                    for name, task in manager.get_tasks("hourly").items():
                        print(f"\033[33m[Task]\033[36m [Hourly]\033[0m Running task: {name}")
                        await task.run(self)
            except asyncio.CancelledError:
                return

        async def daily_loop():
            try:
                while True:
                    now = datetime.now(TIMEZONE)
                    next_noon = now.replace(hour=12, minute=0, second=0, microsecond=0)
                    if now >= next_noon:
                        next_noon += timedelta(days=1)

                    await asyncio.sleep((next_noon - now).total_seconds())

                    for name, task in manager.get_tasks("daily").items():
                        print(f"\033[33m[Task]\033[35m [Daily]\033[0m Running task: {name}")
                        await task.run(self)
            except asyncio.CancelledError:
                return

        async def test_loop():
            try:
                while True:
                    await asyncio.sleep(10)
                    for name, task in manager.get_tasks("test").items():
                        print(f"\033[33m[Task]\033[31m [Testing]\033[0m Running task: {name}")
                        await task.run(self)
            except asyncio.CancelledError:
                return

        # create & store the tasks
        self.running_tasks.append(asyncio.create_task(hourly_loop()))
        self.running_tasks.append(asyncio.create_task(daily_loop()))
        self.running_tasks.append(asyncio.create_task(test_loop()))

    async def shutdown(self):
        """
        Cancels scheduled tasks and cleanly shuts down Discord client.
        Add additional shutdown procedures here in the future.
        """

        print("\033[33mShutting down PyBot...\033[0m\n")

        # cancel running task loops
        for task in self.running_tasks:
            task.cancel()

        # wait for cancellation to finish
        for task in self.running_tasks:
            try:
                await task
            except asyncio.CancelledError:
                pass

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
