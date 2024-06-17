from datetime import datetime
from nextcord import *
import nextcord as discord
from nextcord.ext import commands
from nextcord import Interaction as init
from Lib.Side import *
from Lib.Data import Data
import os
import json

class Moderation(commands.Cog):
    def __init__(self, client:Client):
        self.client = client
    async def kick_command(self,ctx:init | commands.Context,user:Member,reason:str=None):
        if ctx.user.guild_permissions.kick_members:
            if (ctx.user.top_role.position > user.top_role.position) or \
                (ctx.user.id == ctx.guild.owner_id):
                reason = "No Reason Provided" if reason == None else reason
                await user.kick(reason=reason)
                await ctx.send(f"Kicked {user.mention} for {reason}")
            else:
                await ctx.send(embed=error_embed("You can't kick someone with a higher role than you."
                                                 ,title="Permission Error")
                               ,ephemeral=True)
        else:
            await ctx.send(embed=error_embed("You don't have permission to kick members.",title="Permission Error"),ephemeral=True)
    
    @slash_command(name="kick",description="Kick a user from the server.")
    async def kick_slash(self,ctx:init,user:Member,reason:str=None):
        await self.kick_command(ctx,user,reason)
    @commands.command(name="kick",description="Kick a user from the server.")
    async def kick(self,ctx:commands.Context,user:Member,reason:str=None):
        ctx.user = ctx.author
        await self.kick_command(ctx,user,reason)
    
    async def ban_command(self,ctx:init | commands.Context,user:Member,reason:str=None):
        if ctx.user.guild_permissions.ban_members:
            if (ctx.user.top_role.position > user.top_role.position) or \
                (ctx.user.id == ctx.guild.owner_id):
                reason = "No Reason Provided" if reason == None else reason
                await user.ban(reason=reason)
                await ctx.send(f"Banned {user.mention} for {reason}")
            else:
                await ctx.send(embed=error_embed("You can't ban someone with a higher role than you."
                                                 ,title="Permission Error")
                               ,ephemeral=True)
        else:
            await ctx.send(embed=error_embed("You don't have permission to ban members.",title="Permission Error"),ephemeral=True)
    
    @slash_command(name="ban",description="Ban a user from the server.")
    async def ban_slash(self,ctx:init,user:Member,reason:str=None):
        await self.ban_command(ctx,user,reason)
    @commands.command(name="ban",description="Ban a user from the server.")
    async def ban(self,ctx:commands.Context,user:Member,reason:str=None):
        ctx.user = ctx.author
        await self.ban_command(ctx,user,reason)
    
    async def unban_command(self,ctx:init | commands.Context,user:User,reason:str=None):
        if ctx.user.guild_permissions.ban_members:
            reason = "No Reason Provided" if reason == None else reason
            await ctx.guild.unban(user,reason=reason)
            await ctx.send(f"Unbanned {user.mention} for {reason}")
        else:
            await ctx.send(embed=error_embed("You don't have permission to unban members.",title="Permission Error"),ephemeral=True)
    
    @slash_command(name="unban",description="Unban a user from the server.")
    async def unban_slash(self,ctx:init,user:User,reason:str=None):
        await self.unban_command(ctx,user,reason)
    @commands.command(name="unban",description="Unban a user from the server.")
    async def unban(self,ctx:commands.Context,user:User,reason:str=None):
        ctx.user = ctx.author
        await self.unban_command(ctx,user,reason)
    
    async def mute_command(self,ctx:init | commands.Context,user:Member,time:int,reason:str=None):
        if ctx.user.guild_permissions.manage_roles:
            if (ctx.user.top_role.position > user.top_role.position) or \
                (ctx.user.id == ctx.guild.owner_id):
                reason = "No Reason Provided" if reason == None else reason
                user.timeout(time,reason=reason)
                await ctx.send(f"Muted {user.mention} for {reason}")
            else:
                await ctx.send(embed=error_embed("You can't mute someone with a higher role than you."
                                                 ,title="Permission Error")
                               ,ephemeral=True)
        else:
            await ctx.send(embed=error_embed("You don't have permission to mute members.",title="Permission Error"),ephemeral=True)
    
    # @slash_command(name="mute",description="Mute a user in the server.")
    # async def mute_slash(self,ctx:init,user:Member,time:int,reason:str=None):
    #     await self.mute_command(ctx,user,time,reason)
    # @commands.command(name="mute",description="Mute a user in the server.")
    # async def mute(self,ctx:commands.Context,user:Member,time:int,reason:str=None):
    #     ctx.user = ctx.author
    #     await self.mute_command(ctx,user,time,reason)
    
    async def unmute_command(self,ctx:init | commands.Context,user:Member,reason:str=None):
        if ctx.user.guild_permissions.manage_roles:
            if (ctx.user.top_role.position > user.top_role.position) or \
                (ctx.user.id == ctx.guild.owner_id):
                reason = "No Reason Provided" if reason == None else reason
                user.timeout(0,reason=reason)
                await ctx.send(f"Unmuted {user.mention} for {reason}")
            else:
                await ctx.send(embed=error_embed("You can't unmute someone with a higher role than you."
                                                 ,title="Permission Error")
                               ,ephemeral=True)
        else:
            await ctx.send(embed=error_embed("You don't have permission to unmute members.",title="Permission Error"),ephemeral=True)

    # @slash_command(name="unmute",description="Unmute a user in the server.")
    # async def unmute_slash(self,ctx:init,user:Member,reason:str=None):
    #     await self.unmute_command(ctx,user,reason)
    # @commands.command(name="unmute",description="Unmute a user in the server.")
    # async def unmute(self,ctx:commands.Context,user:Member,reason:str=None):
    #     ctx.user = ctx.author
    #     await self.unmute_command(ctx,user,reason)

    async def warn_command(self,ctx:init | commands.Context,user:Member,
                           reason:str=None,proof:str=None,duration:str=None,
                           note:str=None):
        
        if ctx.user.guild_permissions.kick_members:
            if (ctx.user.top_role.position > user.top_role.position) or \
                (ctx.user.id == ctx.guild.owner_id):
                reason = "No Reason Provided" if reason == None else reason  
                current_datetime = datetime.now()
                date = str(current_datetime.strftime("%Y-%m-%d"))
                timed = str(current_datetime.strftime("%H-%M-%S-%f"))
                try:
                    ID = BetterID()
                    data = {
                        user.id: {
                            "reason": reason,
                            "date": date,
                            "time": timed,
                            "mod": ctx.user.id,
                            "proof": proof if proof else "No Proof Provided",
                            "duration": convert_to_seconds(duration) if duration else -1,
                            "note":note if note else "No Note Provided"
                        }
                    }
                except ValueError as e:
                    await ctx.send(embed=error_embed(f"Invalid Duration Provided.\n||{e}||",title="Duration Error"),ephemeral=True)
                    return
                except Exception as e:
                    await ctx.send(embed=error_embed(f"An Error Occurred.\n||{e}||",title="Error"),ephemeral=True)
                    return 
                warns = Data(ctx.guild.id,"warnings")
                warns[user.id].update(data)
                await ctx.send(f"Warned {user.mention} for {reason}")
                warns.save()
            else:
                await ctx.send(embed=error_embed("You can't warn someone with a higher role than you."
                                                 ,title="Permission Error")
                               ,ephemeral=True)
        else:
            await ctx.send(embed=error_embed("You don't have permission to warn members.",title="Permission Error"),ephemeral=True)

    @slash_command(name="warn",description="Warn a user in the server.")
    async def warn_slash(self,ctx:init,user:Member,
                           reason:str=None,duration:str=None,
                           note:str=None):
        await self.warn_command(ctx,user,reason,duration=duration,note=note)
    @commands.command(name="warn",description="Warn a user in the server.")
    async def warn(self,ctx:commands.Context,user:Member,
                           reason:str=None,duration:str=None,
                           note:str=None):
        ctx.user = ctx.author
        await self.warn_command(ctx,user,reason,duration=duration,note=note)

    async def unwarn_command(self,ctx:init | commands.Context,user:Member,reason:str=None):
        if ctx.user.guild_permissions.kick_members:
            if (ctx.user.top_role.position > user.top_role.position) or \
                (ctx.user.id == ctx.guild.owner_id):
                reason = "No Reason Provided" if reason == None else reason
                with open(f"warnings/{user.id}.json","r") as f:
                    warnings = json.load(f)
                warnings.pop()
                with open(f"warnings/{user.id}.json","w") as f:
                    json.dump(warnings,f)
                await ctx.send(f"Unwarned {user.mention} for {reason}")
            else:
                await ctx.send(embed=error_embed("You can't unwarn someone with a higher role than you."
                                                 ,title="Permission Error")
                               ,ephemeral=True)
        else:
            await ctx.send(embed=error_embed("You don't have permission to unwarn members.",title="Permission Error"),ephemeral=True)

    @slash_command(name="unwarn",description="Unwarn a user in the server.")
    async def unwarn_slash(self,ctx:init,user:Member,reason:str=None):
        await self.unwarn_command(ctx,user,reason)
    @commands.command(name="unwarn",description="Unwarn a user in the server.")
    async def unwarn(self,ctx:commands.Context,user:Member,reason:str=None):
        ctx.user = ctx.author
        await self.unwarn_command(ctx,user,reason)

    async def clear_command(self,ctx:init | commands.Context,amount:int):
        if ctx.user.guild_permissions.manage_messages:
            await ctx.channel.purge(limit=amount)
            await ctx.send(f"Cleared {amount} messages.")
        else:
            await ctx.send(embed=error_embed("You don't have permission to clear messages.",title="Permission Error"),ephemeral=True)

    @slash_command(name="clear",description="Clear messages in the channel.")
    async def clear_slash(self,ctx:init,amount:int):
        await self.clear_command(ctx,amount)
    @commands.command(name="clear",description="Clear messages in the channel.",aliases=["purge"])
    async def clear(self,ctx:commands.Context,amount:int):
        ctx.user = ctx.author
        await self.clear_command(ctx,amount)
    


def setup(client):
    client.add_cog(Moderation(client))