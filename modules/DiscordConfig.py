import logging
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from modules.config import Config, Color as color

VERSION = "0.45"

@dataclass
class Database:
    username: str = "<USERNAME>"
    password: str = "<PASSWORD>"
    host: str = "localhost"
    port: int = 5432
    db_name: str = "bot"
    database: str = "postgres"

@dataclass
class Cloudflare:
    access_key_id: str = "<ACCESS KEY ID>"
    secret_access_key: str ="<SECRET ACCESS KEY>"
    endpoint: str = "<END POINT>"
    public_bucket_url: str = "<PUBLIC BUCKET URL>"
    bucket_name : str = "negomi-images"
    

@dataclass
class Colors:
    # Embed Colors
    Debug: color = field(default_factory=lambda: color(0x6A5ACD))
    Info: color = field(default_factory=lambda: color(0xFF69b4))
    Warn: color = field(default_factory=lambda: color(0xFFD700))
    Error: color = field(default_factory=lambda: color(0xB22222))
    # Rarity Colors
    Common: color = field(default_factory=lambda: color(0xFF1493))
    Uncommon: color = field(default_factory=lambda: color(0x00FFB9))
    Rare: color = field(default_factory=lambda: color(0xFF4500))
    Epic: color = field(default_factory=lambda: color(0x32CD32))
    Legendary: color = field(default_factory=lambda: color(0x9400D3))

@dataclass
class OAuthSettings:
    token: str = "<DISCORD_BOT_TOKEN>"
    client_id: str = "<DISCORD_CLIENT_ID>"
    client_secret: str = "<DISCORD_CLIENT_SECRET>"
    redirect_url: str = "https://example.com/callback"
    debug_redirect_url: str = "http://localhost:3000/callback"

