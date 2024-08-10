from typing import List
import nextcord
import nextcord as discord
from nextcord import *
from nextcord.ext import commands
from nextcord import Interaction as init
from nextcord.utils import MISSING
from Lib.Side import *
from Lib.Logger import *
from Lib.Hybrid import setup_hybrid, userCTX
from typing import Dict, Optional
import os
import json

class descriptionNone:
    def __init__(self) -> None:
        value = None
    def __str__(self):
        return "No description Provided"

home_embed= info_embed("Hello, I am Negomi Made By my master/papa Mahiro\n\
                            What Can I do you ask? Well a lot of stuff.\n\n\
                            To get started Check Select List Below!", title="🏠 Home")

def dynamic_cog_getter(cogName: str, client: commands.Bot) -> Optional[Dict]:
    cog = client.get_cog(cogName)
    data= {}
    for command in cog.application_commands:
        name = command.name
        description= command.description if command.description != None else descriptionNone()
        data.update({name:description})
    if data== {}:
        return None
    return data

def embed_builder(CogName: str, title: str, client: commands.Bot, extraInfo:str = None):
    data = dynamic_cog_getter(CogName, client)
    if not data: return
    owner = client.get_user(owner_id)
    embed = info_embed(extraInfo,title)
    for name, description in data.items():
        embed.add_field(name=f"`{name}`",value="This Is User Command" if description == "" else description)
    return embed
    

#TODO: add Button for Admin if the user was admin
class HelpSelect(ui.View):
    def __init__(self,admin: bool=False) -> None:
        super().__init__(timeout=None)
        self.options = [
            SelectOption(label="Home", value="home",emoji="🏠",default=True),
            SelectOption(label="Role", value="role",emoji="👥"),
            SelectOption(label="Temp Voice", value="temp",emoji="🎤"),
            SelectOption(label="AI", value="ai",emoji="😈"),
            SelectOption(label="Other", value="other",emoji="⚙️")
        ]
        self.select = ui.Select(placeholder="Choose an option...",options=self.options)
        self.select.callback = self.callback
        self.add_item(self.select)
        if admin:
            self.adminButton = ui.Button(style=ButtonStyle.green,label="🧑‍💻 Admin")
            self.adminButton.callback = self.adminButtonCallback
            self.add_item(self.adminButton)
    async def callback(self, ctx: Interaction):
        selected_value = self.select.values[0]
        num = 0
        for option in self.options:
            if option.value == self.select.values[0]:
                RealNum = num
            else:
                self.options[num].default = None
            num+=1
        self.options[RealNum].default = True
        self.select.options = self.options
        global home_embed
        owner = ctx.client.get_user(owner_id)
        if selected_value == "home" : embed = home_embed.set_author(name=get_name(owner),icon_url=owner.avatar.url)
        if selected_value == "role" : embed= embed_builder("Rolez","👥 Role" ,          ctx.client,
        extraInfo="")
        if selected_value == "temp" : embed= embed_builder("TempVoice","🎤 Temp Voice", ctx.client,
        extraInfo="You can create a channel by Join the Create Channel ")
        if selected_value == "ai"   : embed= embed_builder("AI", "😈 AI"     ,          ctx.client,
        extraInfo="You can Talk to her by mention her or reply to her message")
        if selected_value == "other": embed= embed_builder("funny", "⚙️ Other",         ctx.client,
        extraInfo="")
        await ctx.response.edit_message(embed=embed,view=self)
    async def adminButtonCallback(self, ctx: init):
        self.remove_item(self.select)
        self.adminButton.label = "Back ⤴️"
        self.adminButton.style = ButtonStyle.blurple
        self.adminButton.callback = self.adminButtonReverseCallback
        owner = ctx.client.get_user(owner_id)
        embed = info_embed(f"Hey Admin! What's up?\n Anyway there isn't a lot showing here.\n\nSo please use the `{prefix}help` for admin commands!",
                           title="🧑‍💻 Admin")
            # .set_author(name=get_name(owner),icon_url=owner.avatar.url)
        await ctx.response.edit_message(embed=embed,view=self)
    async def adminButtonReverseCallback(self, ctx: Interaction):
        self.add_item(self.select)
        self.adminButton.label = "🧑‍💻 Admin"
        self.adminButton.style = ButtonStyle.green
        self.adminButton.callback = self.adminButtonCallback
        owner = ctx.client.get_user(owner_id)
        home_embed.set_author(name=get_name(owner),icon_url=owner.avatar.url)
        await ctx.response.edit_message(embed=home_embed,view=self)
        
        
       
    
    async def disable(self, ctx: nextcord.Interaction):
        buttons = [
            self.button1,self.button2,self.button3,
            self.button4,self.button5,self.button6]
        for button in buttons:
            button.disabled = True
        self.stop()
        await ctx.response.edit_message(view=self)



class Help(commands.Cog):
    def __init__(self, client:Client):
        self.client = client
    @slash_command(name="help",description="Help command")
    async def help(self,ctx:init):
        global home_embed
        admin= ctx.user.guild_permissions.administrator
        view = HelpSelect(admin)
        owner = self.client.get_user(owner_id)
        await ctx.send(embed=home_embed.set_author(name=get_name(owner),icon_url=owner.avatar.url),view=view,ephemeral=True)

    

def setup(client):
    client.add_cog(Help(client))