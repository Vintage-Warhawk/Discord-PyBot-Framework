import os
import discord
import asyncio
from datetime import datetime, timedelta
import pytz
from tasks import manager
from commands import manager as command_manager

TIMEZONE = pytz.timezone("America/Chicago")

intents = discord.Intents.default()
intents.message_content = True

class MyClient(discord.Client):
    async def on_ready(self):
        print(f"Logged in as {self.user}")
        # Start tasks after ready
        asyncio.create_task(self.start_scheduled_tasks())

    async def on_message(self, message):
        if message.author.bot:
            return
        await command_manager.handle_message(message)

    async def start_scheduled_tasks(self):
        # Hourly loop
        async def hourly_loop():
            while True:
                now = datetime.now(TIMEZONE)
                next_hour = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
                await asyncio.sleep((next_hour - now).total_seconds())
                for task in manager.get_tasks("hourly"):
                    await task.run(self)

        # Daily loop
        async def daily_loop():
            while True:
                now = datetime.now(TIMEZONE)
                next_noon = now.replace(hour=12, minute=0, second=0, microsecond=0)
                if now >= next_noon:
                    next_noon += timedelta(days=1)
                await asyncio.sleep((next_noon - now).total_seconds())
                for task in manager.get_tasks("daily"):
                    await task.run(self)

        # Test loop running every 10 seconds
        async def test_loop():
            while True:
                await asyncio.sleep(10)  # run every 10 seconds
                for task in manager.get_tasks("test"):
                    await task.run(self)

        asyncio.create_task(hourly_loop())
        asyncio.create_task(daily_loop())
        asyncio.create_task(test_loop())


async def main():
    client = MyClient(intents=intents)
    await client.start(os.getenv("DISCORD_TOKEN"))  # async start, not run()


if __name__ == "__main__":
    asyncio.run(main())
