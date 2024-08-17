import nextcord
import nextcord as discord
from nextcord import *
from nextcord.ext import commands
from nextcord.ext.commands import Context, command
from nextcord.ext.application_checks import *
from nextcord import Interaction as init
from Lib.Side import *
from Lib.Logger import *
import os
import json

class PluginsManager(commands.Cog):
    def __init__(self, client:Client):
        self.client = client
        self.plugins = [filename[:-3] for filename in os.listdir("classes/Plugins")\
            if filename.endswith(".py")]
        
        
    
    @command(name="plugins",description="View all the Available Plugins")
    async def viewPlugins(self,ctx:Context):
        """View all the Available Plugins"""
        file = Data(ctx.guild.id,"Plugins","Applied Plugins")
        appliedPlugins= file.data if file.data != None else []
        
        pluginsEmbed= info_embed("Showing all the Plugins","Plugins")
        for plugin in self.plugins:
            # Dynamically import the plugin module
            module = __import__(f"classes.Plugins.{plugin}", fromlist=[plugin])
            # Retrieve plugin information
            docs = getattr(module, '__doc__', 'No docs available')
            version = getattr(module, '__version__', 'Unknown')
            author = getattr(module, '__author__', 'Unknown')
            author_discord_id = getattr(module, '__authorDiscordID__', 'Unknown')

            # Add plugin information to the embed
            pluginsEmbed.add_field(
                name=f"✅ {plugin}" if plugin in appliedPlugins else f"🚫 {plugin}",
                value=f"About: `{docs}`\nVersion: `{version}`\nAuthor: `{author}`\nAuthor Discord ID: `{author_discord_id}`",
                inline=False
            )
        await ctx.reply(embed=pluginsEmbed)
    
    @command(name = "load-plugin", aliases=["add-plugin","load"], description="Load any Plugin")
    @commands.cooldown(1, 10, commands.BucketType.member)
    @commands.has_permissions(administrator=True)
    async def load_plugin(self, ctx:Context,name: str):
        """Load a Plugin"""
        name =name.capitalize()
        file = Data(ctx.guild.id,"Plugins","Applied Plugins")
        appliedPlugins= file.data if file.data != None else []
        if name in appliedPlugins:
            await ctx.reply(embed= error_embed("This Plugin Is Already Loaded"
                                               ,"Error While Loading Plugin"))
            return
        elif name not in self.plugins:
            await ctx.reply(embed= error_embed(f"There is no Plugin Called `{name}`\
                \nIf you need help please use {prefix}plugins","Error While Loading Plugin"))
            return
        appliedPlugins.append(name)
        file.data = appliedPlugins
        file.save()
        await ctx.reply(embed=info_embed(f"{name} Plugin is Loaded!","Plugin Loaded"))
    @command(name = "unload-plugin", aliases=["remove-plugin","unload"],description="Unload any Plugin")
    @commands.cooldown(1, 10, commands.BucketType.member)
    @commands.has_permissions(administrator=True)
    async def unload_plugin(self, ctx:Context,name: str):
        """Unload a Plugin"""
        name =name.capitalize()
        file = Data(ctx.guild.id,"Plugins","Applied Plugins")
        appliedPlugins= file.data if file.data != None else []
        if name not in appliedPlugins:
            await ctx.reply(embed= error_embed("This Plugin Is Already Unloaded"
                                               ,"Error While Loading Plugin"))
            return
        file.data.remove(name)
        file.save()
        await ctx.reply(embed=info_embed(f"{name} Plugin is Unloaded!","Plugin Unloaded"))
        
    
    
        
            
    
    

def setup(client):
    client.add_cog(PluginsManager(client))