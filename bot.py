"""
File: bot.py
Maintainer: Vintage Warhawk
Last Edit: 2025-11-17

Description:
This is the main entry point for the Discord bot framework. It sets up the Discord client,
handles incoming messages, and schedules hourly, daily, and test tasks using asyncio.
"""

import os
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
intents.message_content = True  # Required to read message content

class MyClient(discord.Client):
    """
    Custom Discord client class that handles:
    - Bot readiness
    - Incoming messages
    - Scheduled tasks (hourly, daily, test)
    """

    async def on_ready(self):
        """
        Called when the bot is fully connected and ready.
        Starts all scheduled task loops asynchronously.
        """
        print(f"Logged in as \033[32m{self.user}\033[0m")
        asyncio.create_task(self.start_scheduled_tasks())

    async def on_message(self, message):
        """
        Called whenever a new message is sent in a server the bot is in.
        Ignores messages sent by bots.
        Passes messages to the command manager to handle registered commands.
        """
        if message.author.bot:
            return
        await command_manager.handle_message(message)

    async def start_scheduled_tasks(self):
        """
        Starts asynchronous loops for hourly, daily, and test tasks.
        Each loop waits until its next scheduled run time before executing tasks.
        """

        # Loop for hourly tasks
        async def hourly_loop():
            while True:
                now = datetime.now(TIMEZONE)
                # Calculate seconds until the next full hour
                next_hour = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
                await asyncio.sleep((next_hour - now).total_seconds())
                for task in manager.get_tasks("hourly"):
                    await task.run(self)

        # Loop for daily tasks (runs at 12:00 noon)
        async def daily_loop():
            while True:
                now = datetime.now(TIMEZONE)
                next_noon = now.replace(hour=12, minute=0, second=0, microsecond=0)
                if now >= next_noon:
                    next_noon += timedelta(days=1)
                await asyncio.sleep((next_noon - now).total_seconds())
                for task in manager.get_tasks("daily"):
                    await task.run(self)

        # Test loop that runs every 10 seconds for development
        async def test_loop():
            while True:
                await asyncio.sleep(10)
                for task in manager.get_tasks("test"):
                    await task.run(self)

        # Start all loops concurrently
        asyncio.create_task(hourly_loop())
        asyncio.create_task(daily_loop())
        asyncio.create_task(test_loop())


async def main():
    """
    Async entry point for the bot.
    Uses asyncio.run to start the client asynchronously.
    """
    client = MyClient(intents=intents)
    await client.start(os.getenv("DISCORD_TOKEN"))  # Bot token should be set as environment variable


if __name__ == "__main__":
    # Run the async main function when executed directly
    asyncio.run(main())
