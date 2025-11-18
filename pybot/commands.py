"""
File: commands.py
Maintainer: Vintage Warhawk
Last Edit: 2025-11-17

Description:
This file contains all custom command classes for the Discord bot framework.
Commands are registered with a central HookManager instance. Each command
class must implement an asynchronous `run` method that handles the logic
when the command is invoked.
"""

from library.hook_manager import HookManager
from library.config_manager import SetConfig

# Create a HookManager instance for registering commands
manager = HookManager()

# -----------------------------
# Example Command: !test
# -----------------------------
class TestCommand:
    """
    Example command demonstrating argument handling.
    Usage: !test arg1 arg2 ...
    """
    async def run(self, message, args):
        """
        Runs when the !test command is invoked.
        - args[0] is the command itself.
        - args[1:] contains additional parameters provided by the user.
        """
        if len(args) < 2:
            await message.channel.send("No arguments provided!")
            return
        await message.channel.send(f"{message.author.name} ran !test with args: {args[1:]}")

# Register the !test command with the manager
manager.register_hook("!test", TestCommand())

# -----------------------------
# Example Command: !name
# -----------------------------
class NameCommand:
    """
    Command that echoes what the user typed.
    Usage: !name <message>
    """
    async def run(self, message, args):
        """
        Sends a message to the channel showing the user's name and the message.
        """
        await message.channel.send(f"{message.author.name} said: {' '.join(args[1:])}")

# Register the !name command
manager.register_hook("!name", NameCommand())

# -----------------------------
# Example Command: !home
# -----------------------------
class HomeCommand:
    """
    Command for admins to set the 'home' channel for the server.
    Usage: !home
    """
    async def run(self, message, args):
        """
        Saves the current channel as the home channel in the persistent config.
        Only users with administrator permissions can run this command.
        """
        if not message.author.guild_permissions.administrator:
            await message.channel.send("Only admins can set the home channel.")
            return

        # Store the channel ID for this guild in the config system
        SetConfig("home_channels", str(message.channel.id), guild_id=message.guild.id)
        print(f"\033[33m[Log] new home directory set: {message.channel.name} ({message.channel.id})\033[0m")
        await message.channel.send(f"This channel is now set as the home channel for this server!")

# Register the !home command
manager.register_hook("!home", HomeCommand())
