from typing import Any, Optional
from nexon import DataManager
import logging
logger = logging.getLogger("bot")

class FeatureDisabled(Exception):
    """Raised when a feature is disabled."""
    def __init__(self, message: str, feature_name: str, send_error: bool = False):
        self.feature_name = feature_name
        self.send_error = send_error
        super().__init__(message)

class FeatureManager:
    def __init__(self, guild: int, class_name: Optional[str] = None):
        self.guild = guild
        self.class_name = class_name
        self.file = DataManager("Features", guild, default={"enable": True}, subfolder=class_name)
        logger.debug(f"FeatureManager initialized for guild {guild} with class name {class_name}. and file {self.file.path}")
    
    def set_setting(self, feature_name: str, value: Any) -> None:
        """Set a feature setting with validation"""
        if feature_name and isinstance(feature_name, str):
            self.file.data[feature_name] = value
            self.file.save()
    
    def get_setting(self, feature_name: str, default: Any = None) -> Any:
        """Get a feature setting with default value"""
        return self.file.data.get(feature_name, default)
    
    def get_settings(self) -> dict:
        """Get all settings"""
        return dict(self.file.data)
    
    def is_enabled(self) -> bool:
        """Check if the feature class is enabled"""
        return bool(self.file.data.get("enable", True))
    
    def is_disabled(self) -> bool:
        """Check if the feature class is disabled"""
        return not self.is_enabled()
    
    def enable_class(self) -> None:
        """Enable the feature class"""
        self.file.data["enable"] = True
        self.file.save()
    
    def disable_class(self) -> None:
        """Disable the feature class"""
        self.file.data["enable"] = False
        self.file.save()
    
    def delete_setting(self, feature_name: str) -> bool:
        """Delete a feature setting"""
        if feature_name in self.file.data:
            del self.file.data[feature_name]
            self.file.save()
            return True
        return False
    
    def delete_class(self) -> None:
        """Delete the feature class"""
        self.file.delete()