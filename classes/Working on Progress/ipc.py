from nextcord import *
from nextcord.ext import commands, ipc  
from modules.Nexon import *

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