"""
This Is Fun Lib
~~~~~~~~~~~~~~~
"""
import os
from .config import Config
from .richer import print
os.makedirs(".secrets", exist_ok=True)
config = Config(".secrets/config.conf")
layout = ["General","Logger"]#, "Database", "APIs"]
config.set_layout(layout)

VERSION = "0.0.4"

data = {
        "General": {
            "prefix": "ur.",
            "token": "Your Bot Token",
            "SendToOwnerThatIsOnline": True,
            "owner": 829806976702873621,
            "GuildTestingID": 1080951710828220537,
            "ConfigVersion": VERSION
        },
        "Logger": {
            "log": False,
            "Format": '%(asctime)s - %(levelname)s - %(message)s'
        },
    }



try:
    config.load()
except FileNotFoundError:
    config.data = data
    config.save()

if config.data["General"]["ConfigVersion"] != VERSION:
    print("Config Version Mismatch")
    print("Backup Config File...")
    os.makedirs(".secrets/backup", exist_ok=True)
    os.rename(".secrets/config.conf", f".secrets/backup/config_{config["General"]["ConfigVersion"]}.conf")
    print("Backup Done")
    print("Creating New Config File...")
    for section in layout:
        if section not in config.data:
            config[section] = {}
        for key in data[section]:
            if key not in config[section]:
                config.data[section][key] = data[section][key]
    config.data["General"]["ConfigVersion"] = VERSION
    config.save()


token = config["General"]["token"]
prefix = config["General"]["prefix"]
send_to_owner_enabled = config["General"]["SendToOwnerThatIsOnline"]
owner_id = config["General"]["owner"]
TESTING_GUILD_ID = config["General"]["GuildTestingID"]

Logger_Enabled = config["Logger"]["log"]
Format = config["Logger"]["Format"]



line = "____________________________________________________________________"

def clear():
    os.system("cls" if os.name == "nt" else "clear")