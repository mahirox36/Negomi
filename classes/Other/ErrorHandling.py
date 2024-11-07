import traceback
from nextcord import *
from nextcord.ext import commands
from nextcord import Interaction as init
from nextcord.ext.commands import MissingPermissions, NotOwner, NoPrivateMessage, PrivateMessageOnly
from nextcord.ext.application_checks import *
from modules.Side import *
from modules.Logger import *


class ErrorHandling(commands.Cog):
    def __init__(self, client:Client):
        self.client = client

    @commands.Cog.listener()
    async def on_application_command_error(self, ctx: init, error: Exception):
        try:
            err = error.original
        except AttributeError:
            err = error
        if isinstance(err, SlashCommandOnCooldown):
            await ctx.send(
                embed=error_embed(f"You're on cooldown! Try again in {err.time_left:.2f} seconds.", "Too Fast"),
                ephemeral=True)
            return
        elif isinstance(err, ApplicationMissingPermissions):
            missing = ", ".join(err.missing_permissions)
            await ctx.send(
                embed=error_embed(f"You don't have {missing}", "Missing Permissions"),
                ephemeral=True)
            return
        elif isinstance(err, ApplicationNotOwner):
            await ctx.send(
                embed=error_embed(f"You are not the owner of the bot", "Not Owner"),
                ephemeral=True)
            return
        elif isinstance(err, ApplicationNotOwnerGuild):
            await ctx.send(
                embed=error_embed(f"You are not the owner of the Server {err.guild}", "Not Owner of Server"),
                ephemeral=True)
            return
        elif isinstance(err, ApplicationNoPrivateMessage):
            await ctx.send(
                embed=error_embed(f"You can't Use this command in DM", "DM not Allowed"),
                ephemeral=True)
            return
        elif isinstance(err, ApplicationPrivateMessageOnly):
            await ctx.send(
                embed=error_embed(f"You Only Can Do this Command in DM", "DM Only"),
                ephemeral=True)
            return
        elif isinstance(error, FeatureDisabled):
            await ctx.send(
                embed=error_embed(f"This Feature is disabled",
                                  "Feature Disabled"))
            return 
        await ctx.send(embed=error_embed(error,title="An unexpected error occurred"))
        LOGGER.error(error)
    
        # Send detailed traceback to the bot owner
        tb_str = traceback.format_exception(type(error), error, error.__traceback__)
        error_details = "".join(tb_str)
        
        with open("logs/error_traceback.py", "w") as f:
            f.write(error_details)

        # Send the file to the bot owner
        BotInfo: AppInfo = await self.client.application_info()
        if BotInfo.owner.name.startswith("team"):
            user = self.client.get_user(BotInfo.team.owner.id)
            channel = await user.create_dm()
        else:
            channel = await BotInfo.owner.create_dm()

        await channel.send(content="New Error Master!", file=nextcord.File("logs/error_traceback.py"))

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: Exception):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.reply(f"You're on cooldown! Try again in {error.retry_after:.2f} seconds.")
            return
        elif isinstance(error, MissingPermissions):
            missing = ", ".join(error.missing_permissions)
            await ctx.send(
                embed=error_embed(f"You don't have {missing}", "Missing Permissions"))
            return
        elif isinstance(error, NotOwner):
            await ctx.send(
                embed=error_embed(f"You are not the owner of the bot", "Not Owner"))
            return
        elif isinstance(error, FeatureDisabled):
            await ctx.send(
                embed=error_embed(f"This Feature is disabled",
                                  "Feature Disabled"))
            return 
        # elif isinstance(error, NotOwnerGuild):
        #     await ctx.send(
        #         embed=error_embed(f"You are not the owner of the Server {error.guild}", "Not Owner of Server"),
        #         ephemeral=True)
        #     return
        elif isinstance(error, NoPrivateMessage):
            await ctx.send(
                embed=error_embed(f"You can't Use this command in DM", "DM not Allowed"),
                ephemeral=True)
            return
        elif isinstance(error, PrivateMessageOnly):
            await ctx.send(
                embed=error_embed(f"You Only Can Do this Command in DM", "DM Only"),
                ephemeral=True)
            return
        elif isinstance(error,commands.errors.CommandNotFound):
            return
        await ctx.reply(embed=error_embed(error,title="An unexpected error occurred"))
        LOGGER.error(error)
    
        # Send detailed traceback to the bot owner
        tb_str = traceback.format_exception(type(error), error, error.__traceback__)
        error_details = "".join(tb_str)
        
        with open("logs/error_traceback.py", "w") as f:
            f.write(error_details)

        # Send the file to the bot owner
        BotInfo: AppInfo = await self.client.application_info()
        if BotInfo.owner.name.startswith("team"):
            user = self.client.get_user(BotInfo.team.owner.id)
            channel = await user.create_dm()
        else:
            channel = await BotInfo.owner.create_dm()

        await channel.send(content="New Error Master!", file=nextcord.File("logs/error_traceback.py"))

    
    

def setup(client):
    client.add_cog(ErrorHandling(client))