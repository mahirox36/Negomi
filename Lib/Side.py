"""
Side Library for small and big functions and classes for Nextcord
~~~~~~~~~~~~~~~
"""
#TODO: please Change the Id of the owner and the guild id after publish so that no one can use it by mistake
import json
import os
import random
import shutil
import string

import nextcord
from .config import Config, Color as color
from rich import print
from nextcord import Embed, Guild, Member, PermissionOverwrite, Interaction as init, Permissions
from nextcord.ext import commands
from nextcord.ext.application_checks import check
from nextcord.errors import ApplicationCheckFailure
import re
from typing import Any, Dict, List, Optional, Union, NewType, Callable
import time
os.makedirs(".secrets", exist_ok=True)
config_path = ".secrets/config.ini"
config = Config(config_path)
layout = ["General","Logger","General Embeds Colour","Welcome Settings","Advance"]#, Admin Users]
config.set_layout(layout)
#TODO: next 0.12
VERSION = "0.11"

configDataAndIamTryingToMakeItHardToReplaceItByAccidentAnywayHowAreYou = {
        "General": {
            "prefix"                    : "u.",
            "token"                     : "Your Bot Token",
            "SendToOwnerThatIsOnline"   : True,
            "owner"                     : 829806976702873621,
            "GuildTestingID"            : 1080951710828220537,
            "DisableAiClass"            : True,
            "ConfigVersion"             : VERSION
        },
        "Logger": {
            "log"       : False,
            "Format"    : "%(asctime)s - %(levelname)s - %(name)s: %(message)s",
            "logForAI"  : False
        },
        "General Embeds Colour": {
            "Debug" : color(0x00FF00),
            "Info"  : color(0x1E90FF),
            "Warn"  : color(0xFFD700),
            "Error" : color(0xB22222)
        },
        "Welcome Settings":{
            "Enabled"       : True,
            "baseImagePath" : "Assets/img/Welcome.png",
            "Font"          : "Assets/font/MonsterFriendFore.otf",
            "BackupFont"    : "Assets/font/arial.ttf",
            "SizeFont"      : 30,
            "Resize"        : (99, 99),
            "avatarPosition": (47, 47),
            "textPosition"  : (190, 195),
            "textColor_RGB" : (70, 243, 243) 
            
        },
        "Advance": {
            "DefaultBetterID_MaxNumber": 7
        }
    }



try:
    config.load()
except FileNotFoundError:
    config.data = configDataAndIamTryingToMakeItHardToReplaceItByAccidentAnywayHowAreYou
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
        for key in configDataAndIamTryingToMakeItHardToReplaceItByAccidentAnywayHowAreYou[section]:
            if key not in config[section]:
                config.data[section][key] = configDataAndIamTryingToMakeItHardToReplaceItByAccidentAnywayHowAreYou[section][key]
    config.data["General"]["ConfigVersion"] = VERSION
    config.save()

#General
token = config["General"]["token"]
prefix = config["General"]["prefix"]
send_to_owner_enabled = config["General"]["SendToOwnerThatIsOnline"]
owner_id = config["General"]["owner"]
TESTING_GUILD_ID = config["General"]["GuildTestingID"]
DisableAiClass = config["General"]["DisableAiClass"]

#Logger
Logger_Enabled = config["Logger"]["log"]
Format = config["Logger"]["Format"]
logForAI = config["Logger"]["logForAI"]

#US Color
Debug_Color = color(config["General Embeds Colour"]["Debug"]).value
Info_Color  = color(config["General Embeds Colour"]["Info"]).value
Warn_Color  = color(config["General Embeds Colour"]["Warn"]).value
Error_Color = color(config["General Embeds Colour"]["Error"]).value
#UK Colour
Debug_Colour = color(config["General Embeds Colour"]["Debug"]).value
Info_Colour  = color(config["General Embeds Colour"]["Info"]).value
Warn_Colour  = color(config["General Embeds Colour"]["Warn"]).value
Error_Colour = color(config["General Embeds Colour"]["Error"]).value

