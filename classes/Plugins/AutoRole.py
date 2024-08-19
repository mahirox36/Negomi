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

    @commands.command(name = "setup-auto-role",
                    aliases=["auto role"],
                    description = "Setup auto role for members and bots")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 10, commands.BucketType.member)
    @plugin()
    async def setup_auto_role(self,ctx:init,member_role:Role,bot_role:Role = None):
        file= Data(ctx.guild_id,"Auto role")
        file.data = {
            "member_role":member_role.id,
            "bot_role"   :bot_role.id if bot_role else None
        }
        file.save()
        
        await ctx.send("Auto Role Set!")
        
            
    @commands.Cog.listener()
    async def on_member_join(self, member:Member):
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