@dataclass
class BotConfig:
    presence: str = "My Master Mahiro"
    owner_id: Optional[int] = None
    send_to_online_owner: bool = True
    logger_level: str = "INFO"
    debug: bool = False
    colors: Colors = field(default_factory=Colors)
    database: Database = field(default_factory=Database)
    cloudflare: Cloudflare = field(default_factory=Cloudflare)
    oauth: OAuthSettings = field(default_factory=OAuthSettings)
    ai_enabled: bool = False
    ai_ip: str = "127.0.0.1"
    testing_guilds: List[int] = field(default_factory=lambda: [12341234, 43214321])
    version: str = VERSION

    def _validate_config(self, config_path: str) -> None:
        default_config = BotConfig()
        cfg = Config(config_path)
        cfg.load()

        # Check for missing sections and fields
        for section, values in self.__dict__.items():
            if isinstance(values, (Database, Cloudflare, Colors, OAuthSettings)):
                if section not in cfg.data:
                    print(f"Adding missing section: {section}")
                    cfg.data[section] = {}
                for field in values.__dict__:
                    if field not in cfg.data[section]:
                        print(f"Adding missing field: {section}.{field}")
                        cfg.data[section][field] = getattr(default_config.__dict__[section], field) # type: ignore

        # Remove deprecated sections and fields
        sections_to_remove = []
        for section in cfg.data:
            if section not in self.__dict__:
                sections_to_remove.append(section)
                continue
            if isinstance(self.__dict__[section], (Database, Cloudflare, Colors, OAuthSettings)):
                fields_to_remove = []
                for field in cfg.data[section]:
                    if field not in self.__dict__[section].__dict__:
                        fields_to_remove.append(field)
                for field in fields_to_remove:
                    print(f"Removing deprecated field: {section}.{field}")
                    del cfg.data[section][field]

        for section in sections_to_remove:
            print(f"Removing deprecated section: {section}")
            del cfg.data[section]

        cfg.save()

    def save(self, config_path: str = ".secrets/config.ini"):
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        cfg = Config(config_path)
        if os.path.exists(config_path):
            cfg.load()
        
        # Convert colors to string format
        color_data = {}
        for k, v in self.colors.__dict__.items():
            if isinstance(v, color):
                color_data[k] = str(v)
            else:
                color_data[k] = v

        data = {
            "Bot": {
                "presence": self.presence,
                "owner_id": self.owner_id,
                "send_to_online_owner": self.send_to_online_owner,
                "logger_level": self.logger_level,
                "debug": self.debug,
                "version": self.version
            },
            "OAuth": {
                "token": self.oauth.token,
                "client_id": self.oauth.client_id,
                "client_secret": self.oauth.client_secret,
                "redirect_url": self.oauth.redirect_url,
                "debug_redirect_url": self.oauth.debug_redirect_url
            },
            "Database": self.database.__dict__,
            "Cloudflare": self.cloudflare.__dict__,
            "Colors": color_data,
            "AI": {
                "enabled": self.ai_enabled,
                "ip": self.ai_ip,
            },
            "TestingGuilds": self.testing_guilds
        }
        
        # Remove any sections that are no longer in use
        for section in list(cfg.data.keys()):
            if section not in data:
                cfg.remove_section(section)
        
        cfg.set_layout(["Bot", "OAuth", "Database", "Cloudflare", "Colors", "AI", "TestingGuilds"])
        cfg.data = data
        cfg.save()

    @classmethod
    def load(cls, config_path: str = ".secrets/config.ini") -> 'BotConfig':
        # Create default config for comparison
        default_config = cls()
        
        if not os.path.exists(config_path):
            default_config.save(config_path)
            return default_config

        try:
            cfg = Config(config_path)
            cfg.load()
            
            # Load existing data
            bot_data: Dict[str, Any] = cfg.data.get("Bot", {}) # type: ignore
            oauth_data: Dict[str, Any] = cfg.data.get("OAuth", {}) # type: ignore
            database_data: Dict[str, Any] = cfg.data.get("Database", {}) # type: ignore
            cloudflare_data: Dict[str, Any] = cfg.data.get("Cloudflare", {}) # type: ignore
            colors_data: Dict[str, Any] = cfg.data.get("Colors", {}) # type: ignore
            ai_data: Dict[str, Any] = cfg.data.get("AI", {}) # type: ignore
            
            # Convert color values properly
            colors = Colors()
            for k, v in colors_data.items():
                if hasattr(colors, k):
                    if isinstance(v, str) and v.startswith('#'):
                        setattr(colors, k, color(v))
                    elif isinstance(v, (int, str)):
                        setattr(colors, k, color(v))

            # Handle testing guilds
            testing_guilds_data = cfg.data.get("TestingGuilds", [12341234, 43214321])
            if isinstance(testing_guilds_data, str):
                testing_guilds = [int(x.strip()) for x in testing_guilds_data.strip('[]').split(',') if x.strip()]
            elif isinstance(testing_guilds_data, (list, tuple)):
                testing_guilds = [int(x) if isinstance(x, str) else x for x in testing_guilds_data]
            else:
                testing_guilds = [12341234, 43214321]

            # Handle owner_id
            owner_id = bot_data.get("owner_id")
            if owner_id is not None:
                try:
                    owner_id = int(owner_id) if isinstance(owner_id, str) else owner_id
                except (ValueError, TypeError):
                    owner_id = None
            
            # Create config with loaded values
            loaded_config = cls(
                presence=str(bot_data.get("presence", default_config.presence)),
                owner_id=owner_id,
                send_to_online_owner=bool(bot_data.get("send_to_online_owner", default_config.send_to_online_owner)),
                logger_level=str(bot_data.get("logger_level", default_config.logger_level)),
                debug=bool(bot_data.get("debug", default_config.debug)),
                colors=colors,
                oauth=OAuthSettings(
                    token=str(oauth_data.get("token", default_config.oauth.token)),
                    client_id=str(oauth_data.get("client_id", default_config.oauth.client_id)),
                    client_secret=str(oauth_data.get("client_secret", default_config.oauth.client_secret)),
                    redirect_url=str(oauth_data.get("redirect_url", default_config.oauth.redirect_url)),
                    debug_redirect_url=str(oauth_data.get("debug_redirect_url", default_config.oauth.debug_redirect_url))
                ),
                database=Database(
                    username=str(database_data.get("username", default_config.database.username)),
                    password=str(database_data.get("password", default_config.database.password)),
                    host=str(database_data.get("host", default_config.database.host)),
                    port=int(database_data.get("port", default_config.database.port)),
                    db_name=str(database_data.get("db_name", default_config.database.db_name)),
                    database=str(database_data.get("database", default_config.database.database)),
                ),
                cloudflare=Cloudflare(
                    access_key_id=str(cloudflare_data.get("access_key_id", default_config.cloudflare.access_key_id)),
                    secret_access_key=str(cloudflare_data.get("secret_access_key", default_config.cloudflare.secret_access_key)),
                    endpoint=str(cloudflare_data.get("endpoint", default_config.cloudflare.endpoint)),
                    public_bucket_url=str(cloudflare_data.get("public_bucket_url", default_config.cloudflare.public_bucket_url)),
                    bucket_name=str(cloudflare_data.get("bucket_name", default_config.cloudflare.bucket_name)),
                ),
                ai_enabled=bool(ai_data.get("enabled", default_config.ai_enabled)),
                ai_ip=str(ai_data.get("ip", default_config.ai_ip)),
                testing_guilds=testing_guilds,
                version=str(bot_data.get("version", "0.0"))
            )

            # Check if config needs update
            if loaded_config.version != VERSION:
                print(f"Updating config from version {loaded_config.version} to {VERSION}")
                loaded_config.version = VERSION
                # Save updated config
                loaded_config.save(config_path)

            return loaded_config

        except Exception as e:
            logging.error(f"Error loading config: {e}")
            # On error, save and return default config
            default_config.save(config_path)
            return default_config

# Initialize and export configuration
config = BotConfig.load()

# Quick access exports
token = config.oauth.token  # Updated to use OAuth token
Presence = config.presence
overwriteOwner = config.owner_id
send_to_owner_enabled = config.send_to_online_owner
logger_level = config.logger_level
debug = config.debug
colors = config.colors
colours = config.colors
enableAI = config.ai_enabled
ip = config.ai_ip
TESTING_GUILD_ID = config.testing_guilds