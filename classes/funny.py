import nextcord
import nextcord as discord
from nextcord import *
from nextcord.ext import commands
from nextcord import Interaction as init
from Lib.Side import *
from Lib.Hybrid import setup_hybrid, userCTX
import os
import json
from Main import Bot
Hybrid = setup_hybrid(Bot)

class funny(commands.Cog):
    def __init__(self, client:commands.Bot):
        self.client = client
    @slash_command("uwu",description="What Does this thing do?")
    async def uwu2(self,ctx:init):
        await ctx.send("UwU")
    
    

def setup(client):
    client.add_cog(funny(client))