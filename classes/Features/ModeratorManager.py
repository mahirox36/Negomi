from datetime import timedelta
from modules.Nexon import *


class ModeratorManager(commands.Cog):
    def __init__(self, client: Client):
        self.client = client
        self.logger = logging.getLogger(__name__)

    def generate_token(self):
        """Generate a new unique token"""
        better_id = IDManager("Moderator Manager", 42)
        return better_id.generate()

    # @slash_command(name="mod",default_member_permissions=Permissions(administrator=True))
    # async def moded(self, ctx:init):
    #     pass
    # @moded.subcommand(name="manager")
    # async def manager(self, ctx:init):
    #     pass


def setup(client):
    client.add_cog(ModeratorManager(client))
