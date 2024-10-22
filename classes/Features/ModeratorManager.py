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
#TODO: Add a way to add and remove moderators easily
#TODO: Make it easy to Upgrade and Downgrade moderators
#TODO: If the Mod got hacked, and want to return to the server, we should have a way to get him back and the hacker get banned
#TODO: Commands Left: [add, remove, upgrade, downgrade, hacked, list, info]
class MM(commands.Cog):
    def __init__(self, client:Client):
        self.client = client
        self.logger = LOGGER
    
    @slash_command(name="mod",default_member_permissions=Permissions(administrator=True))
    async def moded(self, ctx:init):
        pass
    @moded.subcommand(name="manager")
    async def manager(self, ctx:init):
        pass
    
    @manager.subcommand("setup", "Setup the Moderator Manager")
    async def setup(self, ctx:init,
                    staffRole:Role  = SlashOption("staff"   , "Role for staff members"   ,required=False),
                    trailRole:Role  = SlashOption("trail"   , "Role for trail mod"   ,required=False),
                    modRole:Role    = SlashOption("mod"     , "Role for Mod"   ,required=False),
                    highModRole:Role= SlashOption("high_mod", "Role for High mod"   ,required=False),
                    adminRole:Role  = SlashOption("admin"   , "Role for Admin"   ,required=False)):
        await ctx.response.defer(ephemeral=True)
        guild = ctx.guild
        if adminRole == None:
            adminRole= await guild.create_role(name="Admin",
                                               permissions=Permissions(administrator=True),
                                               color=0x0EE08B, hoist=True)
        if highModRole == None:
            highModRole= await guild.create_role(name="High Moderator",
                                                 permissions=Permissions(moderate_members=True, kick_members=True,
                                                                         ban_members=True, manage_messages=True, manage_nicknames=True,
                                                                         view_audit_log=True, manage_threads=True,
                                                                         mute_members=True, move_members=True, deafen_members=True),
                                                 color=0x824040, hoist=True)
        if modRole == None:
            modRole= await guild.create_role(name="Moderator",
                                             permissions=Permissions(moderate_members=True, kick_members=True,
                                                                     manage_messages=True, manage_nicknames=True,
                                                                     manage_threads=True, mute_members=True),
                                             color=0xFF7D7D, hoist=True)
        if trailRole == None:
            trailRole= await guild.create_role(name="Trail Moderator",
                                               permissions=Permissions(moderate_members=True, manage_messages=True),
                                               color=0x5C5CFF, hoist=True)
            PermissionOverwriteWith()
        if staffRole == None:
            staffRole= await guild.create_role(name="Staff")
        file = Data(ctx.guild_id, "Moderator Manager")
        file.data = {
            "staff": staffRole.id if staffRole else None,
            "trail": trailRole.id if trailRole else None,
            "mod": modRole.id if modRole else None,
            "high": highModRole.id if highModRole else None,
            "admin": adminRole.id if adminRole else None
        }
        file.save()
        await ctx.send(embed=info_embed("Moderator Manager setup successfully", "Moderator Manager"))
    @manager.subcommand("add", "Add a Moderator")
    async def add(self, ctx:init, member:Member, role:Role= None):
        file = Data(ctx.guild_id, "Moderator Manager", "users", default={})
        data = file.load()
        if data == None:
            await ctx.send(embed=error_embed("Moderator Manager is not setup yet", "Moderator Manager"))
            return
        if role.id not in data.values():
            await ctx.send(embed=error_embed("This role is not a Moderator role", "Moderator Manager"))
            return
        if member.id in data.keys():
            
            await ctx.send(embed=error_embed("This member is already a Moderator", "Moderator Manager"))
            return
        BetterId= BetterID("Moderator Manager",42)
        token= BetterId.generate()
            
        data= {
            "currentRole": role.id,
            "token": token,
            "since": ctx.created_at,
            "by": ctx.user.id,
            "pastRoles": []
        }
        data[member.id] = data
        file.save()
        await ctx.send(embed=info_embed(f"{member.mention} is now a {role.mention}", "Moderator Manager"))    
    

def setup(client):
    client.add_cog(MM(client))