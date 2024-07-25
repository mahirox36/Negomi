import nextcord
import nextcord as discord
from nextcord import *
from nextcord.ext import commands
from nextcord import Interaction as init
from Lib.Data import Data
from Lib.Side import *

from Lib.Hybrid import setup_hybrid, userCTX
import os
import json

class TempVoice(commands.Cog):
    def __init__(self, client:Client):
        self.client = client
        self.Hybrid = setup_hybrid(client)



    @commands.command(name = "setup-voice",
                    aliases=["create voice"],
                    description = "Setup temp voice")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 10, commands.BucketType.member)
    async def setup(self, ctx:commands.Context, Category:CategoryChannel):
        file = Data(ctx.guild.id,"TempVoice")
        createChannel = await ctx.guild.create_voice_channel("➕・Create",
            reason=f"Used setup Temp Voice by {ctx.author}", category=Category)
        data = {
            "CreateChannel"     : createChannel.id,
            "categoryChannel"   : Category.id
        }
        file.data = data
        file.save()
        await ctx.send(embed=info_embed("Setup Done!"))
    

    #Listener If a Person Created a Channel
    @commands.Cog.listener()
    async def on_voice_state_update(self, member:discord.Member,
                 before:discord.VoiceState, after:discord.VoiceState):
        try:guild = after.channel.guild
        except AttributeError:return
        file = Data(guild.id,"TempVoice")
        file2 = Data(guild.id,"TempVoice","TempVoices")
        if file.data == None:
            file.data = []
        createChannel = guild.get_channel(file["CreateChannel"])
        if createChannel.id != after.channel.id:return
        newTempChat = await guild.create_voice_channel(member.global_name if member.global_name != None
            else member.display_name+ "'s Chat", category= guild.get_channel(file["categoryChannel"]),
                reason=f"User {member} Created a TempVoice")
        await member.move_to(newTempChat,reason=f"User {member} Created a TempVoice")
        file2.data.append(newTempChat.id)
        file2.save()
    
class TempVoice2(commands.Cog):
    def __init__(self, client:Client):
        self.client = client
        self.Hybrid = setup_hybrid(client)
    #Listener For if the user left the server and there is no one left in the server
    @commands.Cog.listener()
    async def on_voice_state_update(self, member:discord.Member,
                     before:discord.VoiceState, after:discord.VoiceState):
        try: before.channel.id
        except AttributeError: return
        guild = before.channel.guild
        file = Data(guild.id,"TempVoice","TempVoices")
        if file.data == None:
            file.data = []
            file.save()
        print(len(before.channel.members))
        if before.channel.id not in file.data:return
        elif len(before.channel.members) == 0:
            await before.channel.delete()
            file.data.remove(before.channel.id)
            file.save()


def setup(client):
    client.add_cog(TempVoice (client))
    client.add_cog(TempVoice2(client))