from asyncio import sleep
import nextcord
import nextcord as discord
from nextcord import *
from nextcord.ext import commands
from nextcord import Interaction as init, SlashOption
from Lib.Side import *
import ollama
import os
import json
from Lib.Negomi import get_response, generate

models = [model["name"].split(":")[0] for model in ollama.list()["models"]]


class AI(commands.Cog):
    def __init__(self, client:Client):
        self.client = client
        self.running = False
        self.started = False
    
    @slash_command(name="ask",description="ask an Advance AI")
    @cooldown(15)
    @feature()
    async def Say(self,ctx:init,message:str,
                  model= SlashOption(
                      "model",
                      "Select a model you wish to ask to",
                      False,
                      choices=models
                  )):
        try:
            if ctx.guild.id != AI_AllowedServers:
                await ctx.send(embed=error_embed("Sorry But this Only Works on The Owner's Server\n"+
        "If you want this feature please run your [own bot here](https://github.com/mahirox36/Negomi) and your own AI Using Ollama"), ephemeral=True)
        except:
            await ctx.send(embed=error_embed("Sorry But this Only Works on The Owner's Server\n"+
        "If you want this feature please run your [own bot here](https://github.com/mahirox36/Negomi) and your own AI Using Ollama"), ephemeral=True)
        if self.running == True:
            await ctx.send(embed=warn_embed("The AI is thinking right now, You can't talk to her while she is thinking"), ephemeral=True)
            return
        await ctx.response.defer(ephemeral=True)
        self.running = True
        # name = ctx.user.global_name if ctx.user.global_name != None else ctx.user.display_name
        # if name == "HackedMahiro": name = "Mahiro"
        # print(f"{name}: {message}")
        # response= get_response(f"{name}: {message}",message)
        if model == None: response= generate(message)
        else: response= generate(message,model)
        # if response == False:
        #     await ctx.send(embed=debug_embed("Cleared!"))
        #     return
        await ctx.send(embed=info_embed(response,title=None,footer=
            "The output will not save in the history of the AI or any kinda of a File."+
            " If you don't Believe me You can Check The Source code of the Bot",
            author=[self.client.user.display_name,self.client.user.avatar.url]), ephemeral=True)
        self.running = False

    @commands.Cog.listener()
    async def on_message(self, message:Message):
        try: featureInside(message.guild.id,self)
        except: return
        if message.mention_everyone: return
        elif self.client.user.mentioned_in(message):  # Check if the bot is mentioned in the message
            try: 
                if message.guild.id not in AI_AllowedServers :return
            except:return
            if self.running == True:
                await message.reply(embed=warn_embed("The AI is thinking right now, You can't talk to her while she is thinking"), ephemeral=True)
                return
            message.content = message.content.replace("<@1251656934960922775>","Negomi")\
                .replace("  ", " ").replace("  ", " ")
            await message.channel.trigger_typing()
            emoji = "<a:loading:1268004524426006578>"
            await message.add_reaction(emoji)

            name = message.author.global_name if message.author.global_name != None else\
                  message.author.display_name
            
            if name == "HackedMahiro Hachiro": name = "Mahiro"
            channel = message.channel
            if (self.started == False) and (message.reference):
                self.started = True
                reference = await channel.fetch_message(message.reference.message_id)
                if  reference.author.id ==\
                      self.client.user.id:
                    previousContent= reference.content
            else: previousContent = None

            # print(f"{name}: {message}")
            response= get_response(f"{name}: {message.content}",
                                   message.content,previousContent)
            if response == False:
                await message.reply(embed=debug_embed("Cleared!"))
                return
            await message.reply(response)
            await message.remove_reaction(emoji,self.client.user)
    
    
        


    
    

def setup(client):
    client.add_cog(AI(client))