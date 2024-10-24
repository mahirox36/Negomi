from nextcord import *
import nextcord as discord
from nextcord.ext import commands
from nextcord import Interaction as init
from Lib.Side import *
import os
import json

class AutoRole(commands.Cog):
    def __init__(self, client:Client):
        self.client = client

    @slash_command(name="auto",default_member_permissions=Permissions(administrator=True))
    async def auto(self,ctx:init):
        pass
    @auto.subcommand(name="role")
    async def role(self,ctx:init):
        pass

    @role.subcommand(name="setup",
                   description="Setup auto role for members and bots")
    @feature()
    async def setup_auto_role(self,ctx:init,member_role:Role,bot_role:Role = None):
        file= Data(ctx.guild_id,"Auto role")
        file.data = {
            "member_role":member_role.id,
            "bot_role"   :bot_role.id if bot_role else None
        }
        file.save()
        
        await ctx.send(embed=info_embed("Auto role setup successfully"))
        
            
    @commands.Cog.listener()
    async def on_member_join(self, member:Member):
        featureInside(member.guild.id)
        guild = member.guild
        if Data(member.guild.id,"Auto role").check():
            data = Data(member.guild.id,"Auto role").load()
            if data == None:
                return
            if (member.bot) and (data["bot_role"] != None):
                await member.add_roles(guild.get_role(data["bot_role"]))
            if member.bot == False:
                await member.add_roles(guild.get_role(data["member_role"]))


def setup(client):
    client.add_cog(AutoRole(client))