#Welcome Settings
Welcome_enabled = config["Welcome Settings"]["Enabled"]
baseImagePath   = config["Welcome Settings"]["baseImagePath"]
Font            = config["Welcome Settings"]["Font"]
BackupFont      = config["Welcome Settings"]["BackupFont"]
SizeFont        = config["Welcome Settings"]["SizeFont"]
Resize          = config["Welcome Settings"]["Resize"]
avatarPosition  = config["Welcome Settings"]["avatarPosition"]
textPosition    = config["Welcome Settings"]["textPosition"]
textColor       = config["Welcome Settings"]["textColor_RGB"]

#Advance 
maxNum = config["Advance"]["DefaultBetterID_MaxNumber"]


#New Types:
url = NewType("url", str)


def PermissionOverwriteWith(create_instant_invite: Optional[bool]= None,kick_members: Optional[bool]= None,ban_members: Optional[bool]= None,administrator: Optional[bool]= None,manage_channels: Optional[bool]= None,manage_guild: Optional[bool]= None,add_reactions: Optional[bool]= None,view_audit_log: Optional[bool]= None,priority_speaker: Optional[bool]= None,stream: Optional[bool]= None,read_messages: Optional[bool]= None,view_channel: Optional[bool]= None,send_messages: Optional[bool]= None,send_tts_messages: Optional[bool]= None,manage_messages: Optional[bool]= None,embed_links: Optional[bool]= None,attach_files: Optional[bool]= None,read_message_history: Optional[bool]= None,mention_everyone: Optional[bool]= None,external_emojis: Optional[bool]= None,use_external_emojis: Optional[bool]= None,view_guild_insights: Optional[bool]= None,connect: Optional[bool]= None,speak: Optional[bool]= None,mute_members: Optional[bool]= None,deafen_members: Optional[bool]= None,move_members: Optional[bool]= None,use_voice_activation: Optional[bool]= None,change_nickname: Optional[bool]= None,manage_nicknames: Optional[bool]= None,manage_roles: Optional[bool]= None,manage_permissions: Optional[bool]= None,manage_webhooks: Optional[bool]= None,manage_emojis: Optional[bool]= None,manage_emojis_and_stickers: Optional[bool]= None,use_slash_commands: Optional[bool]= None,request_to_speak: Optional[bool]= None,manage_events: Optional[bool]= None,manage_threads: Optional[bool]= None,create_public_threads: Optional[bool]= None,create_private_threads: Optional[bool]= None,send_messages_in_threads: Optional[bool]= None,external_stickers: Optional[bool]= None,use_external_stickers: Optional[bool]= None,start_embedded_activities: Optional[bool]= None,moderate_members: Optional[bool]= None):
    return PermissionOverwrite(create_instant_invite= create_instant_invite,kick_members= kick_members,ban_members= ban_members,administrator= administrator,manage_channels= manage_channels,manage_guild= manage_guild,add_reactions= add_reactions,view_audit_log= view_audit_log,priority_speaker= priority_speaker,stream= stream,read_messages= read_messages,view_channel= view_channel,send_messages= send_messages,send_tts_messages= send_tts_messages,manage_messages= manage_messages,embed_links= embed_links,attach_files= attach_files,read_message_history= read_message_history,mention_everyone= mention_everyone,external_emojis= external_emojis,use_external_emojis= use_external_emojis,view_guild_insights= view_guild_insights,connect= connect,speak= speak,mute_members= mute_members,deafen_members= deafen_members,move_members= move_members,use_voice_activation= use_voice_activation,change_nickname= change_nickname,manage_nicknames= manage_nicknames,manage_roles= manage_roles,manage_permissions= manage_permissions,manage_webhooks= manage_webhooks,manage_emojis= manage_emojis,manage_emojis_and_stickers= manage_emojis_and_stickers,use_slash_commands= use_slash_commands,request_to_speak= request_to_speak,manage_events= manage_events,manage_threads= manage_threads,create_public_threads= create_public_threads,create_private_threads= create_private_threads,send_messages_in_threads= send_messages_in_threads,external_stickers= external_stickers,use_external_stickers= use_external_stickers,start_embedded_activities= start_embedded_activities,moderate_members= moderate_members)
    

