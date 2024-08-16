import nextcord
import nextcord as discord
from nextcord import *
from nextcord.ext import commands
from nextcord import Interaction as init
from Lib.Side import *
from Lib.Logger import *
import os
import json

description= f"Advance viewing is hard but if you understand it, it's easy\n\
        first try type: {prefix}view-x, it gives you folders and you can type the folder you want in after command like {prefix}view-x <Folder>\n\
        can there is no limit of how many folder you type in!\n\
        and if you said '{prefix}view-x show' it will give you the entire data"

class Settings(commands.Cog):
    def __init__(self, client:Client):
        self.client = client
    #TODO: Add Simple Editing for Data
    @commands.command(name = "advance-viewing", aliases=["view-x"],description= description)
    @commands.guild_only()
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
        print(target)
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
    

def setup(client):
    client.add_cog(Settings(client))