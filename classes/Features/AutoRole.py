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
            if not data:
                return
            if not data.enabled:
                return
            if member.bot and data.get_setting('bot_role') != None:
                return await member.add_roles(guild.get_role(data.get_setting("bot_role"))) # type: ignore
            await member.add_roles(guild.get_role(data.get_setting("member_role"))) # type: ignore
        except:
            return


def setup(client):
    client.add_cog(AutoRole(client))