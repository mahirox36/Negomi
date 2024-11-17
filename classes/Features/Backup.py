"""
Backup.py is for Backing up your server as a File"""
import io
from nextcord import *
from nextcord.ext import commands
from nextcord.ext.commands import Context, command
from nextcord import Interaction as init
from modules.Nexon import *
import json
import os
__version__ = 1.3

class Backup(commands.Cog):
    def __init__(self, client:Client):
        self.client = client
    @slash_command(name="export", description="this will export Roles, Channels, and Bots Names", default_member_permissions=Permissions(administrator=True))
    @feature()
    async def export(self,ctx:init):
        await ctx.send(embed=info_embed(f"This will take some time.","Wait! OwO"))
        data = {
            "version": __version__,
            "channels":{
                "Category":{},
                "Voice"   :[],
                "Channels":[]
            },
            "roles"   :[],
            "bot_name":[]
        }
        for i in ctx.guild.channels:
            if str(i.type) == "category":
                data["channels"]["Category"].update({i.id:i.name})
            elif str(i.type) == "voice":
                data["channels"]["Voice"].append([i.name,i.category_id])
            else:
                try:
                    data["channels"]["Channels"].append([i.name,i.category_id,i.topic])
                except ApplicationInvokeError:
                    data["channels"]["Channels"].append([i.name,i.category_id,None])
        for i in reversed(ctx.guild.roles):
            data["roles"].append([i.name,i.color.value,i.permissions.value])
        for i in ctx.guild.bots:
            data["bot_name"].append(i.display_name)
        os.makedirs(f"temp/{ctx.guild.id}",exist_ok=True)
        file_data = io.StringIO()
        try:
            json.dump(data, file_data, indent=2, ensure_ascii=False)
            file_data.seek(0)
            discord_file = File(file_data, filename="backup.json")
            await ctx.channel.send(file=discord_file)
        finally:
            file_data.close()

    @slash_command(name="import",
                   description="This will import Roles, Channels, and Bots Names. You need to upload the file you made with export",
                   default_member_permissions=Permissions(administrator=True))
    @feature()
    async def imported(self,ctx:init, file: Attachment):
        temp = await file.read()
        data = dict(json.loads(temp))
        if data.get("version") == __version__:
            await ctx.send(embed=info_embed("It will take some Time to Import Everything","Okie UwU"))
        else:
            await ctx.send(embed=warn_embed("and we will import it for you, BUT If it didn't work do a new backup!",title="⚠️The Backup Version is Outdated⚠️"))
        temp = {}
        for i in data["channels"]["Category"]:
            category = await ctx.guild.create_category(data["channels"]["Category"][i])
            temp.update({i:category})
        for i in data["channels"]["Voice"]:
            gg = None
            if i[1] != None:
                for j in temp:
                    if str(j) == str(i[1]):
                        gg = j
            await ctx.guild.create_voice_channel(i[0],category=temp.get(gg))
        for i in data["channels"]["Channels"]:
            gg = None
            if i[1] != None:
                for j in temp:
                    if j == str(i[1]):
                        gg = j
            await ctx.guild.create_text_channel(i[0],category=temp.get(gg),topic=i[2])
        for i in data["roles"]:
            if i[0] == "@everyone":
                await ctx.guild.default_role.edit(permissions=Permissions(i[2]))
                continue
            await ctx.guild.create_role(name=i[0],color=Color(i[1]),permissions=Permissions(i[2]))
        finalChannel = await ctx.guild.create_text_channel("more-info")
        botsNames = "Bots Names:\n"
        for i in data["bot_name"]:
            botsNames += i +"\n"
        await finalChannel.send(botsNames)
        await finalChannel.send("Finished Everything")

def setup(client):
    client.add_cog(Backup(client))