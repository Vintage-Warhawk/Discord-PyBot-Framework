from tasks_manager import TaskManager
from config import GetConfig

manager = TaskManager()

# Example task: Hourly Task
class HourlyTask:
    async def run(self, client):
        for guild in client.guilds:
            home_channel_id = GetConfig("home_channels", guild_id=guild.id).value()
            if home_channel_id:
                channel = guild.get_channel(int(home_channel_id))
                if channel:
                    await channel.send("Hourly task executed!")

manager.register_task("hourly", HourlyTask())

# Example task: Daily Task
class DailyTask:
    async def run(self, client):
        for guild in client.guilds:
            home_channel_id = GetConfig("home_channels", guild_id=guild.id).value()
            if home_channel_id:
                channel = guild.get_channel(int(home_channel_id))
                if channel:
                    await channel.send("Daily task executed!")

manager.register_task("daily", DailyTask())

# Example task: Test Task
#class TestTask:
#    async def run(self, client):
#        for guild in client.guilds:
#            home_channel_id = GetConfig("home_channels", guild_id=guild.id).value()
#            if home_channel_id:
#                channel = guild.get_channel(int(home_channel_id))
#                if channel:
#                    await channel.send("Test task executed!")

# manager.register_task("test", TestTask())