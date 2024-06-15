"""
This Is Fun Lib
~~~~~~~~~~~~~~~
"""
import os
from .config import Config

config = Config("secrets/config.conf")
layout = ["General","Logger", "Database", "APIs"]
config.set_layout(layout)
try:
    config.load()
except FileNotFoundError:
    config.data = {
        "General": {
            "prefix": "ur.",
            "token": "Your Bot Token",
            "owner": 829806976702873621,
            "Guild Testing ID": 1080951710828220537
        },
        "Logger": {
            "log": False,
            "log_channel": 0
        },
    }
    config.save()

token = config.data["General"]["token"]
prefix = config.data["General"]["prefix"]
owner_id = config.data["General"]["owner"]
TESTING_GUILD_ID = config.data["General"]["Guild Testing ID"]

Logger_Enabled = config.data["Logger"]["log"]

line = "____________________________________________________________________"

def clear():
    os.system("cls" if os.name == "nt" else "clear")