__UserSettingsVersion__ = 1
import nextcord
import nextcord as discord
from nextcord import *
from nextcord.ext import commands
from nextcord.ui import View, Button, TextInput, Modal
from nextcord import Interaction as init
from modules.Nexon import *
import os
import json

#TODO: Add Kick, Ban Commands

async def check(ctx:init,data:Dict | List) -> bool:
    try:ctx.user.voice.channel
    except:
        await ctx.send(embed=warn_embed("You are not in a channel"),ephemeral=True)
        return False
    num = 0
    for i in data:
        i = dict(i)
        values_list = list(i.values())
        if ctx.user.voice.channel.id == values_list[0]:break
        num += 1
    else:
        await ctx.send(embed=warn_embed("You haven't Created a Channel"),ephemeral=True)
        return False

    if ctx.user.voice.channel.id != data[num].get(str(ctx.user.id)):
        await ctx.send(embed=warn_embed("You are not the Owner of this channel!"),ephemeral=True)
        return False
    else:
        return True

def UserSettings(member):
    user = DataGlobal("TempVoice_UsersSettings",f"{member.id}")
    Default = {
        "Name":member.global_name+ "'s Chat" if member.global_name != None
        else member.display_name + "'s Chat",
        "Hide": True,
        "Lock": True,
        "Max": 0,
        "Version":__UserSettingsVersion__
    }
    if user.data ==None: user.data = Default
    elif user.data.get("Version") != __UserSettingsVersion__: user.data = Default  
    return user

class EditMaxModal(Modal):
    def __init__(self, channel:VoiceChannel,ctx:init):
        super().__init__(title="Edit Max Number of users")
        self.user = UserSettings(ctx.user)
        self.channel = channel

        self.max = TextInput(label="Enter the Max number Of User",
                               placeholder="0 for Unlimited",
                               max_length=2, required=True)
        self.add_item(self.max)

    async def callback(self, ctx: nextcord.Interaction):
        # This is called when the modal is submitted
        try:
            num = int(self.max.value)
        except ValueError:
            await ctx.send(embed=error_embed(f"Value \"{self.max.value}\" isn't a number"),ephemeral=True)
            return
        if num > 99:
            await ctx.send(embed=error_embed("The Value should be less than or equal to 99"),ephemeral=True)
            return
        elif num < 0:
            await ctx.send(embed=error_embed("The Value should be greater than or equal to 0"),ephemeral=True)
            return
        self.user["Max"] = num
        self.user.save()
        await self.channel.edit(user_limit=num)

class EditNameModal(Modal):
    def __init__(self, channel:VoiceChannel,ctx:init):
        super().__init__(title="Edit Name")
        self.user = UserSettings(ctx.user)
        self.channel = channel

        self.name = TextInput(label="New Name", placeholder=ctx.user.global_name + "'s Chat" if ctx.user.global_name != None
            else ctx.user.display_name + "'s Chat", required=True, max_length=100, min_length=1)
        self.add_item(self.name)

    async def callback(self, interaction: nextcord.Interaction):
        # This is called when the modal is submitted
        name = self.name.value
        self.user["Name"] = name
        self.user.save()
        await self.channel.edit(name=name)

def get_channel(data,ctx:init):
    num = 0
    for i in data:
        i = dict(i)
        values_list = list(i.values())
        if ctx.user.voice.channel.id == values_list[0]:break
        num += 1
    else:
        raise Exception
    return ctx.guild.get_channel(data[num].get(str(ctx.user.id)))
def get_before(data,ctx:VoiceState,user:Member):
    num = 0
    for i in data:
        i = dict(i)
        values_list = list(i.values())
        try:
            if ctx.channel.id == values_list[0]:break
        except AttributeError:
            return None
        num += 1
    else:
        return None
    return ctx.channel.guild.get_channel(data[num].get(str(user.id)))



