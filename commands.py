from hook_manager import HookManager
from config import SetConfig

manager = HookManager()

# Example command: !test
class TestCommand:
    async def run(self, message, args):
        # args[0] is the command itself, args[1:] are the actual parameters
        if len(args) < 2:
            await message.channel.send("No arguments provided!")
            return
        await message.channel.send(f"{message.author.name} ran !test with args: {args[1:]}")

manager.register_hook("!test", TestCommand())

# Example command: !name
class NameCommand:
    async def run(self, message, args):
        await message.channel.send(f"{message.author.name} said: {' '.join(args[1:])}")

manager.register_hook("!name", NameCommand())

# Example command: !home
class HomeCommand:
    async def run(self, message, args):
        if not message.author.guild_permissions.administrator:
            await message.channel.send("Only admins can set the home channel.")
            return

        SetConfig("home_channels", str(message.channel.id), guild_id=message.guild.id)
        await message.channel.send(f"This channel is now set as the home channel for this server!")

manager.register_hook("!home", HomeCommand())
