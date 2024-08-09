import traceback
from nextcord import *
from nextcord.ext import commands
from nextcord import Interaction as init
from Lib.Side import *
from Lib.Logger import *

class ErrorHandling(commands.Cog):
    def __init__(self, client:Client):
        self.client = client
    
    @commands.command(name = "error",
                    aliases=["e"],
                    description = "Nothing")
    @commands.is_owner()
    async def commandName(self, ctx:commands.Context):
        1 / 0


    @commands.Cog.listener()
    async def on_application_command_error(self, ctx: init, error: Exception):
        await ctx.send(embed=error_embed(error,title="Error Occurred"))
        LOGGER.error(error)
        tb_str = traceback.format_exception(error,value=error, tb=error.__traceback__)
        error_details = "```vbnet\n"+"".join(tb_str)+"```"
        
        user = self.client.get_user(owner_id)
        channel = await user.create_dm()
        await channel.send(f"New Error Master!\n{error_details}")

    @commands.Cog.listener()
    async def on_command_error(self, ctx: init, error: Exception):
        if isinstance(error,commands.errors.CommandNotFound):
            return
        await ctx.send(embed=error_embed(error,title="Error Occurred"))
        LOGGER.error(error)
        tb_str = traceback.format_exception(error,value=error, tb=error.__traceback__)
        error_details = "```vbnet\n"+"".join(tb_str)+"```"
        
        user = self.client.get_user(owner_id)
        channel = await user.create_dm()
        await channel.send(f"New Error Master!\n{error_details}")

    
    

def setup(client):
    client.add_cog(ErrorHandling(client))