def get_name(user:Member):
    return user.global_name if user.global_name != None else user.display_name

def everyone(guild:Guild):
    return guild.default_role

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def debug_embed(
    description: str = None,
    title: str = "Debug",
    footer: str = None,
    author: List[Union[str, url]] = None
) -> Embed:
    embed =Embed(title=title,description=description,color=Debug_Color)
    if footer: embed.set_footer(text=footer)
    if author != None: embed.set_author(name=author[0],icon_url=author[1])
    return embed

def info_embed(
    description: str = None,
    title: str = "Info",
    footer: str = None,
    author: List[Union[str, url]] = None
) -> Embed:
    embed =Embed(title=title,description=description,color=Info_Colour)
    if footer: embed.set_footer(text=footer)
    if author != None: embed.set_author(name=author[0],icon_url=author[1])
    return embed

def warn_embed(
    description: str = None,
    title: str = "Warn",
    footer: str = None,
    author: List[Union[str, url]] = None
) -> Embed:
    embed =Embed(title=title,description=description,color=Warn_Colour)
    if footer: embed.set_footer(text=footer)
    if author != None: embed.set_author(name=author[0],icon_url=author[1])
    embed.set_author
    return embed

def error_embed(
    description: str = None,
    title: str = "Error",
    footer: str = None,
    author: List[Union[str, url]] = None
) -> Embed:
    embed =Embed(title=title,description=description,color=Error_Colour)
    if footer: embed.set_footer(text=footer)
    if author != None: embed.set_author(name=author[0],icon_url=author[1])
    return embed

def remove_prefix(s, prefix):
    if s.startswith(prefix):
        return s[len(prefix):]
    return s

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

def text_to_number(text: str):
    text = text.lower().strip()
    if text.isdigit():  # Direct number
        return int(text)
    return word_to_number.get(text, None)

def convert_to_seconds(time_string: str):
    """Convert any time to seconds

    Args:
        time_string (str): Time

    Raises:
        ValueError: Invalid time Format 
        ValueError: _description_

    Returns:
        int: Seconds
    """
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
    



        

class SlashCommandOnCooldown(ApplicationCheckFailure):
    def __init__(self, time_left: float):
        self.time_left = time_left
        super().__init__(f"Command is on cooldown. Try again in {time_left:.2f} seconds.")

def setup_hybrid(bot: commands.Bot):
    """
    Register commands on the bot instance.
    """
    def hybrid(name: str, description: str, aliases: List[str] = [], **kwargs: Any):
        def decorator(func: Callable[..., Any]):
            # Register text command
            bot.add_command(commands.Command(func, name="_"+name, **kwargs))
            
            # Register slash command
            bot.slash_command(name=name, description=description)(func)
            
            return func
        return decorator
    
    return hybrid
    
def userCTX(ctx:init):
    try:
        ctx.user = ctx.author
    except:
        pass
    return ctx
def userCONTEXT(ctx:init):
    try:
        ctx.author = ctx.user
    except:
        pass
    return ctx

def create_random_id(data) -> int:
    code = random.randint(1,99999999999999)
    for i in data:
        if code == i:
            return create_random_id(data)
    else:
        return code
    
def check_id(data,code) -> bool:
    for i in data:
        if code == i:
            return False
    else:
        return True
    
    
