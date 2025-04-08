from modules.Nexon import *
from modules.config import Color
from typing import Optional, Union
from nexon import Client, Member, User, ButtonStyle, Interaction, Role, Guild
from nexon.ui import Button, View
from nexon.ext import commands

class Request(View):
    def __init__(self, guild_id: int, client: commands.Bot, fromUser: Member):
        super().__init__(timeout=None)
        self.accept_button = Button(label="✅ Accept", style=ButtonStyle.green)
        self.accept_button.callback = self.accept_callback
        self.add_item(self.accept_button)
        self.guild_id = guild_id
        self.client = client
        self.fromUser = fromUser

    async def accept_callback(self, interaction: Interaction):
        if not (guild := self.client.get_guild(self.guild_id)):
            return
            
        feature = await Feature.get_guild_feature(self.guild_id, "Roles")
        data: dict = feature.get_global("MembersRoles", {})
        if not (user_data := data.get(str(self.fromUser.id))):
            return
            
        user = dict(user_data)
        if not (role := guild.get_role(user["roleID"])):
            return
            
        if not interaction.user:
            return
            
        user["members"].append(f"{interaction.user.id}")
        data[f"{self.fromUser.id}"].update(user)
        data.update({
            f"{interaction.user.id}": {
                "owner": False,
                "roleID": role.id,
            }
        })
        await feature.save()
        
        if not (member := guild.get_member(interaction.user.id)):
            return
            
        await member.add_roles(role)
        
        await interaction.response.send_message(
            embed=Embed.Info(
                title=f"You Joined a {self.fromUser.display_name}'s Role",
                description=f"In {guild.name} and Role {role.name}"
            ),
            ephemeral=True
        )

