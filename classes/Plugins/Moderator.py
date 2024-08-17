"""
Simple Moderation Plugin"""
from datetime import timedelta
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

class Moderator(commands.Cog):
    def __init__(self, client: Client):
        self.client = client

    @command(name="kick", description="Kick a member from the server")
    @commands.has_permissions(kick_members=True)
    @plugin()  # Custom plugin check
    async def kick(self, ctx: Context, user: Member, *, reason: str = "No reason provided"):
        guild = ctx.guild
        if ctx.author.top_role.position <= user.top_role.position:
            await ctx.reply(embed=error_embed("You cannot kick this user due to role hierarchy.", "Kick Error"))
            return

        try:
            await user.kick(reason=reason)
            await ctx.send(embed=info_embed(f"Successfully kicked {user.mention} for: {reason}", "Kick Success"))
            log_action("Kick", ctx.author, user, reason)  # Logging the action
        except nextcord.Forbidden:
            await ctx.reply(embed=error_embed("I do not have permission to kick this user.", "Kick Error"))
        except Exception as e:
            await ctx.reply(embed=error_embed(f"An error occurred: {str(e)}", "Kick Error"))

    @command(name="ban", description="Ban a member from the server")
    @commands.has_permissions(ban_members=True)
    @plugin()
    async def ban(self, ctx: Context, user: Member, *, reason: str = "No reason provided"):
        if ctx.author.top_role.position <= user.top_role.position:
            await ctx.reply(embed=error_embed("You cannot ban this user due to role hierarchy.", "Ban Error"))
            return

        try:
            await user.ban(reason=reason)
            await ctx.send(embed=info_embed(f"Successfully banned {user.mention} for: {reason}", "Ban Success"))
            log_action("Ban", ctx.author, user, reason)  # Logging the action
        except nextcord.Forbidden:
            await ctx.reply(embed=error_embed("I do not have permission to ban this user.", "Ban Error"))
        except Exception as e:
            await ctx.reply(embed=error_embed(f"An error occurred: {str(e)}", "Ban Error"))

    @command(name="unban", description="Unban a member from the server")
    @commands.has_permissions(ban_members=True)
    @plugin()
    async def unban(self, ctx: Context, *, user: str):
        banned_users = await ctx.guild.bans()
        user_name, user_discriminator = user.split('#')

        for ban_entry in banned_users:
            banned_user = ban_entry.user

            if (banned_user.name, banned_user.discriminator) == (user_name, user_discriminator):
                await ctx.guild.unban(banned_user)
                await ctx.send(embed=info_embed(f"Successfully unbanned {banned_user.mention}", "Unban Success"))
                log_action("Unban", ctx.author, banned_user, "Unban")  # Logging the action
                return
        
        await ctx.reply(embed=error_embed(f"User {user} not found in the ban list.", "Unban Error"))
        
    @command(name="mute", description="Mute a member in the server")
    @commands.has_permissions(manage_roles=True)
    @plugin()
    async def mute(self, ctx: Context, user: Member, *, reason: str = "No reason provided"):
        mute_role = nextcord.utils.get(ctx.guild.roles, name="Muted")

        if not mute_role:
            mute_role = await ctx.guild.create_role(name="Muted")
            for channel in ctx.guild.channels:
                await channel.set_permissions(mute_role, speak=False, send_messages=False)

        if mute_role in user.roles:
            await ctx.reply(embed=error_embed(f"{user.mention} is already muted.", "Mute Error"))
            return

        await user.add_roles(mute_role, reason=reason)
        await ctx.send(embed=info_embed(f"{user.mention} has been muted for: {reason}", "Mute Success"))
        log_action("Mute", ctx.author, user, reason)  # Logging the action

    @command(name="unmute", description="Unmute a member in the server")
    @commands.has_permissions(manage_roles=True)
    @plugin()
    async def unmute(self, ctx: Context, user: Member):
        mute_role = nextcord.utils.get(ctx.guild.roles, name="Muted")

        if mute_role not in user.roles:
            await ctx.reply(embed=error_embed(f"{user.mention} is not muted.", "Unmute Error"))
            return

        await user.remove_roles(mute_role)
        await ctx.send(embed=info_embed(f"{user.mention} has been unmuted.", "Unmute Success"))
        log_action("Unmute", ctx.author, user, "Unmute")  # Logging the action
    
    @command(name="timeout", description="Timeout a member for a specified duration")
    @commands.has_permissions(moderate_members=True)
    @plugin()
    async def timeout(self, ctx: Context, user: Member, duration: int, unit: str, *, reason: str = "No reason provided"):
        time_units = {
            "s": timedelta(seconds=duration),
            "sec": timedelta(seconds=duration),
            "secs": timedelta(seconds=duration),
            "m": timedelta(minutes=duration),
            "min": timedelta(minutes=duration),
            "mins": timedelta(minutes=duration),
            "h": timedelta(hours=duration),
            "hour": timedelta(hours=duration),
            "hours": timedelta(hours=duration),
            "d": timedelta(days=duration),
            "day": timedelta(days=duration),
            "days": timedelta(days=duration)
        }

        if unit not in time_units:
            await ctx.reply(embed=error_embed(f"Invalid time unit. Use 's', 'm', 'h', or 'd'.", "Timeout Error"))
            return

        if ctx.author.top_role.position <= user.top_role.position:
            await ctx.reply(embed=error_embed("You cannot timeout this user due to role hierarchy.", "Timeout Error"))
            return

        try:
            await user.timeout_for(time_units[unit], reason=reason)
            await ctx.send(embed=info_embed(f"{user.mention} has been timed out for {duration}{unit} for: {reason}", "Timeout Success"))
            log_action("Timeout", ctx.author, user, reason)
        except nextcord.Forbidden:
            await ctx.reply(embed=error_embed("I do not have permission to timeout this user.", "Timeout Error"))
        except Exception as e:
            await ctx.reply(embed=error_embed(f"An error occurred: {str(e)}", "Timeout Error"))

# Ensure the cog is properly set up
def setup(client):
    client.add_cog(Moderator(client))