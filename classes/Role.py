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
        try:
            if file.data.get(f"{ctx.user.id}") != None:
                await ctx.send(embed=error_embed("You already have a role"),ephemeral=True)
                return
        except AttributeError: file.data = {}
        if name.lower() in self.notAllowed:
            await ctx.send(embed=error_embed("This word/name isn't allowed"),ephemeral=True)
            return
        role = await guild.create_role(reason=f"{ctx.user.name}/{ctx.user.id} Created a role",
                                name=name, color=color.value,hoist=True)
        await ctx.user.add_roles(role)
        await ctx.send(embed=info_embed(f"You have created a role by the name: {name}", title="Role Created!"),ephemeral=True)
        data= {f"{ctx.user.id}":{
            "owner"     :True,
            "roleID"    :role.id,
            "members"   :[]
        }}
        file.data.update(data)
        file.save()
    
    @slash_command(name="role-edit",description="Edit your own role like the name or role or both!")
    async def role_edit(self,ctx:init,name:str=None,color:str=SlashOption("color","Type Hex code or one of these colors",
                                        required=False, autocomplete=True,default=None)):
        guild = ctx.guild
        if color != None:
            color = self.colors[color]
        file = Data(guild.id,"Roles","MembersRoles")
        try:
            user = file.data.get(f"{ctx.user.id}")
            if user == None:
                await ctx.send(embed=error_embed("You Don't have a role"),ephemeral=True)
                return
            if user["owner"] == False:
                await ctx.send(embed=error_embed("You aren't the owner of the Role"),ephemeral=True)
                return
        except AttributeError: 
            await ctx.send(embed=error_embed("You Don't have a role"),ephemeral=True)
            return
        try:
            if name.lower() in self.notAllowed:
                await ctx.send(embed=error_embed("This word/name isn't allowed"),ephemeral=True)
                return
        except AttributeError:pass
        role = guild.get_role(user["roleID"])
        if (name == None) and (color == None):
            await ctx.send(embed=error_embed("you haven't change anything ||trying to be funny?||"),ephemeral=True)
            return
        if name != None:await role.edit(name=name)
        if color!= None:await role.edit(color=color)
        await ctx.send(embed=info_embed(f"You have Edit a role by the name", title="Role Edited!"),ephemeral=True)


    @slash_command(name="role-delete",description="delete your own role")
    async def role_delete(self,ctx:init):
        guild = ctx.guild
        file = Data(guild.id,"Roles","MembersRoles")
        try:
            user = file.data.get(f"{ctx.user.id}")
            if user == None:
                await ctx.send(embed=error_embed("You Don't have a role"),ephemeral=True)
                return
            if user["owner"] == False:
                await ctx.send(embed=error_embed("You aren't the owner of the Role"),ephemeral=True)
                return
        except AttributeError: 
            await ctx.send(embed=error_embed("You Don't have a role"),ephemeral=True)
            return
        role = guild.get_role(user["roleID"])
        await role.delete(reason=f"{ctx.user.name}/{ctx.user.id} deleted a role")
        await ctx.send(embed=info_embed(f"You have deleted the role", title="Role Deleted!"),ephemeral=True)
        for i in user["members"]:
            del file.data[i]
        del file.data[f"{ctx.user.id}"]
        file.save()
    
    @slash_command(name="role-user-add",description="Add the role to a user")
    async def role_user_add(self,ctx:init, member:Member):
        guild = ctx.guild
        file = Data(guild.id,"Roles","MembersRoles")
        if ctx.user.id == member.id:
            await ctx.send(embed=error_embed("You can't add yourself"),ephemeral=True)
            return
        elif member.bot:
            await ctx.send(embed=error_embed("You can't add a bot"),ephemeral=True)
            return
        try:
            user = dict(file.data.get(f"{ctx.user.id}"))
            user2= file.data.get(f"{member.id}")
            if user == None:
                await ctx.send(embed=error_embed("You Don't have a role"),ephemeral=True)
                return
            if user2 != None:
                await ctx.send(embed=error_embed("He/She already have a role"),ephemeral=True)
                return
            if user["owner"] == False:
                await ctx.send(embed=error_embed("You aren't the owner of the Role"),ephemeral=True)
                return
        except AttributeError: 
            await ctx.send(embed=error_embed("You & Him/Her Don't have a role"),ephemeral=True)
            return
        role = guild.get_role(user["roleID"])
        user["members"].append(f"{member.id}")
        file.data[f"{ctx.user.id}"].update(user)
        data = {f"{member.id}":{
            "owner" :False,
            "roleID":role.id,
        }}
        file.data.update(data)
        file.save()
        await member.add_roles(role)

        await ctx.send(embed=info_embed(f"The {get_name(member)} Added!", title="Member Added!"),ephemeral=True)

    @slash_command(name="role-user-remove",description="Remove the role from a user")
    async def role_user_remove(self,ctx:init, member:Member):
        guild = ctx.guild
        file = Data(guild.id,"Roles","MembersRoles")
        if ctx.user.id == member.id:
            await ctx.send(embed=error_embed("You can't remove yourself"),ephemeral=True)
            return
        elif member.bot:
            await ctx.send(embed=error_embed("You can't remove a bot"),ephemeral=True)
            return
        try:
            user = file.data.get(f"{ctx.user.id}")
            user2= file.data.get(f"{member.id}")
            if user == None:
                await ctx.send(embed=error_embed("You Don't have a role"),ephemeral=True)
                return
            elif user2 == None:
                await ctx.send(embed=error_embed("He/She doesn't have a role"),ephemeral=True)
                return
            elif user["owner"] == False:
                await ctx.send(embed=error_embed("You aren't the owner of the Role"),ephemeral=True)
                return
            elif user["roleID"] != user2["roleID"]:
                await ctx.send(embed=error_embed("He/She doesn't have your role"),ephemeral=True)
        except AttributeError: 
            await ctx.send(embed=error_embed("You & Him/Her Don't have a role"),ephemeral=True)
            return
        role = guild.get_role(user["roleID"])
        user["members"].remove(f"{member.id}")
        file.data[f"{ctx.user.id}"].update(user)
        del file.data[f"{member.id}"]
        file.save()
        await member.remove_roles(role)

        await ctx.send(embed=info_embed(f"The {get_name(member)} Removed!", title="Member Removed!"),ephemeral=True)
    

    @create_role.on_autocomplete("color")
    @role_edit.on_autocomplete("color")
    async def name_autocomplete(self, interaction: nextcord.Interaction, current: str):
        colors = [i for i in self.colors.keys()]
        suggestions = [name for name in colors if name.lower().startswith(current.lower())]
        await interaction.response.send_autocomplete(suggestions)
    
    
    

def setup(client):
    client.add_cog(Rolez(client))