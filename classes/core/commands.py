from datetime import datetime
from nextcord import *
import nextcord as discord
from nextcord.ext import commands
from nextcord import Interaction as init
from Lib.Side import *
import Lib.Data as Data
import os
import json


class ExtensionSelect(discord.ui.Select):
    def __init__(self, extensions, ctx):
        # Populate the dropdown options with the extensions
        options = [discord.SelectOption(label=ext) for ext in extensions]
        super().__init__(placeholder="Choose an extension to unload...", min_values=1, max_values=1, options=options)
        self.ctx = ctx

    async def callback(self, interaction: discord.Interaction):
        # Unload the selected extension
        extension = self.values[0]
        try:
            client.unload_extension(f"classes.{extension}")
            await interaction.response.send_message(f"Unloaded {extension}", ephemeral=True)
            # Optionally, update the dropdown to remove the unloaded extension
            # This requires additional logic to edit the original message
        except Exception as e:
            await interaction.response.send_message(embed=error_embed(str(e)), ephemeral=True)

class ExtensionDropdownView(discord.ui.View):
    def __init__(self, extensions, ctx):
        super().__init__()
        self.add_item(ExtensionSelect(extensions, ctx))


class commands(commands.Cog):
    def __init__(self, client:Client):
        self.client = client
        self.initial_extension = []
        self.core_extension = []

        for filename in os.listdir("./classes"):
            if filename.endswith(".py"):
                self.initial_extension.append("classes." + filename[:-3])
        for filename in os.listdir("./classes/core"):
            if filename.endswith(".py"):
                self.core_extension.append("classes.core." + filename[:-3])
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
        for i in self.core_extension:
            a += str(i + " (Core)\n")
            temp += 1
        for i in self.initial_extension:
            a += str(i + "\n")
            temp += 1
        a += f"\n{temp} Classes!```"
        await ctx.send(a)

    
    


def setup(client):
    client.add_cog(classes_commands(client))