class ControlPanel(View):
    def __init__(self, data:Dict,user:User):
        super().__init__(timeout=None)
        self.create_buttons()
        self.data = data
        self.user = UserSettings(user)       

    def create_buttons(self):
        self.button1 = Button(label=f"📝 Edit Name", style=nextcord.ButtonStyle.primary)
        self.button1.callback = self.Edit_Name
        self.add_item(self.button1)

        self.button2 = Button(label=f"🫥 Hide/Show", style=nextcord.ButtonStyle.primary)
        self.button2.callback = self.Hide
        self.add_item(self.button2)

        self.button3 = Button(label=f"🔓 Lock/Unlock", style=nextcord.ButtonStyle.primary)
        self.button3.callback = self.Lock
        self.add_item(self.button3)

        self.button4 = Button(label=f"📝 Change Max Users", style=nextcord.ButtonStyle.primary)
        self.button4.callback = self.Max
        self.add_item(self.button4)

        self.button5 = Button(label=f"🚫 Delete Channel Messages", style=nextcord.ButtonStyle.primary)
        self.button5.callback = self.Delete_Messages
        self.add_item(self.button5)

        

        self.button6 = Button(label=f"⛔ Delete", style=nextcord.ButtonStyle.primary)
        self.button6.callback = self.Delete
        self.add_item(self.button6)

    async def Edit_Name(self, ctx: nextcord.Interaction):
        if await check(ctx,self.data) == False:
            await self.disable(ctx)
            return
        try:
            modal = EditNameModal(get_channel(self.data,ctx),ctx)
        except Exception:
            await ctx.send(embed=warn_embed("You haven't Created a Channel"),ephemeral=True)
            return
        await ctx.response.send_modal(modal)
        

    async def Hide(self, ctx: nextcord.Interaction):
        if await check(ctx,self.data) == False:
            await self.disable(ctx)
            return
        channeled = get_channel(self.data,ctx)
        if self.user.data["Hide"] == True:
            self.user.data["Hide"] = False
            await channeled.set_permissions(everyone(ctx.guild),view_channel=True,
                                            connect=True if self.user.data["Lock"] == False else False)
            await ctx.send(embed=info_embed("The channel is showing", title="Operation Success"),ephemeral=True)
        else:
            self.user.data["Hide"] = True
            await channeled.set_permissions(everyone(ctx.guild),view_channel=False,
                                            connect=True if self.user.data["Lock"] == False else False)
            await ctx.send(embed=info_embed("The channel is hiding", title="Operation Success"),ephemeral=True)
        self.user.save()
        return
    
    async def Lock(self, ctx: nextcord.Interaction):
        if await check(ctx,self.data) == False:
            await self.disable(ctx)
            return
        channeled = get_channel(self.data,ctx)
        if self.user.data["Lock"] == True:
            self.user.data["Lock"] = False
            await channeled.set_permissions(everyone(ctx.guild),connect=True,
                view_channel=True if self.user.data["Hide"] == False else False)
            await ctx.send(embed=info_embed("The channel is Unlocked", title="Operation Success"),ephemeral=True)
        else:
            self.user.data["Lock"] = True
            await channeled.set_permissions(everyone(ctx.guild),connect=False,
                view_channel=True if self.user.data["Hide"] == False else False)
            await ctx.send(embed=info_embed("The channel is Locked", title="Operation Success"),ephemeral=True)
        self.user.save()
        return
    
    async def Max(self, ctx: nextcord.Interaction):
        if await check(ctx,self.data) == False:
            await self.disable(ctx)
            return
        try:
            modal = EditMaxModal(get_channel(self.data,ctx),ctx)
        except Exception:
            await ctx.send(embed=warn_embed("You haven't Created a Channel"),ephemeral=True)
            return
        await ctx.response.send_modal(modal)

    async def Delete_Messages(self, ctx: nextcord.Interaction):
        if await check(ctx,self.data) == False:
            await self.disable(ctx)
            return
        try:
            channeled = get_channel(self.data,ctx)
        except Exception:
            await ctx.send(embed=warn_embed("You haven't Created a Channel"),ephemeral=True)
            return
        await channeled.purge(limit=10000)

    async def Delete(self, ctx: nextcord.Interaction):
        if await check(ctx,self.data) == False:
            await self.disable(ctx)
            return
        try:
            channeled = get_channel(self.data,ctx)
        except Exception:
            await ctx.send(embed=warn_embed("You haven't Created a Channel"),ephemeral=True)
            return
        file = Data(ctx.guild.id,"TempVoice","TempVoices")
        num = 0
        for i in file.data:
            i = dict(i)
            values_list = list(i.values())
            if channeled.id == values_list[0]:break
            num += 1
        else:return
        await channeled.delete()
        file.data.remove(file.data[num])
        file.save()
        await self.disable(ctx)

    async def disable(self, ctx: nextcord.Interaction):
        buttons = [
            self.button1,self.button2,self.button3,
            self.button4,self.button5,self.button6]
        for button in buttons:
            button.disabled = True
        self.stop()
        await ctx.response.edit_message(view=self)

async def invite_function(ctx:init,user:Member,client):
    await ctx.response.defer(ephemeral=True)
    if ctx.user.id == user.id:
        await ctx.send(embed=error_embed("You can't Invite yourself"))
        return
    elif user.id == client.user.id:
        await ctx.send(embed=error_embed("Are You trying to Invite me?",footer="No, You can't"))
        return
    elif user.bot:
        await ctx.send(embed=error_embed("You can't Invite Bot"))
        return
    file = Data(ctx.guild.id,"TempVoice","TempVoices")  
    await check(ctx,file.data)
    channel = get_channel(file.data,ctx)
    name = ctx.user.global_name if ctx.user.global_name != None else ctx.user.display_name
    await channel.set_permissions(user, view_channel=True, connect=True)
    try:
        await user.send(embed=info_embed(
            f"You have Been Invited by {ctx.user.mention} to Channel {channel.mention}.\n[View The Channel]({channel.jump_url})",
            "Invitation",
            f"Click the Channel to Join it",[name,ctx.user.avatar.url]
            ))
    except HTTPException:
        ctx.channel.send(f"{user.mention}",embed=info_embed(
            f"{user.mention}, You have Been Invited by {ctx.user.mention} to Channel {channel.mention}.\n[View The Channel]({channel.jump_url})",
            "Invitation",
            f"Click the Channel to Join it",[name,ctx.user.avatar.url]
            ))
    await ctx.send("Sended!",ephemeral=True)
    return


