from typing import cast
from modules.Nexon import *
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
            logger.info(f"AutoRole: {data}")
            if not data.get_setting():
                return
            if not data.enabled:
                return
            if member.bot and data.get_setting('botRoles') is not None:
                bot_roles = guild.get_role(data.get_setting("botRoles"))
                if bot_roles and isinstance(bot_roles, list):
                    for bot_role in bot_roles:
                        if bot_role not in member.roles:
                            await member.add_roles(bot_role)
                else:
                    return
            user_roles = data.get_setting("userRoles")
            if isinstance(user_roles, list):
                for role_id in user_roles:
                    user_role = guild.get_role(role_id)
                    if user_role:
                        await member.add_roles(user_role)
                    else:
                        logger.info(f"User role with ID {role_id} not found.")
            else:
                logger.info(f"Invalid userRoles setting: {user_roles}")
        except Exception as e:
            console.print_exception()
            logger.error(f"Error in AutoRole: {e}")
            return


def setup(client):
    client.add_cog(AutoRole(client))