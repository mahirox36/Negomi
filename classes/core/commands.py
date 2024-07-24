from datetime import datetime
from nextcord import *
import nextcord as discord
from nextcord.ext import commands
from nextcord import Interaction as init
from Lib.Side import *
import Lib.Data as Data
from Lib.richer import *
import os
import json


class ExtensionSelect(discord.ui.Select):
    def __init__(self, extensions, ctx,client:Client):
        # Populate the dropdown options with the extensions
        options = [discord.SelectOption(label=ext) for ext in extensions]
        super().__init__(placeholder="Choose an extension to unload...", min_values=1, max_values=1, options=options)
        self.ctx = ctx
        self.client = client

    async def callback(self, interaction: discord.Interaction):
        # Unload the selected extension
        extension = self.values[0]
        try:
            self.client.unload_extension(f"classes.{extension}")
            await interaction.response.send_message(f"Unloaded {extension}", ephemeral=True)
            commandz(self.client).initial_extension.remove(f"classes.{extension}")
            
        except Exception as e:
            await interaction.response.send_message(embed=error_embed(str(e)), ephemeral=True)

class ExtensionDropdownView(discord.ui.View):
    def __init__(self, extensions, ctx,client:Client):
        super().__init__()
        self.add_item(ExtensionSelect(extensions, ctx,client))


class commandz(commands.Cog):
    def __init__(self, client:Client):
        self.client = client
        self.initial_extension = []
        self.core_extension = []
        self.initial_extensionName = []
        self.core_extensionName = []

        for filename in os.listdir("./classes"):
            if filename.endswith(".py"):
                self.initial_extension.append("classes." + filename[:-3])
                self.initial_extensionName.append(filename[:-3])
        for filename in os.listdir("./classes/core"):
            if filename.endswith(".py"):
                self.core_extension.append("classes.core." + filename[:-3])
                self.core_extensionName.append(filename[:-3])
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
        await client.change_presence(activity=Activity(type=ActivityType.watching, name=f"Over {len(client.guilds)} Servers"))
        # clear()
        print(Rule(f'{client.user.display_name}  Is Reloaded!',style="bold green"))
        if send_to_owner_enabled:
            user = client.get_user(owner_id)
            channel = await user.create_dm()
            await channel.send(embed=info_embed("Bot is Reloaded"))

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
    async def unload_class(self,ctx:init):
        await ctx.response.defer(ephemeral=True)
        await Data.check_owner_permission(ctx)
        await ctx.send("Please Select the Extension/s to Unload", view=ExtensionDropdownView(self.initial_extensionName, ctx,self.client))

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
    client.add_cog(commandz(client))