"""
File: schedule_manager.py
Maintainer: Vintage Warhawk
Last Edit: 2025-11-21
"""

class ScheduleManager:
	"""
	Manages schedules for tasks grouped by interval.

	Attributes:
		schedules (list): A list of schedule hooks.
	"""

	def __init__(self):
		"""
		Initialize the ScheduleManager with an empty schedule list.
		"""
		self.schedules = {}

	def register_schedule(self, interval_name: str, schedule ):
		"""
		Register a schedule calling all tasks on that interval.

		Args:
			interval_name (str): e.g., "hourly", "daily"
			schedule: class
		"""
		self.schedules[interval_name] = schedule