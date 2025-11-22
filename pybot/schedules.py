"""
File: tasks.py
Maintainer: Vintage Warhawk
Last Edit: 2025-11-21
"""

from datetime import datetime, timedelta
import pytz

TIMEZONE = pytz.timezone("America/Chicago")

from library.schedule_manager import ScheduleManager
from library.config_manager import GetConfig

# Create a ScheduleManager instance to register tasks
manager = ScheduleManager()

# -----------------------------
# Example Schedule: Test
# -----------------------------
class TestSchedule:
	"""
	Schedule that runs hooked tasks every 10 seconds.
	"""
	async def get(self, client):
		seconds = 10
		return seconds

# Register the test schedule
manager.register_schedule("test", TestSchedule())

# -----------------------------
# Example Schedule: Minutely
# -----------------------------
class MinutelySchedule:
	"""
	Schedule that runs hooked tasks on the minute.
	"""
	async def get(self, client):
		now = datetime.now(TIMEZONE).replace(microsecond=0)
		next_minute = (now + timedelta(minutes=1)).replace(second=0, microsecond=0)
		return (next_minute - now).total_seconds()

# Register the minutely schedule
manager.register_schedule("minutely", MinutelySchedule())

# -----------------------------
# Example Schedule: Hourly
# -----------------------------
class HourlySchedule:
	"""
	Schedule that runs hooked tasks on the hour.
	"""
	async def get(self, client):
		now = datetime.now(TIMEZONE).replace(microsecond=0)
		next_hour = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
		return (next_hour - now).total_seconds()

# Register the hourly schedule
manager.register_schedule("hourly", HourlySchedule())

# -----------------------------
# Example Schedule: Noon
# -----------------------------
class NoonSchedule:
	"""
	Schedule that runs hooked tasks every day at noon.
	"""
	async def get(self, client):
		now = datetime.now(TIMEZONE).replace(microsecond=0)
		next_noon = now.replace(hour=12, minute=0, second=0, microsecond=0)
		if now >= next_noon:
			next_noon += timedelta(days=1)

		return (next_noon - now).total_seconds()

# Register the noon schedule
manager.register_schedule("noon", NoonSchedule())