class TempVoice(commands.Cog):
    def __init__(self, client:Client):
        self.client = client
    @slash_command(name="voice")
    async def voice(self,ctx:init):
        pass
    @voice.subcommand(name="panel",
        description="Bring the Control Panel for the TempVoice chat")
    @feature()
    async def controlpanel(self,ctx:init):
        file = Data(ctx.guild.id,"TempVoice","TempVoices")  
        checks = check(ctx,file.data)
        if await checks == False: return
        
        await ctx.response.send_message(embed=info_embed(title="Control Panel",
                description="Please Chose"),view=ControlPanel(file.data,ctx.user),
                ephemeral=True)


     
    @voice.subcommand("invite",description="Invite a member to Voice chat")
    @feature()
    async def invite_slash(self,ctx:init,user:Member):
        return await invite_function(ctx,user,self.client)
    
    @user_command("Invite Voice",dm_permission=False)
    @feature()
    async def invite(self,ctx:init, user:Member):
        return await invite_function(ctx,user,self.client)
        



    @commands.command(name = "setup-voice",
                    aliases=["create voice"],
                    description = "Setup temp voice")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 10, commands.BucketType.member)
    async def setup(self, ctx:commands.Context, Category:CategoryChannel):
        featureInside(ctx.guild.id,self)
        file = Data(ctx.guild.id,"TempVoice")
        createChannel = await ctx.guild.create_voice_channel("➕・Create",
            reason=f"Used setup Temp Voice by {ctx.author}", category=Category)
        data = {
            "CreateChannel"     : createChannel.id,
            "categoryChannel"   : Category.id
        }
        file.data = data
        file.save()
        await ctx.send(embed=info_embed("Setup Done!"),ephemeral=True)
    

    #Listener If a Person Created a Channel
    @commands.Cog.listener()
    async def on_voice_state_update(self, member:discord.Member,
                 before:discord.VoiceState, after:discord.VoiceState):
        try: featureInside(after.channel.guild.id,self)
        except AttributeError:
            try: featureInside(before.channel.guild.id,self)
            except AttributeError: return
        try:guild = after.channel.guild
        except AttributeError:return
        file = Data(guild.id,"TempVoice")
        file2 = Data(guild.id,"TempVoice","TempVoices")
        if file.check() == False:
            return
        if get_before(file2.data,before,member) != None:
            await member.disconnect(reason="Trying to Bug the Bot")
            return
        user = DataGlobal("TempVoice_UsersSettings",f"{member.id}")
        if user.data != None:
            if user.data.get("Version") == __UserSettingsVersion__:
                temp = user.data
                name = temp["Name"]
                connect = True if temp["Lock"] == False else False
                view = True if temp["Hide"] == False else False
                Max = temp["Max"]
                del temp
        else:
            name = member.global_name+ "'s Chat" if member.global_name != None \
                else member.display_name+ "'s Chat"
            connect = False
            view = False
            Max = 0
        if file.data == None:
            file.data = []
        createChannel = guild.get_channel(file["CreateChannel"])
        if createChannel.id != after.channel.id:return

        overwrite = {
            everyone(guild) : PermissionOverwriteWith(connect=connect, view_channel=view),
            member          : PermissionOverwriteWith(connect=True, view_channel=True,
                                            priority_speaker=True, move_members=True)
        }

        newTempChat = await guild.create_voice_channel(name, category= guild.get_channel(file["categoryChannel"]),
                reason=f"User {member} Created a TempVoice",overwrites=overwrite,user_limit=Max)
        await member.move_to(newTempChat,reason=f"User {member} Created a TempVoice")
        file2.data.append({member.id:newTempChat.id})
        file2.save()
        await newTempChat.send(embed=warn_embed("Only the Owner can change the settings of this channel, "+
                                          "Even If he Left",title="Note",author=[member.name,member.avatar.url]))
    
    
    
class TempVoice2(commands.Cog):
    def __init__(self, client:Client):
        self.client = client
    #Listener For if the user left the server and there is no one left in the server
    @commands.Cog.listener()
    async def on_voice_state_update(self, member:discord.Member,
                     before:discord.VoiceState, after:discord.VoiceState):
        try: featureInside(after.channel.guild.id,self)
        except AttributeError:
            try: featureInside(before.channel.guild.id,self)
            except AttributeError: return

        try: before.channel.id
        except AttributeError: return
        guild = before.channel.guild
        file = Data(guild.id,"TempVoice","TempVoices")
        if file.data == None:
            file.data = []
            file.save()
        num = 0
        for i in file.data:
            i = dict(i)
            values_list = list(i.values())
            if before.channel.id == values_list[0]:break
            num += 1
        else:return
        if len(before.channel.members) == 0:
            await before.channel.delete()
            file.data.remove(file.data[num])
            file.save()
            return


def setup(client):
    client.add_cog(TempVoice (client))
    client.add_cog(TempVoice2(client))