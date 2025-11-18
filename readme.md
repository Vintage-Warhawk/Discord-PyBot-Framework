# Discord PyBot Framework

This is a Python-based Discord bot framework that supports:

- Custom commands
- Custom scheduled tasks (hourly/daily)
- Per-server configuration with persistent storage
- Cross-platform build scripts (`build.bat` for Windows, `build.sh` for Linux)

## Table of Contents

1. Requirements
2. Building the Bot
3. Running the Bot
4. Creating Custom Commands
5. Creating Custom Tasks
6. Data System / Config

## Requirements

- Docker installed and running on your machine
- Discord Bot Token

Python dependencies are installed automatically via Docker.

## Building the Bot

### Windows

Run the build script:

```
build.bat
```

Enter your Discord token when prompted.
Confirm to continue.
The bot will be built and started using Docker Compose.

### Linux / macOS

Run the shell build script:

```
./build.sh
```

Enter your Discord token.
Confirm to continue.
The bot will be built and started using Docker Compose.

Make sure `build.sh` is executable:

```
chmod +x build.sh
```

## Running the Bot

After building, the bot runs inside Docker. To restart:

```
docker compose up -d
```

To stop the bot:

```
docker compose down
```

The Discord token is passed to the container as an environment variable.

This bot can run on any machine with Docker installed.

## Creating Custom Commands

Commands are defined in `commands.py` or additional files.

### Example Command

```
from hook_manager import HookManager

manager = HookManager()

class HelloCommand:
    async def run(self, message, args):
        await message.channel.send(f"Hello {message.author.name}!")

manager.register_hook("!hello", HelloCommand())
```

Trigger: `!hello` — users type this to invoke the command.
Arguments: `args` is a list of arguments after the trigger.

Example:

```
!hello arg1 arg2
# args = ["arg1", "arg2"]
```

## Creating Custom Tasks

Tasks are defined in `tasks.py` and registered with `tasks_manager.py`.

### Example Task

```
from tasks_manager import TaskManager

manager = TaskManager()

class HourlyTask:
    async def run(self, client):
        for guild in client.guilds:
            channel = guild.text_channels[0]
            await channel.send("Hourly task executed!")

manager.register_task("hourly", HourlyTask())
```

Supported intervals: `hourly` and `daily`.
The bot runs tasks automatically on the schedule:
Hourly: every full hour.
Daily: at 12:00 noon (timezone-aware).
A `test` task loop can be added to run every 10 seconds for development.

## Data System / Config

The bot uses a persistent JSON-based config (`data.json`) to store server-specific data.

### SetConfig

```
from config import SetConfig

SetConfig("home_channels", str(message.channel.id), guild_id=message.guild.id)
```

### GetConfig

```
from config import GetConfig

home_channel_id = GetConfig("home_channels", guild_id=message.guild.id).value()
```

Supports per-guild settings using `guild_id`.
Can store home channels or other persistent bot settings.
Data is stored in `data.json` and persisted in Docker.

## Notes

Ensure the bot has message content intent enabled in the Discord Developer Portal.
Tasks and commands are modular and can be extended by creating new classes and registering them with the manager.
Review all code changes before committing to the repository.

