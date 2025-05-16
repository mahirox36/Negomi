import copy
import logging
from typing import Dict, Optional, Any, Tuple
from modules.Nexon import Feature

logger = logging.getLogger("welcome.config")


class WelcomeConfigManager:
    """Manages welcome configurations and settings"""

    def __init__(self):
        """Initialize configuration manager"""
        self.welcome_cache: Dict[int, Dict[str, Any]] = {}

    def get_default_settings(self) -> dict:
        """Get default welcome settings with enhanced customization options"""
        return {
            "message": "Welcome {mention} to {server}!",
            "channel_id": None,
            "style": "image",
            "enabled": True,
            "embed_color": 0x5865F2,
            "image_settings": {
                "background_url": "https://raw.githubusercontent.com/mahirox36/Negomi/refs/heads/main/Assets/img/Welcome.png",
                "canvas_size": [800, 400],
                "blur_background": False,
                "blur_amount": 5,
                "background_brightness": 0.8,
                "overlay_opacity": 0,
                "avatar_size": [128, 128],
                "avatar_position": [0.125, 0.25],
                "avatar_border": True,
                "border_color": "#FFFFFF",
                "border_width": 3,
                "effects": {
                    "blur": 0,
                    "brightness": 1.0,
                    "contrast": 1.0,
                    "saturation": 1.0,
                    "overlay_color": None,
                    "overlay_opacity": 0.5,
                    "rotation": 0,
                },
                "text_elements": [
                    {
                        "text": "Welcome {member}!",
                        "position": [0.3125, 0.375],
                        "size": 48,
                        "color": "#FFFFFF",
                        "font": "arial",
                        "shadow": True,
                        "shadow_offset": 2,
                        "shadow_color": "#000000",
                        "outline": False,
                        "outline_size": 2,
                        "outline_color": "#000000",
                        "gradient": {
                            "enabled": False,
                            "start_color": "#FFFFFF",
                            "end_color": "#000000",
                            "direction": "horizontal",
                        },
                    }
                ],
                "shapes": [
                    {
                        "type": "rectangle",
                        "coordinates": [0.2, 0.2, 0.8, 0.8],
                        "color": "#FFFFFF",
                        "opacity": 128,
                        "outline": "#000000",
                        "width": 2,
                        "enabled": False,
                    }
                ]
            },
        }

    async def get_welcome_config(self, guild_id: int) -> dict:
        """Get welcome configuration with defaults"""
        if guild_id in self.welcome_cache:
            return self.welcome_cache[guild_id]

        feature = await Feature.get_guild_feature_or_none(guild_id, "Welcome")
        if feature is None:
            defaults = self.get_default_settings()
            self.welcome_cache[guild_id] = defaults
            return defaults

        config = feature.get_setting("welcome_config")
        if not config:
            defaults = self.get_default_settings()
            self.welcome_cache[guild_id] = defaults
            return defaults

        # Merge with defaults to ensure all fields exist
        defaults = self.get_default_settings()

        # Deep merge the configs
        merged_config = self._deep_merge(defaults, config)

        # Ensure critical settings exist
        self._ensure_critical_settings(merged_config)

        self.welcome_cache[guild_id] = merged_config
        return merged_config

    def _deep_merge(self, default: Dict, custom: Dict) -> Dict:
        """Deep merge two dictionaries, with custom values taking precedence"""
        result = default.copy()

        for key, value in custom.items():
            # If both dicts have the key and both values are dicts, merge them
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = self._deep_merge(result[key], value)
            else:
                # Otherwise just use the custom value
                result[key] = value

        return result

    def _ensure_critical_settings(self, config: dict):
        """Ensure critical settings exist in the config"""
        # Ensure text_elements exists and is a list
        if "image_settings" in config:
            if "text_elements" not in config["image_settings"]:
                config["image_settings"]["text_elements"] = self.get_default_settings()[
                    "image_settings"
                ]["text_elements"]
            if "custom_elements" not in config["image_settings"]:
                config["image_settings"]["custom_elements"] = []

            # Ensure all elements have valid positions
            for elements_key in ["text_elements", "custom_elements"]:
                for element in config["image_settings"][elements_key]:
                    if "position" in element:
                        # Ensure position is stored as a list
                        if isinstance(element["position"], tuple):
                            element["position"] = list(element["position"])

    async def save_welcome_config(self, guild_id: int, config: dict) -> dict:
        """Save welcome configuration and invalidate caches"""
        feature = await Feature.get_guild_feature(guild_id, "Welcome")
        await feature.set_setting("welcome_config", config)
        self.welcome_cache[guild_id] = config  # Update with new config

        # Add guild to active guilds list if not already there
        global_feature = await Feature.get_global_feature("Welcome")
        active_guilds = set(global_feature.get_global("guilds", []))
        if guild_id not in active_guilds:
            active_guilds.add(guild_id)
            await global_feature.set_global("guilds", list(active_guilds))

        logger.debug(f"Saved welcome config for guild {guild_id}")
        return config

    async def prepare_config_for_image_generation(self, config: dict) -> dict:
        """Prepare configuration for image generation by converting relative positions to absolute pixels.
        This is needed because the frontend uses relative positions (0-1) but image generation needs pixels.
        """
        if not config:
            return self.get_default_settings()

        # Create a deep copy to avoid modifying the original
        transformed_config = copy.deepcopy(config)

        # Dynamically set canvas size based on background image size
        if "background_url" in transformed_config["image_settings"]:
            background_url = transformed_config["image_settings"]["background_url"]
            # Assume a function fetch_image_size(url) exists to get image dimensions
            try:
                CANVAS_WIDTH, CANVAS_HEIGHT = await self.fetch_image_size(background_url)
            except Exception as e:
                logger.error(f"Failed to fetch background image size: {e}")
                CANVAS_WIDTH, CANVAS_HEIGHT = 800, 400  # Fallback to default size

        # Ensure all settings are applied
        if "image_settings" in transformed_config:
            img_settings = transformed_config["image_settings"]

            # Convert avatar position from relative to absolute pixels
            if "avatar_position" in img_settings:
                rel_pos = img_settings["avatar_position"]
                if (
                    isinstance(rel_pos, list)
                    and len(rel_pos) == 2
                    and all(isinstance(p, (int, float)) for p in rel_pos)
                ):
                    if all(0 <= p <= 1 for p in rel_pos):
                        img_settings["avatar_position"] = [
                            int(rel_pos[0] * CANVAS_WIDTH),
                            int(rel_pos[1] * CANVAS_HEIGHT),
                        ]

            # Convert text elements
            if "text_elements" in img_settings:
                for element in img_settings["text_elements"]:
                    if "position" in element:
                        rel_pos = element["position"]
                        if (
                            isinstance(rel_pos, list)
                            and len(rel_pos) == 2
                            and all(isinstance(p, (int, float)) for p in rel_pos)
                        ):
                            if all(0 <= p <= 1 for p in rel_pos):
                                element["position"] = [
                                    int(rel_pos[0] * CANVAS_WIDTH),
                                    int(rel_pos[1] * CANVAS_HEIGHT),
                                ]

            # Convert custom elements
            if "custom_elements" in img_settings:
                for element in img_settings["custom_elements"]:
                    if "position" in element:
                        rel_pos = element["position"]
                        if (
                            isinstance(rel_pos, list)
                            and len(rel_pos) == 2
                            and all(isinstance(p, (int, float)) for p in rel_pos)
                        ):
                            if all(0 <= p <= 1 for p in rel_pos):
                                element["position"] = [
                                    int(rel_pos[0] * CANVAS_WIDTH),
                                    int(rel_pos[1] * CANVAS_HEIGHT),
                                ]

                    if "size" in element:
                        rel_size = element["size"]
                        if (
                            isinstance(rel_size, list)
                            and len(rel_size) == 2
                            and all(isinstance(s, (int, float)) for s in rel_size)
                        ):
                            if all(0 <= s <= 1 for s in rel_size):
                                element["size"] = [
                                    int(rel_size[0] * CANVAS_WIDTH),
                                    int(rel_size[1] * CANVAS_HEIGHT),
                                ]

        return transformed_config

    async def fetch_image_size(self, url: str) -> Tuple[int, int]:
        """Fetch the dimensions of an image from a URL."""
        import aiohttp
        from PIL import Image
        import io

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        image_data = await response.read()
                        with Image.open(io.BytesIO(image_data)) as img:
                            return img.size
        except Exception as e:
            logger.error(f"Error fetching image size from {url}: {e}")

        # Fallback to default size if fetching fails
        return 800, 400

    async def validate_config(self, config: dict) -> Tuple[bool, str]:
        """Validate welcome configuration"""
        try:
            required_fields = ["message", "channel_id", "style", "enabled"]
            for field in required_fields:
                if field not in config:
                    return False, f"Missing required field: {field}"

            if config["style"] not in ["text", "embed", "image"]:
                return False, "Invalid style type"

            if config["style"] == "image":
                img_settings = config.get("image_settings", {})
                if not img_settings:
                    return False, "Missing image settings"

                required_img_fields = ["background_url", "canvas_size", "text_elements"]
                for field in required_img_fields:
                    if field not in img_settings:
                        return False, f"Missing required image field: {field}"

                if (
                    not isinstance(img_settings["canvas_size"], list)
                    or len(img_settings["canvas_size"]) != 2
                ):
                    return False, "Invalid canvas size format"

                for text_elem in img_settings.get("text_elements", []):
                    if "text" not in text_elem or "position" not in text_elem:
                        return False, "Invalid text element configuration"

            return True, "Configuration is valid"
        except Exception as e:
            return False, f"Validation error: {str(e)}"

    async def get_api_config(self, guild_id: int) -> dict:
        """Get configuration formatted for API use"""
        config = await self.get_welcome_config(guild_id)

        # Convert colors to hex format for API
        if "embed_color" in config:
            config["embed_color"] = f"#{config['embed_color']:06x}"

        # Convert positions to percentages for frontend
        if "image_settings" in config:
            img_settings = config["image_settings"]

            # Convert avatar position
            if "avatar_position" in img_settings:
                img_settings["avatar_position"] = [
                    x * 100 for x in img_settings["avatar_position"]
                ]

            # Convert text positions
            for text_elem in img_settings.get("text_elements", []):
                if "position" in text_elem:
                    text_elem["position"] = [x * 100 for x in text_elem["position"]]

            # Convert shape positions
            for shape in img_settings.get("shapes", []):
                if "coordinates" in shape:
                    shape["coordinates"] = [x * 100 for x in shape["coordinates"]]

        return config

    async def save_api_config(self, guild_id: int, config: dict) -> dict:
        """Save configuration from API format"""
        # Convert hex colors to integer format
        if "embed_color" in config and isinstance(config["embed_color"], str):
            config["embed_color"] = int(config["embed_color"].lstrip("#"), 16)

        # Convert percentage positions to decimals
        if "image_settings" in config:
            img_settings = config["image_settings"]

            # Convert avatar position
            if "avatar_position" in img_settings:
                img_settings["avatar_position"] = [
                    x / 100 for x in img_settings["avatar_position"]
                ]

            # Convert text positions
            for text_elem in img_settings.get("text_elements", []):
                if "position" in text_elem:
                    text_elem["position"] = [x / 100 for x in text_elem["position"]]

            # Convert shape positions
            for shape in img_settings.get("shapes", []):
                if "coordinates" in shape:
                    shape["coordinates"] = [x / 100 for x in shape["coordinates"]]

        # Validate configuration
        valid, message = await self.validate_config(config)
        if not valid:
            raise ValueError(message)

        return await self.save_welcome_config(guild_id, config)
