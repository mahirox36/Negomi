"""From time to time It Refresh the Main Chat With 3 Methods"""
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

__version__ = 1.0
__author__= "Mahiro"
__authorDiscordID__ = 829806976702873621

class Refresh(commands.Cog):
    def __init__(self, client:Client):
        self.client = client
    
    @commands.command(name = "methods")
    @commands.has_permissions(administrator=True)
    @plugin()
    async def methods(self, ctx:commands.Context):
        await ctx.reply(embed=info_embed("These are the Three Methods You Can Use.","Methods")\
            .add_field(name="1. Don't Save Chat",value="Delete And Create The Chat without Saving it to a File or Archive Channel",inline=False)\
            .add_field(name="2. Save it as Archive", value="When it's time to Refresh it Move the original Channel To Archive Category and then \
                And then Clone the same Channel without it's messages to the same place as the old one",inline=False)\
            .add_field(name="3. Save it as Archive",value="Save it and send it as Zip File in a specific channel",inline=False)\
            .add_field(name="How do you use them?",value=f"After Typing `{prefix}add-refresh` you type first a channel and then type the number of the method then the Day Counter \
                an Example: `{prefix}add-refresh {ctx.channel.mention} 1 <days>`",inline=False))
    
    # @commands.command(name = "add-refresh")
    # @commands.has_permissions(administrator=True)
    # @plugin()
    # async def add_refresh(self, ctx:commands.Context,channel: TextChannel, method: int):
        
    
    

def setup(client):
    client.add_cog(Refresh(client))