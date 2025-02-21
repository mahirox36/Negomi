from typing import List
from modules.Nexon import *
from nexon.ext import commands
from nexon.ext.application_checks import check
from .DataManager import DataManager

class FeatureDisabled(commands.CheckFailure):
    def __init__(self, message: str, feature_name: str, send_error: bool = True):
        self.message = message
        self.feature_name = feature_name
        self.send_error = send_error
        super().__init__(message)

def get_feature_state(guild_id: int) -> List[str]:
    """Get the list of disabled features for a guild."""
    with DataManager("Feature", guild_id, default=[], auto_save=False) as file:
        return file.data

def feature():
    """
    Decorator to check if a feature is enabled.
    Raises FeatureDisabled if the feature is disabled.
    """
    def predicate(ctx):
        # Skip check in DMs
        if not getattr(ctx, 'guild', None):
            return True

        # Get the cog name without numbers
        if hasattr(ctx, 'application_command'):
            # For slash commands
            cog_name = remove_numbers(ctx.application_command.parent_cog.__class__.__name__)
        else:
            # For regular commands
            cog_name = remove_numbers(ctx.cog.__class__.__name__)

        disabled_features = get_feature_state(ctx.guild.id)
        
        if cog_name.lower() in disabled_features:
            raise FeatureDisabled(
                f"Feature '{cog_name}' is disabled in this server.",
                cog_name
            )
        
        return True

    return check(predicate)

async def check_feature_inside(guild_id: int, cog: object, send_Error: bool = False) -> bool:
    """
    Check if a feature is enabled within other code.
    Returns True if feature is enabled, False if disabled.
    """
    try:
        cog_name = remove_numbers(cog.__class__.__name__.lower())
        disabled_features = get_feature_state(guild_id)
        if cog_name in disabled_features:
            raise FeatureDisabled(
                f"Feature '{cog_name}' is disabled in this server.",
                cog_name, send_Error
            )
        
        return True
    except FeatureDisabled:
        raise FeatureDisabled(
                f"Feature '{cog_name}' is disabled in this server.",
                cog_name, send_Error
            )
    except Exception:
        return True  # Allow feature by default on error