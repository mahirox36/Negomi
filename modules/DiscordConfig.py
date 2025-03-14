import logging
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from modules.config import Config, Color as color

VERSION = "0.42"

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
    token: str = "Your Bot Token"
    client_id: str = "Your Client ID"
    client_secret: str = "Your Client Secret"
    redirect_url: str = "https://example.com/callback"
    debug_redirect_url: str = "http://localhost:3000/callback"

@dataclass
class BotConfig:
    presence: str = "My Master Mahiro"
    owner_id: Optional[int] = None
    send_to_online_owner: bool = True
    logger_level: str = "INFO"
    debug: bool = False
    split_frontend: bool = False
    colors: Colors = field(default_factory=Colors)
    oauth: OAuthSettings = field(default_factory=OAuthSettings)
    ai_enabled: bool = False
    ai_ip: str = "127.0.0.1"
    gemini_api: str = ""
    testing_guilds: List[int] = field(default_factory=lambda: [12341234, 43214321])
    version: str = VERSION

    def save(self, config_path: str = ".secrets/config.ini"):
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        cfg = Config(config_path)
        
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
                "split_frontend": self.split_frontend,
                "version": self.version
            },
            "OAuth": {
                "token": self.oauth.token,
                "client_id": self.oauth.client_id,
                "client_secret": self.oauth.client_secret,
                "redirect_url": self.oauth.redirect_url,
                "debug_redirect_url": self.oauth.debug_redirect_url
            },
            "Colors": color_data,
            "AI": {
                "enabled": self.ai_enabled,
                "ip": self.ai_ip,
                "gemini_api": self.gemini_api
            },
            "TestingGuilds": self.testing_guilds
        }
        
        cfg.set_layout(["Bot", "OAuth", "Colors", "AI", "TestingGuilds"])
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
            bot_data = cfg.data.get("Bot", {})
            oauth_data = cfg.data.get("OAuth", {})
            colors_data = cfg.data.get("Colors", {})
            ai_data = cfg.data.get("AI", {})
            
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
                split_frontend=bool(bot_data.get("split_frontend", default_config.split_frontend)),
                colors=colors,
                oauth=OAuthSettings(
                    token=str(oauth_data.get("token", default_config.oauth.token)),
                    client_id=str(oauth_data.get("client_id", default_config.oauth.client_id)),
                    client_secret=str(oauth_data.get("client_secret", default_config.oauth.client_secret)),
                    redirect_url=str(oauth_data.get("redirect_url", default_config.oauth.redirect_url)),
                    debug_redirect_url=str(oauth_data.get("debug_redirect_url", default_config.oauth.debug_redirect_url))
                ),
                ai_enabled=bool(ai_data.get("enabled", default_config.ai_enabled)),
                ai_ip=str(ai_data.get("ip", default_config.ai_ip)),
                gemini_api=str(ai_data.get("gemini_api", default_config.gemini_api)),
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
split_frontend = config.split_frontend
colors = config.colors
colours = config.colors
enableAI = config.ai_enabled
ip = config.ai_ip
Gemini_API = config.gemini_api
TESTING_GUILD_ID = config.testing_guilds