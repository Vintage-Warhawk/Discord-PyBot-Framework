"""
File: tasks_manager.py
Maintainer: Vintage Warhawk
Last Edit: 2025-11-21
"""

class TaskManager:
	"""
	Manages scheduled tasks grouped by interval.

	Attributes:
		tasks (dict): A dictionary mapping interval names to lists of task instances.
	"""

	def __init__(self):
		"""
		Initialize the TaskManager with an empty task dictionary.
		"""
		self.tasks = {}

	def register_task(self, interval_name: str, name: str, task):
		"""
		Register a task under a specific interval.

		Args:
			interval_name (str): e.g., "hourly", "daily"
			name (str): task name for logs and identification
			task: instance with async run(client)
		"""
		self.tasks.setdefault(interval_name, {})[name] = task

	def get_tasks(self, interval_name: str):
		"""
		Retrieve all tasks registered under a specific interval.

		Args:
			interval_name (str): The interval name to fetch tasks for.

		Returns:
			dict: {task_name: task_instance}
		"""
		return self.tasks.get(interval_name, {})
