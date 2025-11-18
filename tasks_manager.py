class TaskManager:
    def __init__(self):
        self.tasks = {}  # {"hourly": [...], "daily": [...]}

    def register_task(self, interval_name: str, task):
        """Register a task under an interval (hourly, daily)"""
        self.tasks.setdefault(interval_name, []).append(task)

    def get_tasks(self, interval_name: str):
        return self.tasks.get(interval_name, [])