class Roles(commands.Cog):
    def __init__(self, client: commands.Bot):
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
    
    
    @role.subcommand(name="create",description="Create a role for yourself")
    async def create_role(self, ctx: Interaction, name: str, color: str = SlashOption(
        "color", "Type Hex code or one of these colors", required=True, autocomplete=True
    )):
        if not ctx.guild or not ctx.user or isinstance(ctx.user, User):
            return await ctx.send(embed=Embed.Error("Your are not in a server"))
            
        # Check role creation mode
        feature = await Feature.get_guild_feature(ctx.guild.id, "Roles")
        data: dict = feature.get_setting()
        mode = data.get("creation_mode", "everyone")

        # Check if user is booster when required
        if mode == "boosters" and not getattr(ctx.user, "premium_since", None):
            await ctx.response.send_message(
                embed=Embed.Error(
                    "Only server boosters can create roles. Boost the server to unlock this feature!",
                    title="Booster Only Command"
                ),
                ephemeral=True
            )
            return

        try:
            color_obj = self.colors.get(color.capitalize(), Color(color if color.startswith("#") else f"#{color}"))
        except (KeyError, ValueError):
            await ctx.response.send_message(
                embed=Embed.Error("Invalid color format"),
                ephemeral=True
            )
            return

        guild = ctx.guild
        feature = await Feature.get_guild_feature(ctx.guild.id, "Roles")
        data: dict = feature.get_setting()
        if data.get(str(ctx.user.id)):
            await ctx.send(embed=Embed.Error("You already have a role"),ephemeral=True)
            return
        if name.lower() in self.notAllowed: #TODO: use a library instead to censor words
            await ctx.send(embed=Embed.Error("This word/name isn't allowed"),ephemeral=True)
            return
        role = await guild.create_role(reason=f"{ctx.user.name}/{ctx.user.id} Created a role",
                                name=name, color=color_obj.value,hoist=True)
        await ctx.user.add_roles(role)
        await ctx.send(embed=Embed.Info(f"You have created a role by the name: {name}", title="Role Created!"),ephemeral=True)
        data= {f"{ctx.user.id}":{
            "owner"     :True,
            "roleID"    :role.id,
            "members"   :[]
        }}
        data.update(data)
        await feature.save()
    
    @role.subcommand(name="edit",description="Edit your own role like the name or role or both!")
    @cooldown(15)
    async def role_edit(self,ctx: Interaction, name: Optional[str] = None, color:str=SlashOption("color","Type Hex code or one of these colors",
                                        required=False, autocomplete=True,default=None)):
        guild = ctx.guild
        if not guild or not ctx.user or not isinstance(ctx.user, Member):
            await ctx.send(embed=Embed.Error("This command can only be used in a server"),ephemeral=True)
            return
        if color != None:
            color = self.colors.get(color.capitalize(), Color("#FFFFFF")).hex
            colorInt = self.colors.get(color.capitalize(), Color("#FFFFFF")).value
        feature = await Feature.get_guild_feature(guild.id, "Roles")
        data: dict = feature.get_global("MembersRoles", {})
        try:
            user = data.get(str(ctx.user.id))
            if user == None:
                await ctx.send(embed=Embed.Error("You Don't have a role"),ephemeral=True)
                return
            if user["owner"] == False:
                await ctx.send(embed=Embed.Error("You aren't the owner of the Role"),ephemeral=True)
                return
        except AttributeError: 
            await ctx.send(embed=Embed.Error("You Don't have a role"),ephemeral=True)
            return
        if name:
            if name.lower() in self.notAllowed:
                await ctx.send(embed=Embed.Error("This word/name isn't allowed"),ephemeral=True)
                return
        role = guild.get_role(user["roleID"])
        if not role:
           role= await guild.fetch_role(user["roleID"])
        if (name == None) and (color == None):
            await ctx.send(embed=Embed.Error("you haven't change anything ||trying to be funny?||"),ephemeral=True)
            return
        if name != None:await role.edit(name=name)
        if color!= None:await role.edit(color=colorInt)
        await ctx.send(embed=Embed.Info(f"You have Edit a role by the name", title="Role Edited!"),ephemeral=True)


    @role.subcommand(name="delete",description="delete your own role")
    async def role_delete(self,ctx:init):
        guild = ctx.guild
        if not guild or not ctx.user:
            await ctx.send(embed=Embed.Error("This command can only be used in a server"),ephemeral=True)
            return
        feature = await Feature.get_guild_feature(guild.id, "Roles")
        data: dict = feature.get_setting("MembersRole", {})
        try:
            user = data.get(str(ctx.user.id))
            if user == None:
                await ctx.send(embed=Embed.Error("You Don't have a role"),ephemeral=True)
                return
            if user["owner"] == False:
                await ctx.send(embed=Embed.Error("You aren't the owner of the Role"),ephemeral=True)
                return
        except AttributeError: 
            await ctx.send(embed=Embed.Error("You Don't have a role"),ephemeral=True)
            return
        role = guild.get_role(user["roleID"])
        if not role:
            role = await guild.fetch_role(user["roleID"])
        await role.delete(reason=f"{ctx.user.name}/{ctx.user.id} deleted a role")
        await ctx.send(embed=Embed.Info(f"You have deleted the role", title="Role Deleted!"),ephemeral=True)
        for i in user["members"]:
            del data[i]
        del data[f"{ctx.user.id}"]
        await feature.save()
    
    @user_command("Role: Add User", contexts=[InteractionContextType.guild])
    async def role_user_add_user_command(self,ctx:init, member:Member):
        await self.role_user_add(ctx,member)
    @user_command("Role: Remove User", contexts=[InteractionContextType.guild])
    async def role_user_remove_user_command(self,ctx:init, member:Member):
        await self.role_user_remove(ctx,member)


    @role.subcommand(name="add",description="Add the role to a user")
    @cooldown(15)
    async def role_user_add(self,ctx:init, member:Member):
        guild = ctx.guild
        if not guild or not ctx.user or isinstance(ctx.user, User) or not ctx.channel or isinstance(ctx.channel, (CategoryChannel, ForumChannel)):
            await ctx.send(embed=Embed.Error("This command can only be used in a server"),ephemeral=True)
            return
        
        feature = await Feature.get_guild_feature(guild.id, "Roles")
        data: dict = feature.get_setting("MembersRole", {})
        if ctx.user.id == member.id:
            await ctx.send(embed=Embed.Error("You can't add yourself"),ephemeral=True)
            return
        elif member.bot:
            await ctx.send(embed=Embed.Error("You can't add a bot"),ephemeral=True)
            return
        try:
            user: Optional[dict] = data.get(str(ctx.user.id))
            user2: Optional[dict] = data.get(f"{member.id}")
            if not user:
                await ctx.send(embed=Embed.Error("You Don't have a role"),ephemeral=True)
                return
            if user2:
                await ctx.send(embed=Embed.Error("He/She already have a role"),ephemeral=True)
                return
            if user["owner"] == False:
                await ctx.send(embed=Embed.Error("You aren't the owner of the Role"),ephemeral=True)
                return
        except AttributeError: 
            await ctx.send(embed=Embed.Error("You & Him/Her Don't have a role"),ephemeral=True)
            return
        view = Request(guild.id,self.client,ctx.user)
        #Send DM or Channel
        role = guild.get_role(user["roleID"])
        if not role:
            role = await guild.fetch_role(user["roleID"])
        try:
            await member.send(member.mention,embed=Embed.Info(title=f"You got Invited by {ctx.user.display_name}",description=f"In {guild.name} and Role {role.name}"),
                              view=view)
        except:
            await ctx.channel.send(member.mention,embed=Embed.Info(title=f"You got Invited by {ctx.user.display_name}",description=f"In {guild.name} and Role {role.name}"),
                                view=view)
        await ctx.send(embed=Embed.Info(title="Invited!",description=f"You have Invited {member.mention}"))

    @role.subcommand(name="remove",description="Remove the role from a user")
    @cooldown(15)
    async def role_user_remove(self,ctx:init, member:Member):
        guild = ctx.guild
        if not guild or not ctx.user:
            await ctx.send(embed=Embed.Error("This command can only be used in a server"),ephemeral=True)
            return
        feature = await Feature.get_guild_feature(guild.id, "Roles")
        data: dict = feature.get_setting("MembersRole", {})
        if ctx.user.id == member.id:
            await ctx.send(embed=Embed.Error("You can't remove yourself"),ephemeral=True)
            return
        elif member.bot:
            await ctx.send(embed=Embed.Error("You can't remove a bot"),ephemeral=True)
            return
        try:
            user = data.get(f"{ctx.user.id}")
            user2= data.get(f"{member.id}")
            if not user:
                await ctx.send(embed=Embed.Error("You Don't have a role"),ephemeral=True)
                return
            elif not user2:
                await ctx.send(embed=Embed.Error("He/She doesn't have a role"),ephemeral=True)
                return
            elif user["owner"] == False:
                await ctx.send(embed=Embed.Error("You aren't the owner of the Role"),ephemeral=True)
                return
            elif user["roleID"] != user2["roleID"]:
                await ctx.send(embed=Embed.Error("He/She doesn't have your role"),ephemeral=True)
        except AttributeError: 
            await ctx.send(embed=Embed.Error("You & Him/Her Don't have a role"),ephemeral=True)
            return
        role = guild.get_role(user["roleID"])
        if not role:
            role = await guild.fetch_role(user["roleID"])
        user["members"].remove(f"{member.id}")
        data[f"{ctx.user.id}"].update(user)
        del data[f"{member.id}"]
        await feature.save()
        await member.remove_roles(role)

        await ctx.send(embed=Embed.Info(f"The {member.display_name} Removed!", title="Member Removed!"),ephemeral=True)
    

    @create_role.on_autocomplete("color")
    @role_edit.on_autocomplete("color")
    async def name_autocomplete(self, interaction: Interaction, current: str):
        colors = [i for i in self.colors.keys()]
        suggestions = [name for name in colors if name.lower().startswith(current.lower())]
        if (suggestions == []) and (current.startswith("#")):
             suggestions = [current]
        await interaction.response.send_autocomplete(suggestions)
    
    
    

def setup(client: commands.Bot):
    client.add_cog(Roles(client))