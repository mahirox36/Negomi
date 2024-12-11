from nextcord import *
from nextcord.ext import commands
from nextcord import Interaction as init
from modules.Nexon import *
import os
import json
from pathlib import Path

description= f"Advance viewing is hard but if you understand it, it's easy\n\
        first try type: {prefix}view-x, it gives you folders and you can type the folder you want in after command like {prefix}view-x <Folder>\n\
        can there is no limit of how many folder you type in!\n\
        and if you said '{prefix}view-x show' it will give you the entire data"

class Settings(commands.Cog):
    def __init__(self, client:Client):
        self.client = client
        self.featuresPath = Path("classes/Features")
        self.features = [f.stem.lower() for f in self.featuresPath.iterdir() if f.is_file() if f.name.endswith(".py")]
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
    
    def get_disabled(self, serverID) -> List[str]:
        with DataGlobal("Feature", serverID, [], False) as data:
            return data.data
    
    def get_enabled(self, serverID) -> List[str]:
        with DataGlobal("Feature", serverID, [], False) as data:
            result = set(self.features) - set(data.data)
        return result
        
    
    @slash_command("feature", default_member_permissions=Permissions(administrator=True))
    async def feature(self, ctx):
        pass
    
    @feature.subcommand("disable")
    async def disable(self, ctx:init, feature: str =SlashOption("feature", "Select a feature to disable", True,autocomplete=True)):
        feature= feature.lower()
        if feature in self.get_disabled(ctx.guild_id):
            await ctx.send(embed=error_embed(f"{feature} is Already Disabled", "Already disabled"), ephemeral=True)
            return
        elif feature not in self.features:
            await ctx.send(embed=error_embed(f"There is not feature called {feature}"))
            return
        data = self.get_disabled(ctx.guild.id)
        data.append(feature)
        with DataGlobal("Feature", ctx.guild_id) as file:
            file.data = data
        await ctx.send(embed=info_embed(f"{feature.capitalize()} got disabled!","Feature disabled"))
    
    @feature.subcommand("enable")
    async def enable(self, ctx:init, feature: str =SlashOption("feature", "Select a feature to disable", True,autocomplete=True)):
        feature= feature.lower()
        if feature in self.get_enabled(ctx.guild_id):
            await ctx.send(embed=error_embed(f"{feature} is Already enabled", "Already enabled"), ephemeral=True)
            return
        elif feature not in self.features:
            await ctx.send(embed=error_embed(f"There is not feature called {feature}"))
            return
        data = self.get_disabled(ctx.guild.id)
        data.remove(feature)
        with DataGlobal("Feature", ctx.guild_id) as file:
            file.data = data
        await ctx.send(embed=info_embed(f"{feature.capitalize()} got enabled!","Feature enabled"))
    
    @disable.on_autocomplete("feature")
    async def feature_autocomplete(self, interaction: Interaction, current: str):
        available_features:List[str] = self.get_enabled(interaction.guild_id)
        # Filter features based on the current input
        suggestions = [name for name in available_features if name.lower().startswith(current.lower())]

        # Respond with the filtered choices
        await interaction.response.send_autocomplete(suggestions)
        
    @enable.on_autocomplete("feature")
    async def feature_autocomplete(self, interaction: Interaction, current: str):
        available_features = self.get_disabled(interaction.guild_id)
        suggestions = [name for name in available_features if name.lower().startswith(current.lower())]

        # Respond with the filtered choices
        await interaction.response.send_autocomplete(suggestions)
    

def setup(client):
    client.add_cog(Settings(client))