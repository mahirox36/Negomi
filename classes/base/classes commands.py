from datetime import datetime
from nextcord import *
import nextcord as discord
from nextcord.ext import commands
from nextcord import Interaction as init
from Lib.Side import *
import Lib.Data as Data
import os
import json

class classes_commands(commands.Cog):
    def __init__(self, client:Client):
        self.client = client
        self.initial_extension = []
        self.base_extension = []

        for filename in os.listdir("./classes"):
            if filename.endswith(".py"):
                self.initial_extension.append("classes." + filename[:-3])
        for filename in os.listdir("./classes/base"):
            if filename.endswith(".py"):
                self.base_extension.append("classes.base." + filename[:-3])
    @slash_command("reload_classes")
    async def reload_classes(self,ctx:init):
        await ctx.response.defer(ephemeral=True)
        """Reload all Classes
            ~~~~~~~"""
        await Data.check_owner_permission(ctx)
        temp = 0
        await ctx.response.send_message("Reloading...",ephemeral=True)
        a = await ctx.channel.send("```Reloading...```")
        for i in list(client.extensions):
            client.reload_extension(i)
            fv = a.content.replace(".```","")
            temp += 1
        fv = a.content.replace(".```","")
        await a.edit(fv + f"\n\nReloaded {temp} Classes!```")
        # clear()
        print('Your Bot Is Reloaded!\nWe have logged in as {0.user}'.format(client))
        print(line)

    @slash_command("load_class")
    async def load_class(self,ctx:init,extension:str):
        await ctx.response.defer(ephemeral=True)
        await Data.check_owner_permission(ctx)
        try:
            client.load_extension(f"classes.{extension}")
            await ctx.send(f"Loaded {extension}")
        except Exception as e:
            await ctx.send(embed=error_embed(str(e)))

    @slash_command("unload_class")
    async def unload_class(self,ctx:init,extension:str):
        await ctx.response.defer(ephemeral=True)
        await Data.check_owner_permission(ctx)
        try:
            client.unload_extension(f"classes.{extension}")
            await ctx.send(f"Unloaded {extension}")
        except Exception as e:
            await ctx.send(embed=error_embed(str(e)))

    @slash_command("reload_class")
    async def reload_class(self,ctx:init,extension:str):
        await ctx.response.defer(ephemeral=True)
        await Data.check_owner_permission(ctx)
        try:
            client.reload_extension(f"classes.{extension}")
            await ctx.send(f"Reloaded {extension}")
        except Exception as e:
            await ctx.send(embed=error_embed(str(e)))

    @slash_command("list_classes")
    async def list_classes(self,ctx:init):
        await ctx.response.defer(ephemeral=True)
        await Data.check_owner_permission(ctx)
        temp = 0
        a = "```\n"
        for i in self.base_extension:
            a += str(i + " (Base)\n")
            temp += 1
        for i in self.initial_extension:
            a += str(i + "\n")
            temp += 1
        a += f"\n{temp} Classes!```"
        await ctx.send(a)

    
    


def setup(client):
    client.add_cog(classes_commands(client))