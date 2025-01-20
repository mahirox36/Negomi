import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from modules.config import Config, Color as color
from rich import print as pprint

VERSION = "0.26"

@dataclass
class GeneralConfig:
    prefix: str = "u."
    token: str = "Your Bot Token"
    presence : str = "My Master Mahiro"
    send_to_online_owner : bool = True
    owner_id : int = None
    ConfigVersion: str = VERSION

@dataclass
class LoggerConfig:
    format : str = "%(asctime)s - %(levelname)s - %(name)s: %(message)s"
    level : str = "Info"

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
    enabled : bool = True
    base_image_path : str = "Assets/img/Welcome.png"
    font : str = "Assets/font/MonsterFriendFore.otf"
    backup_font : str = "Assets/font/arial.ttf"
    font_size : int = 30
    resize_dimensions : tuple[int, int] = (99, 99)
    avatar_position : tuple[int, int] = (47, 47)
    text_position : tuple[int, int] = (190, 195)
    text_color_rgb : tuple[int, int, int] = (70, 243, 243)

@dataclass
class CommandsSettings:
    enable_advanced_viewing : bool = True

@dataclass
class AISettings:
    enable : bool = False
    ip: str = "127.0.0.1"
    allow_all_servers: bool = False
    allow_all_users: bool = False

@dataclass
class Bot_Config:
    General: GeneralConfig = field(default_factory=GeneralConfig)
    Logger: LoggerConfig = field(default_factory=LoggerConfig)
    General_Embeds_Colour: ColorConfig = field(default_factory=ColorConfig)
    Welcome_Settings: WelcomeConfig = field(default_factory=WelcomeConfig)
    Commands_Settings: CommandsSettings = field(default_factory=CommandsSettings)
    AI: AISettings = field(default_factory=AISettings)
    Testing_guilds_id: List[int] = field(default_factory=lambda: [12341234,43214321])
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
            "Embeds Colour": self.General_Embeds_Colour.to_dict(),
            "Welcome": {
                k: v for k, v in self.Welcome_Settings.__dict__.items()
            },
            "Commands": {
                k: v for k, v in self.Commands_Settings.__dict__.items()
            },
            "AI": {
                k: v for k, v in self.AI.__dict__.items()
            },
            "TESTING GUILDS ID": self.Testing_guilds_id,
            "AI_AllowedServers": self.AI_AllowedServers,
            "AI_AllowedUsersID": self.AI_AllowedUsersID
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Bot_Config':
        """Create a Bot_Config instance from a dictionary."""
        return cls(
            General=GeneralConfig(**data.get("General", {})),
            Logger=LoggerConfig(**data.get("Logger", {})),
            General_Embeds_Colour=ColorConfig.from_dict(data.get("Embeds Colour", {})),
            Welcome_Settings=WelcomeConfig(**data.get("Welcome", {})),
            Commands_Settings=CommandsSettings(**data.get("Commands", {})),
            AI=AISettings(**data.get("AI", {})),
            Testing_guilds_id=data.get("TESTING GUILDS ID", []),
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
            "Embeds Colour",
            "Welcome",
            "Commands",
            "AI",
            "TESTING GUILDS ID",
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
Presence = BotConfig.General.presence
send_to_owner_enabled = BotConfig.General.send_to_online_owner
overwriteOwner = BotConfig.General.owner_id

Format = BotConfig.Logger.format
Level = BotConfig.Logger.level
 
# Colors/Colour
colors = BotConfig.General_Embeds_Colour
colours = BotConfig.General_Embeds_Colour

# Commands
EnableAdvanceViewing = BotConfig.Commands_Settings.enable_advanced_viewing

#AI
enableAI = BotConfig.AI.enable
ip = BotConfig.AI.ip
allowAllServers = BotConfig.AI.allow_all_servers
allowAllUsers  = BotConfig.AI.allow_all_users

# Welcome
Welcome_enabled = BotConfig.Welcome_Settings.enabled
baseImagePath = BotConfig.Welcome_Settings.base_image_path
Font = BotConfig.Welcome_Settings.font
BackupFont = BotConfig.Welcome_Settings.backup_font
SizeFont = BotConfig.Welcome_Settings.font_size
Resize = BotConfig.Welcome_Settings.resize_dimensions
avatarPosition = BotConfig.Welcome_Settings.avatar_position
textPosition = BotConfig.Welcome_Settings.text_position
textColor = BotConfig.Welcome_Settings.text_color_rgb

# Advanced Settings
TESTING_GUILD_ID = BotConfig.Testing_guilds_id
AI_AllowedServers = BotConfig.AI_AllowedServers
AI_AllowedUsersID = BotConfig.AI_AllowedUsersID