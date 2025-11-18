"""
File: tasks_manager.py
Maintainer: Vintage Warhawk
Last Edit: 2025-11-17

Description:
This file defines the TaskManager class, which manages scheduled tasks for the
Discord bot framework. Tasks are grouped by interval names (e.g., "hourly", "daily", "test").
The manager allows registration of task classes and retrieval of tasks for execution.
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
        self.tasks = {}  # {"hourly": [...], "daily": [...]}

    def register_task(self, interval_name: str, task):
        """
        Register a task under a specific interval.

        Args:
            interval_name (str): The interval name, e.g., "hourly", "daily", "test".
            task: An instance of a class implementing an async `run(client)` method.
        """
        self.tasks.setdefault(interval_name, []).append(task)

    def get_tasks(self, interval_name: str):
        """
        Retrieve all tasks registered under a specific interval.

        Args:
            interval_name (str): The interval name to fetch tasks for.

        Returns:
            list: A list of task instances for the given interval.
        """
        return self.tasks.get(interval_name, [])
