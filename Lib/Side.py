"""
This Is Fun Lib
~~~~~~~~~~~~~~~
"""
#TODO: please Change the Id of the owner and the guild id after publish so that no one can use it by mistake
import os
import random
import string
from .config import Config, Color as color
from .richer import print
from .Data import DataGlobal as GlobalData
from nextcord import Embed
import re
from typing import Any, Dict, Iterator, List, Union
from datetime import timedelta
os.makedirs(".secrets", exist_ok=True)
config_path = ".secrets/config.conf"
config = Config(config_path)
layout = ["General","Logger","General Embeds Colour","Advance"]#, "Database", "APIs"]
config.set_layout(layout)

VERSION = "0.0.8"

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
        "General Embeds Colour": {
            "Debug" : color(0x00FF00),
            "Info"  : color(0x1E90FF),
            "Warn"  : color(0xFFD700),
            "Error" : color(0xB22222)
        },
        "Advance": {
            "DefaultBetterID_MaxNumber": 7,
            "AllowOtherCoreExtension": False,
        }
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

#US
Debug_Color = color(config["General Embeds Colour"]["Debug"]).value
Info_Color  = color(config["General Embeds Colour"]["Info"]).value
Warn_Color  = color(config["General Embeds Colour"]["Warn"]).value
Error_Color = color(config["General Embeds Colour"]["Error"]).value
#UK
Debug_Colour = color(config["General Embeds Colour"]["Debug"]).value
Info_Colour  = color(config["General Embeds Colour"]["Info"]).value
Warn_Colour  = color(config["General Embeds Colour"]["Warn"]).value
Error_Colour = color(config["General Embeds Colour"]["Error"]).value

#Advance 
maxNum = config["Advance"]["DefaultBetterID_MaxNumber"]
AllowOtherCoreExtension = config["Advance"]["AllowOtherCoreExtension"]


def clear():
    os.system("cls" if os.name == "nt" else "clear")

def debug_embed(description:str,title:str="Debug"):
    return Embed(title=title,description=description,color=Debug_Color)

def info_embed(description:str,title:str="Info"):
    return Embed(title=title,description=description,color=Info_Color)

def warn_embed(description:str,title:str="Warn"):
    return Embed(title=title,description=description,color=Warn_Color)

def error_embed(description:str,title:str="Error"):
    return Embed(title=title,description=description,color=Error_Color)


# Dictionary to convert words to numbers
word_to_number = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
    "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
    "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
    "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60,
    "seventy": 70, "eighty": 80, "ninety": 90,"hundred":100
}

# Dictionary to convert time units to seconds
time_units = {
    "s"     : 1 ,       'sec'   : 1,     'second'   : 1,    'seconds'   : 1,
    "m"     : 60 ,      'min'   : 60,    'minute'   : 60,   'minutes'   : 60,
    'h'     : 3600,     'hour'  : 3600,  'hours'    : 3600,
    'd'     : 86400,    'day'   : 86400, 'days'     : 86400,
    'w'     : 604800,   'week'  : 604800,'weeks'    : 604800,
    'month' : 2592000,  'months': 2592000  # Assuming 1 month = 30 days
}

def text_to_number(text):
    text = text.lower().strip()
    if text.isdigit():  # Direct number
        return int(text)
    return word_to_number.get(text, None)

def convert_to_seconds(time_string):
    time_string = time_string.lower()
    
    # Regex to find patterns like '5 days', 'five days', '5d', etc.
    pattern = r'(\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred)\s*(s|sec|second|seconds|m|min|minute|minutes|h|hour|hours|d|day|days|w|week|weeks|month|months)?'
    match = re.match(pattern, time_string)
    
    if match:
        number_text, unit = match.groups()
        number = text_to_number(number_text) if not number_text.isdigit() else int(number_text)
        unit = unit if unit else 'sec'  # Default to seconds if no unit is provided

        if number is None or unit not in time_units:
            raise ValueError(f"Invalid time format: {time_string}")
        
        return number * time_units[unit]
    else:
        raise ValueError(f"Invalid time format: {time_string}")
    

class BetterID:
    def __init__(self,max:int = maxNum):
        self.max = max
        self.file = GlobalData("","BetterID")
        try:
            self.data = self.file.load()
        except FileNotFoundError:
            self.data = []
            self.file.data = self.data
            self.file.save()
    def create_random_id(self) -> str:
        characters = string.ascii_lowercase + string.digits  # lowercase letters + digits
        code = ''.join(random.choice(characters) for _ in range(self.max))
        for i in self.data:
            if code == i:
                return self.create_random_id()
        else:
            self.data.append(code)
            self.file.data = self.data
            self.file.save()
            return code
        
    def check_id(self,code) -> bool:
        for i in self.data:
            if code == i:
                return False
        else:
            return True

    def __getitem__(self, key: str) -> Union[Dict[str, Any], List[Any]]:
        if key in self.data:
            try:
                return self.data[key]
            except KeyError:
                return None
        else:
            raise KeyError(f"'{key}' not found in the data")
    
    def __setitem__(self, key: str, value: Any) -> None:
        self.data[key] = value

    def __delitem__(self, key: str) -> None:
        del self.data[key]

    def __iter__(self) -> Iterator:
        return iter(self.data)

    def __len__(self) -> int:
        return len(self.data)

    def __repr__(self) -> str:
        return f"{self.data}"
    
    def __str__(self) -> str:
        return f"{self.data}"

    def __contains__(self, key: str) -> bool:
        return key in self.data

    def __eq__(self, other: Any) -> bool:
        return self.data == other

    def __ne__(self, other: Any) -> bool:
        return self.data != other

    def __add__(self, other: Any) -> Any:
        return self.data + other

    def __sub__(self, other: Any) -> Any:
        return self.data - other

    def __mul__(self, other: Any) -> Any:
        return self.data * other

    def __floordiv__(self, other: Any) -> Any:
        return self.data // other

    def __mod__(self, other: Any) -> Any:
        return self.data % other

    def __divmod__(self, other: Any) -> Any:
        return divmod(self.data, other)

    def __pow__(self, other: Any) -> Any:
        return self.data ** other

    def __lshift__(self, other: Any) -> Any:
        return self.data << other
        
