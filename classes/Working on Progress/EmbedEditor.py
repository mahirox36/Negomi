import nextcord
import nextcord as discord
from nextcord import *
from nextcord.ext import commands
from nextcord.ext.commands import Context, command
from nextcord.ext.application_checks import *
from nextcord import Interaction as init
from modules.Side import *
from modules.Logger import *
import os
import json

class EmbedEditorModal(ui.Modal):
    def __init__(self,code):
        super().__init__("New Embed")
        self.name = ui.TextInput("Name", placeholder="Name of the Embed")
        self.color = ui.TextInput("Color", placeholder="Color of the Embed")
        
        self.add_item(self.name)
        self.add_item(self.color)

    async def callback(self, ctx: init):
        pass


class EmbedEditor(commands.Cog):
    def __init__(self, client:Client):
        self.client = client
        # self.colors = {
        # "Red": Color("#FF0000"),"Green": Color("#008000"),"Blue": Color("#0000FF"),"Yellow": Color("#FFFF00"),"Cyan": Color("#00FFFF"),
        # "Magenta": Color("#FF00FF"),"Orange": Color("#FFA500"),"Purple": Color("#800080"),"Pink": Color("#FFC0CB"),"Brown": Color("#A52A2A"),
        # "Gray": Color("#808080"),"Black": Color("#000001"),"White": Color("#FFFFFF"),"Lime": Color("#00FF00"),"Olive": Color("#808000"),
        # "Navy": Color("#000080"),"Teal": Color("#008080"),"Maroon": Color("#800000"),"Silver": Color("#C0C0C0"),"Gold": Color("#FFD700"),
        # "Coral": Color("#FF7F50"),"Salmon": Color("#FA8072"),"Turquoise": Color("#40E0D0"),"Indigo": Color("#4B0082"),"Violet": Color("#EE82EE")}
    @slash_command(name="embed", default_member_permissions=Permissions(administrator=True))
    async def embed(self,ctx:init):
        pass
    
    @embed.subcommand(name = "create",description = "Create a embed")
    @guild_only()
    @cooldown(10)
    async def create_embed(self,ctx:init):
        bid= BetterID("EmbedEditor")
        code= bid.create_random_id()
        await ctx.send(embed=info_embed("Please fill the following information to create a new embed", "New Embed"),view=EmbedEditorModal(code))
        
    
    
    
    # @create_embed.on_autocomplete("color")
    # async def name_autocomplete(self, interaction: nextcord.Interaction, current: str):
    #     colors = [i for i in self.colors.keys()]
    #     suggestions = [name for name in colors if name.lower().startswith(current.lower())]
    #     if (suggestions == []) and (current.startswith("#")):
    #          suggestions = [current]
    #     await interaction.response.send_autocomplete(suggestions)
    

def setup(client):
    client.add_cog(EmbedEditor(client))