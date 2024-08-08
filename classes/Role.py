import nextcord
import nextcord as discord
from nextcord import *
from nextcord.ext import commands
from nextcord import Interaction as init, SlashOption
from Lib.Data import Data
from Lib.Side import *
from Lib.Hybrid import setup_hybrid, userCTX
from Lib.config import Color
import os
import json

class Rolez(commands.Cog):
    def __init__(self, client:Client):
        self.client = client
        #Not allowed Words for roles
        self.notAllowed = ["nigga","niggers","nigger","gay","femboy","femboys",
                           "trans","transgender","kiss","sex","strip"]
        self.colors = {
    "Red": Color("#FF0000"),"Green": Color("#008000"),"Blue": Color("#0000FF"),"Yellow": Color("#FFFF00"),"Cyan": Color("#00FFFF"),
    "Magenta": Color("#FF00FF"),"Orange": Color("#FFA500"),"Purple": Color("#800080"),"Pink": Color("#FFC0CB"),"Brown": Color("#A52A2A"),
    "Gray": Color("#808080"),"Black": Color("#000000"),"White": Color("#FFFFFF"),"Lime": Color("#00FF00"),"Olive": Color("#808000"),
    "Navy": Color("#000080"),"Teal": Color("#008080"),"Maroon": Color("#800000"),"Silver": Color("#C0C0C0"),"Gold": Color("#FFD700"),
    "Coral": Color("#FF7F50"),"Salmon": Color("#FA8072"),"Turquoise": Color("#40E0D0"),"Indigo": Color("#4B0082"),"Violet": Color("#EE82EE")}
    
    @slash_command(name="role-create",description="Create a role for your self")
    async def create_role(self,ctx:init,name:str,color:str=SlashOption("color","Type Hex code or one of these colors",
                                        required=True, autocomplete=True)):
        guild = ctx.guild
        color = self.colors[color]
        file = Data(guild.id,"Roles","MembersRoles")
        if file.data != None:
            if file.data.get(f"{ctx.user.id}") != None:
                await ctx.send(embed=error_embed("You already have a role"),ephemeral=True)
                return
        if name.lower() in self.notAllowed:
            await ctx.send(embed=error_embed("This word isn't allowed"),ephemeral=True)
            return
        role = await guild.create_role(reason=f"{ctx.user.name}/{ctx.user.id} Created a role",
                                name=name, color=color.value)
        await ctx.send(embed=info_embed(f"You have created a role by the name: {name}", title="Role Created!"))
        data= {f"{ctx.user.id}":{
            "owner":True,
            "roleID":role.id
        }}
        file.data.update(data) if file.data != None else file.data = data
    @create_role.on_autocomplete("color")
    async def name_autocomplete(self, interaction: nextcord.Interaction, current: str):
        # Example list of names
        colors = [i for i in self.colors.keys()]
        # Filter and return names that match the user's input
        suggestions = [name for name in colors if name.lower().startswith(current.lower())]
        await interaction.response.send_autocomplete(suggestions)
    
    

def setup(client):
    client.add_cog(Rolez(client))