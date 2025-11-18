"""
File: hook_manager.py
Maintainer: Vntage Warhawk
Last Edit: 2025-11-17

Description:
This file defines the HookManager class, which manages command hooks for the Discord bot.
It allows commands to be registered with triggers (like "!test") and handles incoming
messages by dispatching them to the appropriate command class.
"""

class HookManager:
    """
    Manages command hooks.

    Attributes:
        hooks (dict): Maps command triggers (lowercase) to their handler classes.
    """

    def __init__(self):
        """
        Initialize the hook manager with an empty hook dictionary.
        """
        self.hooks = {}

    def register_hook(self, trigger: str, handler):
        """
        Register a command trigger with a handler class.

        Args:
            trigger (str): The text trigger for the command (e.g., "!name").
            handler: An instance of a class implementing an async `run(message, args)` method.
        """
        self.hooks[trigger.lower()] = handler

    async def handle_message(self, message):
        """
        Handle incoming Discord messages and dispatch to the registered hook if found.

        Args:
            message (discord.Message): The message object from the Discord API.

        Notes:
            - The first word of the message is treated as the trigger.
            - All message words (including the trigger) are passed as `args` to the handler.
        """
        if not message.content:
            return

        parts = message.content.strip().split()
        if not parts:
            return

        trigger = parts[0].lower()  # Command trigger, e.g., "!test"
        args = parts                 # Full message split into parts

        if trigger in self.hooks:
            handler = self.hooks[trigger]
            print(f"\033[33m[Command]\033[32m {message.author.name}\033[0m Called command: \033[33m{args[0]}\033[0m")
            await handler.run(message, args)
