from modules.Nexon import *

description= f"Advance viewing is hard but if you understand it, it's easy\n\
        first try type: {prefix}view-x, it gives you folders and you can type the folder you want in after command like {prefix}view-x <Folder>\n\
        can there is no limit of how many folder you type in!\n\
        and if you said '{prefix}view-x show' it will give you the entire data"

class Settings(commands.Cog):
    def __init__(self, client: Client):
        self.client = client
        self.features_path = Path("classes/Features")
        base_path = Path.cwd()
        self.features_path = base_path / "classes" / "Features"
        
        # Get all Python files in features directory
        self.features = [
            f.stem.lower() 
            for f in self.features_path.iterdir() 
            if f.is_file() and f.name.endswith(".py")
        ]
        logger.debug(self.features)
    
    def get_disabled_features(self, server_id: str) -> List[str]:
        """Get list of disabled features for a server."""
        with DataManager("Feature", server_id, default=[], auto_save=False) as file:
            return file.data
    
    def get_enabled_features(self, server_id: str) -> Set[str]:
        """Get set of enabled features for a server."""
        with DataManager("Feature", server_id, default=[], auto_save=False) as file:
            return set(self.features) - set(file.data)
    @slash_command("feature", default_member_permissions=Permissions(administrator=True))
    async def feature(self, ctx):
        """Base command for feature management."""
        pass

    @feature.subcommand("disable", "Disable a feature in your server") 
    async def disable(self, ctx: init, 
                     feature: str = SlashOption("feature", "Select a feature to disable", 
                                              required=True, autocomplete=True)):
        feature = feature.lower()
        disabled_features = self.get_disabled_features(ctx.guild_id)

        if feature in disabled_features:
            await ctx.send(
                embed=error_embed("Feature Already Disabled", f"{feature} is already disabled"),
                ephemeral=True
            )
            return
        
        if feature not in self.features:
            await ctx.send(
                embed=error_embed("Invalid Feature", f"Feature '{feature}' does not exist")
            )
            return

        disabled_features.append(feature)
        with DataManager("Feature", ctx.guild_id) as file:
            file.data = disabled_features
        
        await ctx.send(
            embed=info_embed("Feature Disabled", f"{feature.capitalize()} has been disabled")
        )

    @feature.subcommand("enable", "Enable a feature in your server") 
    async def enable(self, ctx: init,
                    feature: str = SlashOption("feature", "Select a feature to enable",
                                             required=True, autocomplete=True)):
        feature = feature.lower()
        enabled_features = self.get_enabled_features(ctx.guild_id)

        if feature in enabled_features:
            await ctx.send(
                embed=error_embed("Feature Already Enabled", f"{feature} is already enabled"),
                ephemeral=True
            )
            return
        
        if feature not in self.features:
            await ctx.send(
                embed=error_embed("Invalid Feature", f"Feature '{feature}' does not exist")
            )
            return

        disabled_features = self.get_disabled_features(ctx.guild_id)
        disabled_features.remove(feature)
        
        with DataManager("Feature", ctx.guild_id) as file:
            file.data = disabled_features
        
        await ctx.send(
            embed=info_embed("Feature Enabled", f"{feature.capitalize()} has been enabled")
        )

    @disable.on_autocomplete("feature")
    async def disable_autocomplete(self, interaction: Interaction, current: str):
        """Autocomplete for disable command showing enabled features."""
        available_features = self.get_enabled_features(interaction.guild_id)
        suggestions = [
            name for name in available_features 
            if name.lower().startswith(current.lower())
        ]
        await interaction.response.send_autocomplete(suggestions)

    @enable.on_autocomplete("feature")
    async def enable_autocomplete(self, interaction: Interaction, current: str):
        """Autocomplete for enable command showing disabled features."""
        available_features = self.get_disabled_features(interaction.guild_id)
        suggestions = [
            name for name in available_features 
            if name.lower().startswith(current.lower())
        ]
        await interaction.response.send_autocomplete(suggestions)
    

def setup(client):
    client.add_cog(Settings(client))