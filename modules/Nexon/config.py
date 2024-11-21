import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from .BetterID import create_code_ipc
from modules.config import Config, Color as color
from rich import print as pprint

VERSION = "0.19"

@dataclass
class GeneralConfig:
    prefix: str = "u."
    token: str = "Your Bot Token"
    Presence: str = "My Master Mahiro"
    SendToOwnerThatIsOnline: bool = True
    DisableAiClass: bool = True
    ownerOverwrite: int = None
    ConfigVersion: str = VERSION

@dataclass
class LoggerConfig:
    Format: str = "%(asctime)s - %(levelname)s - %(name)s: %(message)s"
    logForAI: bool = False

@dataclass
class ColorConfig:
    Debug: color = field(default_factory=lambda: color(0x6a5acd))
    Info: color = field(default_factory=lambda: color(0xff69b4))
    Warn: color = field(default_factory=lambda: color(0xFFD700))
    Error: color = field(default_factory=lambda: color(0xB22222))

    def to_dict(self) -> Dict[str, str]:
        """Convert color values to hex strings for storage"""
        return {
            k: str(v) for k, v in self.__dict__.items()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ColorConfig':
        """Create ColorConfig from dictionary, handling hex strings"""
        processed_data = {}
        for key, value in data.items():
            if isinstance(value, (int, str)):
                processed_data[key] = color(value)
            elif isinstance(value, color):
                processed_data[key] = value
            else:
                raise ValueError(f"Invalid color value for {key}: {value}")
        return cls(**processed_data)


@dataclass
class WelcomeConfig:
    Enabled: bool = True
    baseImagePath: str = "Assets/img/Welcome.png"
    Font: str = "Assets/font/MonsterFriendFore.otf"
    BackupFont: str = "Assets/font/arial.ttf"
    SizeFont: int = 30
    Resize: tuple[int, int] = (99, 99)
    avatarPosition: tuple[int, int] = (47, 47)
    textPosition: tuple[int, int] = (190, 195)
    textColor_RGB: tuple[int, int, int] = (70, 243, 243)

@dataclass
class AdvanceConfig:
    IpcPassword: str = field(default_factory=create_code_ipc)
    IpcEnabled: bool = False
    IpcHost: str = 'localhost'
    IpcPort:int = 8765
    GuildTestingID: int = 1080951710828220537

@dataclass
class Bot_Config:
    General: GeneralConfig = field(default_factory=GeneralConfig)
    Logger: LoggerConfig = field(default_factory=LoggerConfig)
    General_Embeds_Colour: ColorConfig = field(default_factory=ColorConfig)
    Welcome_Settings: WelcomeConfig = field(default_factory=WelcomeConfig)
    Advance: AdvanceConfig = field(default_factory=AdvanceConfig)
    AI_AllowedServers: List[int] = field(default_factory=lambda: [12341234,43214321])
    AI_AllowedUsersID: List[int] = field(default_factory=lambda: [43214321,12341234])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the config to a dictionary format."""
        return {
            "General": {
                k: v for k, v in self.General.__dict__.items()
            },
            "Logger": {
                k: v for k, v in self.Logger.__dict__.items()
            },
            "General Embeds Colour": self.General_Embeds_Colour.to_dict(),
            "Welcome Settings": {
                k: v for k, v in self.Welcome_Settings.__dict__.items()
            },
            "Advance": {
                k: v for k, v in self.Advance.__dict__.items()
            },
            "AI_AllowedServers": self.AI_AllowedServers,
            "AI_AllowedUsersID": self.AI_AllowedUsersID
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Bot_Config':
        """Create a Bot_Config instance from a dictionary."""
        return cls(
            General=GeneralConfig(**data.get("General", {})),
            Logger=LoggerConfig(**data.get("Logger", {})),
            General_Embeds_Colour=ColorConfig.from_dict(data.get("General Embeds Colour", {})),
            Welcome_Settings=WelcomeConfig(**data.get("Welcome Settings", {})),
            Advance=AdvanceConfig(**data.get("Advance", {})),
            AI_AllowedServers=data.get("AI_AllowedServers", []),
            AI_AllowedUsersID=data.get("AI_AllowedUsersID", [])
        )

@dataclass
class ConfigManager:
    config_path: str
    backup_folder: str = ".secrets/backup"
    
    def __post_init__(self) -> None:
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        os.makedirs(self.backup_folder, exist_ok=True)
        self.config = Config(self.config_path)
        self.layout = [
            "General",
            "Logger",
            "General Embeds Colour",
            "Welcome Settings",
            "Advance",
            "AI_AllowedServers",
            "AI_AllowedUsersID"
        ]
        self.config.set_layout(self.layout)
        self.BotConfig: Optional[Bot_Config] = None
    
    def create_backup(self) -> str:
        """Create a backup of the current config file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        current_version = self.config.data.get("General", {}).get("ConfigVersion", "unknown")
        backup_filename = f"config_{current_version}_{timestamp}.ini"
        backup_path = os.path.join(self.backup_folder, backup_filename)
        
        try:
            if os.path.exists(self.config.filepath):
                with open(self.config.filepath, 'r') as source:
                    with open(backup_path, 'w') as target:
                        target.write(source.read())
            return backup_path
        except Exception as e:
            raise Exception(f"Failed to create backup: {str(e)}")
    
    def update_config(self, new_config: Bot_Config) -> None:
        """Update the configuration while preserving existing values."""
        backup_path = self.create_backup()
        backup_data = self.config.data.copy()
        
        try:
            # Convert new config to dict format
            new_data = new_config.to_dict()
            
            # Update existing config data
            for section in self.layout:
                if section not in new_data:
                    continue
                
                if isinstance(new_data[section], list):
                    if section in self.config.data and isinstance(self.config.data[section], list):
                        continue  # Preserve existing list
                    self.config.data[section] = new_data[section].copy()
                    continue
                
                if section not in self.config.data:
                    self.config.data[section] = {}
                
                for key, default_value in new_data[section].items():
                    if section not in self.config.data or key not in self.config.data[section]:
                        self.config.data[section][key] = default_value
            self.config.data[self.layout[0]]["ConfigVersion"] = VERSION
            
            # Update BotConfig with the merged data
            temp = Bot_Config.from_dict(self.config.data)
            self.config.data = temp.to_dict()
            del temp
            
            self.BotConfig = Bot_Config.from_dict(self.config.data)
            self.config.save()
            
        except Exception as e:
            # Restore from backup on failure
            self.config.data = backup_data
            try:
                if os.path.exists(backup_path):
                    with open(backup_path, 'r') as source:
                        with open(self.config.filepath, 'w') as target:
                            target.write(source.read())
                    pprint("Config restored from backup due to save failure")
            except Exception as restore_error:
                pprint(f"Failed to restore from backup: {str(restore_error)}")
            raise Exception(f"Failed to save updated config: {str(e)}")

def initialize_config() -> ConfigManager:
    """Initialize the configuration system."""
    config_manager = ConfigManager(".secrets/config.ini")
    
    try:
        config_manager.config.load()
        current_version = config_manager.config.data.get("General", {}).get("ConfigVersion")
        
        # Create default config
        default_config = Bot_Config()
        
        # Check if config exists and version matches
        if not current_version or current_version != VERSION:
            pprint(f"Updating config from version {current_version} to {VERSION}")
            default_config.General.ConfigVersion = VERSION
            config_manager.update_config(default_config)
            
        # Load the config into Bot_Config instance
        config_manager.BotConfig = Bot_Config.from_dict(config_manager.config.data)
            
    except FileNotFoundError:
        # Create new config with defaults
        default_config = Bot_Config()
        config_manager.config.data = default_config.to_dict()
        config_manager.BotConfig = default_config
        config_manager.config.save()
    
    return config_manager

# Initialize and export configuration
config_manager = initialize_config()
config = config_manager.config
BotConfig = config_manager.BotConfig

# Export configuration values
token = BotConfig.General.token
prefix = BotConfig.General.prefix
Presence = BotConfig.General.Presence
send_to_owner_enabled = BotConfig.General.SendToOwnerThatIsOnline
DisableAiClass = BotConfig.General.DisableAiClass
overwriteOwner = BotConfig.General.ownerOverwrite

Format = BotConfig.Logger.Format
logForAI = BotConfig.Logger.logForAI

# Colors/Colours
for color_type in ["Debug", "Info", "Warn", "Error"]:
    color_value = getattr(BotConfig.General_Embeds_Colour, color_type)
    globals()[f"{color_type}_Color"] = color_value
    globals()[f"{color_type}_Colour"] = color_value

# Welcome Settings
Welcome_enabled = BotConfig.Welcome_Settings.Enabled
baseImagePath = BotConfig.Welcome_Settings.baseImagePath
Font = BotConfig.Welcome_Settings.Font
BackupFont = BotConfig.Welcome_Settings.BackupFont
SizeFont = BotConfig.Welcome_Settings.SizeFont
Resize = BotConfig.Welcome_Settings.Resize
avatarPosition = BotConfig.Welcome_Settings.avatarPosition
textPosition = BotConfig.Welcome_Settings.textPosition
textColor = BotConfig.Welcome_Settings.textColor_RGB

# Advanced Settings
IpcPassword = BotConfig.Advance.IpcPassword
IpcEnabled= BotConfig.Advance.IpcEnabled
IpcHost= BotConfig.Advance.IpcHost
IpcPort= BotConfig.Advance.IpcPort
TESTING_GUILD_ID = BotConfig.Advance.GuildTestingID
AI_AllowedServers = BotConfig.AI_AllowedServers
AI_AllowedUsersID = BotConfig.AI_AllowedUsersID