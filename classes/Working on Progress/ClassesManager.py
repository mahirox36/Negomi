from nextcord import *
from nextcord.ext import commands
from nextcord import Interaction as init
from nextcord import SlashOption
from typing import List
from modules.Nexon import *

class ClassesManager(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.client = bot

    @slash_command("class", default_member_permissions=Permissions(8),dm_permission=False,guild_ids=TESTING_GUILD_ID)
    async def classSet(self,ctx: init):
        pass

    @classSet.subcommand(name="reload", description="Reload a bot class (Owner only).")
    async def reload_class(
        self,
        interaction: Interaction,
        class_name: str = SlashOption(
            name="class",
            description="Select the class to reload.",
            autocomplete=True
        ),
    ):
        """Reload a specific class."""
        # Ensure the command is only accessible to the bot owner
        if interaction.user.id != get_owner(self.client):
            await interaction.response.send_message("This command is restricted to the bot owner.", ephemeral=True)
            return

        # Try to reload the class
        try:
            self.client.reload_extension(f"classes.Features.{class_name}")
            await interaction.response.send_message(f"Successfully reloaded class: `{class_name}`", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Failed to reload class `{class_name}`.\nError: {e}", ephemeral=True)
        
        self.client.sync_all_application_commands()
        
    @reload_class.on_autocomplete("class_name")
    def class_autocomplete(self, interaction: Interaction, current: str) -> List[str]:
        """Provide a list of currently loaded Classes for autocompletion."""
        return [cog for cog in self.bot.cogs.keys() if current.value.lower() in cog.lower()]


# Setup function to add the class to the bot
def setup(bot: commands.Bot):
    bot.add_cog(ClassesManager(bot))
