from typing import cast
from modules.Nexon import *
from 
class AutoRole(commands.Cog):
    def __init__(self, client:Bot):
        self.client = client
        
    @commands.Cog.listener()
    async def on_member_join(self, member:Member):
        guild = member.guild
        try:
            data = await Feature.get_guild_feature(
                feature_name="auto_role",
                guild_id=guild.id,
            )
            if not data.get_setting():
                return
            if not data.enabled:
                return
            if member.bot and data.get_setting('botRoles') is not None:
                bot_role = guild.get_role(data.get_setting("botRoles"))
                if bot_role:
                    return await member.add_roles(bot_role)
                else:
                    return
            user_role = guild.get_role(data.get_setting("userRoles"))
            if user_role:
                await member.add_roles(user_role)
            else:
                logger.info(f"User role with ID {data.get_setting('userRoles')} not found.")
        except Exception as e:
            console.print_exception()
            logger.error(f"Error in AutoRole: {e}")
            return


def setup(client):
    client.add_cog(AutoRole(client))