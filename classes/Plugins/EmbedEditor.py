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
class EmbedEditor(commands.Cog):
    def __init__(self, client:Client):
        self.client = client
    
    
    @commands.command(name = "create-embed",
                    description = "Setup auto role for members and bots")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 10, commands.BucketType.member)
    @plugin()
    async def create_embed(self,ctx:init,member_role:Role,bot_role:Role = None):
        file= Data(ctx.guild_id,"Auto role")
        file.data = {
            "member_role":member_role.id,
            "bot_role"   :bot_role.id if bot_role else None
        }
        file.save()
        
        await ctx.send("Auto Role Set!")
    

def setup(client):
    client.add_cog(EmbedEditor(client))