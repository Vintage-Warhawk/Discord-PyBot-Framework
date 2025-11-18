"""
File: config.py
Maintainer: Vintage Warhawk
Last Edit: 2025-11-17

Description:
This file provides a simple JSON-based configuration system for the Discord bot.
It allows storing and retrieving persistent data per server (guild) or globally.
Includes GetConfig and SetConfig classes for reading and writing configuration entries.
"""

import json
import os

# The JSON file that stores all persistent configuration data
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.abspath(os.path.join(BASE_DIR, "..", "data", "data.json"))

class Config:
    """
    Base configuration class.
    Handles reading from and writing to the JSON config file.
    """

    def __init__(self):
        """
        Initializes the config file if it does not exist.
        """
        if not os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "w") as f:
                json.dump({}, f)

    def _load(self):
        """
        Loads and returns the full configuration data as a dictionary.
        """
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)

    def _save(self, data):
        """
        Saves the provided dictionary to the config file with formatting.
        """
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f, indent=4)

# -----------------------------
# Read configuration values
# -----------------------------
class GetConfig(Config):
    """
    Retrieves configuration values from the JSON file.
    Supports optional per-guild (server) scoping.
    """

    def __init__(self, key, guild_id=None):
        """
        Args:
            key (str): The configuration key to retrieve.
            guild_id (str|int, optional): Guild ID for per-server values.
        """
        super().__init__()
        self.key = key
        self.guild_id = str(guild_id) if guild_id else None

    def value(self):
        """
        Returns the stored value for the key (and guild if provided).
        """
        data = self._load()
        if self.guild_id:
            return data.get(self.key, {}).get(self.guild_id)
        return data.get(self.key)

# -----------------------------
# Write configuration values
# -----------------------------
class SetConfig(Config):
    """
    Stores configuration values in the JSON file.
    Supports optional per-guild (server) scoping.
    """

    def __init__(self, key, value, guild_id=None):
        """
        Args:
            key (str): The configuration key to set.
            value (any): The value to store.
            guild_id (str|int, optional): Guild ID for per-server values.
        """
        super().__init__()
        self.key = key
        self.value = value
        self.guild_id = str(guild_id) if guild_id else None
        self.save()

    def save(self):
        """
        Saves the value to the config file, either globally or per-guild.
        """
        data = self._load()
        if self.guild_id:
            if self.key not in data:
                data[self.key] = {}
            data[self.key][self.guild_id] = self.value
        else:
            data[self.key] = self.value
        self._save(data)
