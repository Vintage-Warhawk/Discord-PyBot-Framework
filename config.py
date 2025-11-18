import json
import os

CONFIG_FILE = "data.json"

class Config:
    def __init__(self):
        if not os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "w") as f:
                json.dump({}, f)

    def _load(self):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)

    def _save(self, data):
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f, indent=4)

class GetConfig(Config):
    def __init__(self, key, guild_id=None):
        super().__init__()
        self.key = key
        self.guild_id = str(guild_id) if guild_id else None

    def value(self):
        data = self._load()
        if self.guild_id:
            return data.get(self.key, {}).get(self.guild_id)
        return data.get(self.key)

class SetConfig(Config):
    def __init__(self, key, value, guild_id=None):
        super().__init__()
        self.key = key
        self.value = value
        self.guild_id = str(guild_id) if guild_id else None
        self.save()

    def save(self):
        data = self._load()
        if self.guild_id:
            if self.key not in data:
                data[self.key] = {}
            data[self.key][self.guild_id] = self.value
        else:
            data[self.key] = self.value
        self._save(data)
