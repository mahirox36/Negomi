import nextcord
import nextcord as discord
from nextcord import *
from nextcord.ext import commands, ipc  
from nextcord.ext.commands import Context, command
from nextcord.ext.application_checks import *
from nextcord import Interaction as init
from modules.Nexon import *
import os
import json

class IpcRoutes(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @ipc.server.route()
    async def get_member_count(self, data):
        guild = self.client.get_guild(data.guild_id)

        return guild.member_count
    @ipc.server.route()
    async def get_guilds_count(self, data):
        return len(self.client.guilds)
    

def setup(client):
    client.add_cog(IpcRoutes(client))