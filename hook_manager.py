# hook_manager.py
class HookManager:
    def __init__(self):
        self.hooks = {}

    def register_hook(self, trigger: str, handler):
        """Register a command trigger with a handler class"""
        self.hooks[trigger.lower()] = handler

    async def handle_message(self, message):
        """Handle incoming messages and dispatch to the proper hook"""
        if not message.content:
            return

        parts = message.content.strip().split()
        if not parts:
            return

        trigger = parts[0].lower()      # "!command"
        args = parts                      # full array including the trigger

        if trigger in self.hooks:
            handler = self.hooks[trigger]
            await handler.run(message, args)
