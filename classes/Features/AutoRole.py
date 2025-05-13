from typing import cast
from modules.Nexon import *


class AutoRole(commands.Cog):
    def __init__(self, client: Bot):
        self.client = client

    @commands.Cog.listener()
    async def on_member_join(self, member: Member):
        guild = member.guild
        try:
            # Fetch the auto_role feature data for the guild
            data = await Feature.get_guild_feature(
                feature_name="auto_role",
                guild_id=guild.id,
            )


            # Check if the feature is enabled and properly configured
            if not data.enabled or not data.get_setting():
                return

            # Handle bot roles if the member is a bot
            if member.bot:
                bot_roles_ids = data.get_setting("botRoles")
                if bot_roles_ids:
                    bot_roles = [guild.get_role(role_id) or await guild.fetch_role(role_id) for role_id in bot_roles_ids]
                    bot_roles = [role for role in bot_roles if role]  # Filter out None values
                    if bot_roles:
                        await member.add_roles(*bot_roles)
                return

            # Handle user roles for non-bot members
            user_roles_ids = data.get_setting("userRoles")
            if user_roles_ids:
                user_roles = [guild.get_role(role_id) or await guild.fetch_role(role_id) for role_id in user_roles_ids]
                user_roles = [role for role in user_roles if role]  # Filter out None values
                if user_roles:
                    await member.add_roles(*user_roles)
                else:
                    logger.warning(f"No valid user roles found for {member}.")
            else:
                logger.warning(f"Invalid or missing userRoles setting: {user_roles_ids}")

        except Exception as e:
            logger.error(f"Error in AutoRole on_member_join: {e}", exc_info=True)
            console.print_exception()


def setup(client):
    client.add_cog(AutoRole(client))
