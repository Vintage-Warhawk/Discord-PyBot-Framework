<img width="1000" height="380" alt="PyBot_Logo_Dark" src="https://github.com/user-attachments/assets/ffd0e198-0554-4867-a59d-bf9d94c990ab" />

# Discord PyBot Framework
Version 2025.11.19-Experimental

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

## Platform Support Notice

This project uses the Docker image `python:3.12-slim`, which is Linux-based. As a result:

- **Windows:** Runs through Docker Desktop using the WSL2 backend (not natively).
- **Linux:** Runs natively through Docker.
- **macOS:** Runs through Docker Desktop, which uses an embedded Linux VM.

The bot does **not** run natively on Windows or macOS. It runs on any system that supports Docker’s Linux container environment.


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

Commands are defined in `pybot/commands.py` or additional files.

### Example Command

```
from library.command_manager import CommandManager

manager = CommandManager()

class HelloCommand:
    async def run(self, message, args):
        await message.channel.send(f"Hello {message.author.name}!")

manager.register_command("!hello", HelloCommand())
```

Trigger: `!hello` — users type this to invoke the command.
Arguments: `args` is a list of arguments after the trigger.

Example:

```
!hello arg1 arg2
# args = ["arg1", "arg2"]
```

## Creating Custom Tasks

Tasks are defined in `pybot/tasks.py` and registered with `library.tasks_manager.py`.

### Example Task

```
from library.tasks_manager import TaskManager

manager = TaskManager()

class HourlyTask:
    async def run(self, client):
        for guild in client.guilds:
            channel = guild.text_channels[0]
            await channel.send("Hourly task executed!")

manager.register_task("hourly", "Task_Name", HourlyTask())
```

Supported intervals: `hourly` and `daily`.
The bot runs tasks automatically on the schedule:
Hourly: every full hour.
Daily: at 12:00 noon (timezone-aware).
A `test` task loop can be added to run every 10 seconds for development.

## Data System / Config

The bot uses a persistent JSON-based config (`data/data.json`) to store server-specific data.

### SetConfig

```
from library.config_manager import SetConfig

SetConfig("home_channels", str(message.channel.id), guild_id=message.guild.id)
```

### GetConfig

```
from library.config_manager import GetConfig

home_channel_id = GetConfig("home_channels", guild_id=message.guild.id).value()
```

Supports per-guild settings using `guild_id`.
Can store home channels or other persistent bot settings.
Data is stored in `data/data.json` and persisted in Docker.

## Notes

Ensure the bot has message content intent enabled in the Discord Developer Portal.
Tasks and commands are modular and can be extended by creating new classes and registering them with the manager.

## License

This project is released under a non-commercial license. You can use, modify, distribute, or sublicense the code for **non-commercial purposes only**, and no attribution is required.

Commercial use or any use intended to generate profit is strictly prohibited.

See the [LICENSE](./LICENSE) file for full details.

<img width="1000" height="380" alt="PyBot_Branding" src="https://github.com/user-attachments/assets/1f931736-679a-40c8-bd48-95b9ea9ca0c0" />