class Data:
    def __init__(self,server_id:int, name:str,file:str="data",subFolder: str = None):
        self.path = f"Data/{name}/{server_id}" 
        self.file = f"{self.path}/{file}.json" if subFolder == None else f"{self.path}/{subFolder}/{file}.json"
        os.makedirs(self.path,exist_ok=True)
        if subFolder != None: os.makedirs(os.path.join(self.path, subFolder), exist_ok=True)
        
        try:
            self.load()
        except FileNotFoundError:
            self.data: Union[Dict, List, None] = None
    
    def save(self) -> None:
        with open(self.file, "w") as f:
            json.dump(self.data,f,indent=4)
    
    def load(self) -> Any:
        with open(self.file, "r") as f:
            self.data = json.load(f)
        return self.data
    
    def check(self) -> bool:
        if os.path.exists(self.file):
            return True
        return False
    
    def delete(self) -> None:
        os.remove(self.file)
    def delete_guild(self):
        shutil.rmtree(self.path)
    
    def __getitem__(self, key: str) -> Union[Dict[str, Any], List[Any]]:
        if key in self.data:
            try:
                return self.data[key]
            except KeyError:
                return None
        else:
            raise KeyError(f"'{key}' not found in the data")

    def __setitem__(self, key: str, value: Union[Dict[str, Any], List[Any]]) -> None:
        if key in self.data:
            self.data[key] = value
        else:
            raise KeyError(f"'{key}' not found in the data")

class DataGlobal:
    def __init__(self, name:str,file:str="data"):
        if name == ""   : self.path = f"Data/"
        else            : self.path = f"Data/{name}/"
        self.file = f"{self.path}{file}.json"
        os.makedirs(self.path,exist_ok=True)
        try:
            self.load()
        except FileNotFoundError:
            self.data: Union[Dict, List, None] = None
    
    def save(self):
        with open(self.file, "w") as f:
            json.dump(self.data,f)
        return self
    
    def load(self) -> Any:
        with open(self.file, "r") as f:
            self.data = json.load(f)
        return self.data
    
    def check(self) -> bool:
        if os.path.exists(self.file):
            return True
        return False
    
    def delete(self,code) -> None:
        del self.data[code]
        self.save()
        os.remove(self.file)
    def __getitem__(self, key: str) -> Union[Dict[str, Any], List[Any]]:
        if key in self.data:
            try:
                return self.data[key]
            except KeyError:
                return None
        else:
            raise KeyError(f"'{key}' not found in the data")

    def __setitem__(self, key: str, value: Union[Dict[str, Any], List[Any]]) -> None:
        if key in self.data:
            self.data[key] = value
        else:
            raise KeyError(f"'{key}' not found in the data")

async def high(ctx:init,user:Member):
    if user.top_role.position >= ctx.user.top_role.position:
        await ctx.send(f"User {user} Is Higher Than you")
        return True
    return False

class ApplicationNotOwnerGuild(ApplicationCheckFailure):
    def __init__(self,user:Member,guild:Guild) -> None:
        super().__init__()
        self.guild= guild.name
        self.user= get_name(user)

    
class BetterID:
    def __init__(self,max:int = maxNum):
        self.max = max
        self.file = DataGlobal("BetterID")
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


cooldowns= {}
def cooldown(cooldown_time: int):
    async def predicate(ctx: init) -> bool:
        global cooldowns
        name = ctx.application_command.name
        user_id = ctx.user.id

        if name not in cooldowns:
            cooldowns[name] = {}

        # Check if the user is on cooldown
        if user_id in cooldowns[name]:
            time_left = cooldowns[name][user_id] - time.time()
            if time_left > 0:
                raise SlashCommandOnCooldown(time_left)

        # Set a new cooldown for the user
        cooldowns[name][user_id] = time.time() + cooldown_time
        return True

    return check(predicate)

def is_owner_guild():
    async def predicate(ctx: init) -> bool:

        if not ctx.guild.owner.id == ctx.user.id:
            raise ApplicationNotOwnerGuild(ctx.user,ctx.guild)
        return True

    return check(predicate)

class PluginNotLoaded(commands.CheckFailure):
    def __init__(self, message: Optional[str] = None) -> None:
        super().__init__(message or "This command didn't get loaded in your server")

def plugin():
    def predicate(ctx) -> bool:
        file = Data(ctx.guild.id, "Plugins", "Applied Plugins")
        applied_plugins = file.data if file.data is not None else []
        if ctx.cog is None or ctx.cog.__cog_name__ not in applied_plugins:
            raise PluginNotLoaded(f"Plugin '{ctx.cog.__cog_name__}' is not loaded.")
        return True  # Check passed
    return commands.check(predicate)