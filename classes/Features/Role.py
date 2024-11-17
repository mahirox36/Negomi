import nextcord
import nextcord as discord
from nextcord import *
from nextcord.ext import commands
from nextcord import Interaction as init, SlashOption
from modules.Nexon import *
from modules.config import Color
import os
import json

class Request(ui.View):
    def __init__(self,guild_id,client: commands.Bot, fromUser: Member):
        super().__init__(timeout=None)
        self.Accept = ui.Button(label=f"✅ Accept", style=nextcord.ButtonStyle.green)
        self.Accept.callback = self.Accept
        self.add_item(self.Accept)
        self.guild_id= guild_id
        self.client = client
        self.fromUser =fromUser

    async def Accept(self, ctx: nextcord.Interaction):
        guild= self.client.get_guild(self.guild_id)
        file = Data(self.guild_id,"Roles","MembersRoles")
        role = guild.get_role(user["roleID"])
        user = dict(file.data.get(f"{self.fromUser.id}"))
        user["members"].append(f"{ctx.user.id}")
        file.data[f"{self.fromUser.id}"].update(user)
        data = {f"{member.id}":{
            "owner" :False,
            "roleID":role.id,
        }}
        file.data.update(data)
        file.save()
        member= guild.get_member(ctx.user.id)
        await member.add_roles(role)
        await ctx.send(embed=info_embed(title=f"You Joined a {get_name(self.fromUser)}'s Role",description=f"In {guild.name} and Role {role.name}"
                                        ,author=[guild.name,guild.icon.url]),ephemeral= True)


class Rolez(commands.Cog):
    def __init__(self, client:Client):
        self.client = client
        #Not allowed Words for roles
        self.notAllowed = ["nigga","niggers","nigger","gay","femboy","femboys",
                           "trans","transgender","kiss","sex","strip"]
        self.colors = {
    "Red": Color("#FF0000"),"Green": Color("#008000"),"Blue": Color("#0000FF"),"Yellow": Color("#FFFF00"),"Cyan": Color("#00FFFF"),
    "Magenta": Color("#FF00FF"),"Orange": Color("#FFA500"),"Purple": Color("#800080"),"Pink": Color("#FFC0CB"),"Brown": Color("#A52A2A"),
    "Gray": Color("#808080"),"Black": Color("#000001"),"White": Color("#FFFFFF"),"Lime": Color("#00FF00"),"Olive": Color("#808000"),
    "Navy": Color("#000080"),"Teal": Color("#008080"),"Maroon": Color("#800000"),"Silver": Color("#C0C0C0"),"Gold": Color("#FFD700"),
    "Coral": Color("#FF7F50"),"Salmon": Color("#FA8072"),"Turquoise": Color("#40E0D0"),"Indigo": Color("#4B0082"),"Violet": Color("#EE82EE")}
    
    @slash_command(name="role")
    async def role(self,ctx:init):
        pass
    
    @role.subcommand(name="setup",description="Create a role for your self")
    @feature()
    async def setup(self,ctx:init):
        ctx.guild.integrations()
    @role.subcommand(name="create",description="Create a role for your self")
    @feature()
    async def create_role(self,ctx:init,name:str,color:str=SlashOption("color","Type Hex code or one of these colors",
                                        required=True, autocomplete=True)):
        guild = ctx.guild
        try:color = self.colors[color.capitalize()]
        except KeyError:color= Color("#"+color if not color.startswith("#") else color)
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
    
    @role.subcommand(name="edit",description="Edit your own role like the name or role or both!")
    @cooldown(15)
    @feature()
    async def role_edit(self,ctx:init,name:str=None,color:str=SlashOption("color","Type Hex code or one of these colors",
                                        required=False, autocomplete=True,default=None)):
        guild = ctx.guild
        if color != None:
            color = self.colors[color.capitalize()]
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


    @role.subcommand(name="delete",description="delete your own role")
    @feature()
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
    
    @user_command("Role: Add User")
    @feature()
    async def role_user_add_user_command(self,ctx:init, member:Member):
        await self.role_user_add(ctx,member)
    @user_command("Role: Remove User")
    @feature()
    async def role_user_remove_user_command(self,ctx:init, member:Member):
        await self.role_user_remove(ctx,member)


    @role.subcommand(name="add",description="Add the role to a user")
    @cooldown(3)
    @feature()
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
        view = Request(guild.id,self.client,ctx.user)
        #Send DM or Channel
        role = guild.get_role(user["roleID"])
        try:
            await member.send(member.mention,embed=info_embed(title=f"You got Invited by {get_name(ctx.user)}",description=f"In {guild.name} and Role {role.name}",author=[guild.name,guild.icon.url]),
                              view=view)
        except:
            await ctx.channel.send(member.mention,embed=info_embed(title=f"You got Invited by {get_name(ctx.user)}",description=f"In {guild.name} and Role {role.name}",author=[guild.name,guild.icon.url]),
                                view=view)
        await ctx.send(embed=info_embed(title="Invited!",description=f"You have Invited {member.mention}"))

    @role.subcommand(name="remove",description="Remove the role from a user")
    @cooldown(3)
    @feature()
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
        if (suggestions == []) and (current.startswith("#")):
             suggestions = [current]
        await interaction.response.send_autocomplete(suggestions)
    
    
    

def setup(client):
    client.add_cog(Rolez(client))