import nextcord
import nextcord as discord
from nextcord import *
from nextcord.ext import commands
from nextcord import Interaction as init
from Lib.Side import *
from Lib.Hybrid import setup_hybrid, userCTX
import os
import json

class Invite(commands.Cog):
    def __init__(self, client:Client):
        self.client = client
    
    @commands.command(name = "setup-invite",
                    description = "Setup Invite System to save ...") #FIXME
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 10, commands.BucketType.member)
    async def setup_invite(self, ctx:commands.Context):
        await ctx.send("template command")
    
    

def setup(client):
    client.add_cog(Invite(client))