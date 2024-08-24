import os
from .BetterID import create_code_ipc
from Lib.config import Config, Color as color


os.makedirs(".secrets", exist_ok=True)
config_path = ".secrets/config.ini"
config = Config(config_path)
layout = ["General","Logger","General Embeds Colour","Welcome Settings","Advance", "AI_AllowedServers"]#, Admin Users]
config.set_layout(layout)
VERSION = "0.15"



configDataAndIamTryingToMakeItHardToReplaceItByAccidentAnywayHowAreYou = {
        "General": {
            "prefix"                    : "u.",
            "token"                     : "Your Bot Token",
            "Presence"                  : "My Master Mahiro",
            "SendToOwnerThatIsOnline"   : True,
            "owner"                     : 829806976702873621,
            "GuildTestingID"            : 1080951710828220537,
            "DisableAiClass"            : True,
            "ConfigVersion"             : VERSION
        },
        "Logger": {
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
            "IpcPassword":create_code_ipc()
        },
        "AI_AllowedServers":[
            12341234
        ]
    }

def create_comments(config: Config):
    config.create_comment("- <Server IDs>", "AI_AllowedServers",0)
    return config

try:
    config.load()
except FileNotFoundError:
    config.data = configDataAndIamTryingToMakeItHardToReplaceItByAccidentAnywayHowAreYou
    config= create_comments(config)
    config.save()

if config.data["General"]["ConfigVersion"] != VERSION:
    print("Config Version Mismatch")
    print("Backup Config File...")
    os.makedirs(".secrets/backup", exist_ok=True)
    os.rename(".secrets/config.ini", f".secrets/backup/config_{config["General"]["ConfigVersion"]}.ini")
    print("Backup Done")
    print("Creating New Config File...")
    for section in layout:
        if section not in config.data:
            config[section] = {}
        for key in configDataAndIamTryingToMakeItHardToReplaceItByAccidentAnywayHowAreYou[section]:
            if key not in config[section]:
                config.data[section][key] = configDataAndIamTryingToMakeItHardToReplaceItByAccidentAnywayHowAreYou[section][key]
    config= create_comments(config)
    config.data["General"]["ConfigVersion"] = VERSION
    config.save()

#General
token = config["General"]["token"]
prefix = config["General"]["prefix"]
Presence= config["General"]["Presence"]
send_to_owner_enabled = config["General"]["SendToOwnerThatIsOnline"]
owner_id = config["General"]["owner"]
TESTING_GUILD_ID = config["General"]["GuildTestingID"]
DisableAiClass = config["General"]["DisableAiClass"]

#Logger
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

#1274892436035993632
#Advance 
IpcPassword         = config["Advance"]["IpcPassword"]
AI_AllowedServers   = config["AI_AllowedServers"]