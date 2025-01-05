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
    @commands.command(name = "advance-viewing", aliases=["view-x", "view"],description= description)
    @commands.guild_only()
    @enableByConfig(EnableAdvanceViewing)
    async def advance_viewing(self, ctx:commands.Context, *folders):
        data = {}
        base_path = "./data"
        
        for folder in filter(lambda f: os.path.isdir(f"{base_path}/{f}") and f != "TempVoice_UsersSettings", os.listdir(base_path)):
            folder_path = f"{base_path}/{folder}/{ctx.guild.id}"

            if not os.path.exists(folder_path):
                continue
            
            data[folder] = {}

            for item in os.listdir(folder_path):
                item_path = os.path.join(folder_path, item)

                if os.path.isfile(item_path):
                    with open(item_path) as f:
                        data[folder][item] = json.load(f)
                elif os.path.isdir(item_path):
                    for file in os.listdir(item_path):
                        file_path = os.path.join(item_path, file)
                        if os.path.isfile(file_path):
                            data[folder][item] = {}
                            with open(file_path) as f:
                                data[folder][item][file] = json.load(f)
        try: temp = folders[0]
        except IndexError: temp = "X"
        if temp == "show":
            try:
                await ctx.reply(f"```json\n{json.dumps(data,indent=2)}```")
            except:
                await ctx.reply(embed= error_embed("The Data was about to send was too long",title="Couldn't send"))
            return
        elif folders == ():
            simpleData = ""
            for file in data:
                simpleData += f"{file}\n"
            await ctx.reply(embed= info_embed(simpleData,title="Data/"))
            return
        try:target = os.path.join(base_path, str(folders[0]) ,str(ctx.guild.id),\
                str(folders[1]),str(folders[2]))
        except IndexError:
            try:target = os.path.join(base_path, folders[0] ,str(ctx.guild.id), folders[1])
            except IndexError:target = os.path.join(base_path, folders[0] ,str(ctx.guild.id))
        logger.info(target)
        if os.path.isdir(target):
            items = os.listdir(target)
            description = "\n".join(items)
            await ctx.reply(embed=info_embed(f"```\n{description}```", title=f"Contents of {folders[-1]}:"))
        elif os.path.isfile(target):
            with open(target) as f:
                file_data = json.load(f)
            await ctx.reply(embed=info_embed(title=f"Contents of {folders[-1]}:", description=f"```json\n{json.dumps(file_data, indent=2)}```"))
        else:
            await ctx.reply(embed=error_embed(description=f"`{folders[-1]}` is not a valid folder or file."))
    
    def get_disabled_features(self, server_id: str) -> List[str]:
        """Get list of disabled features for a server."""
        with DataGlobal("Feature", server_id, [], False) as file:
            return file.data
    
    def get_enabled_features(self, server_id: str) -> Set[str]:
        """Get set of enabled features for a server."""
        with DataGlobal("Feature", server_id, [], False) as file:
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
        with DataGlobal("Feature", ctx.guild_id) as file:
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
        
        with DataGlobal("Feature", ctx.guild_id) as file:
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