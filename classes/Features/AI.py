from asyncio import sleep
import nextcord
import nextcord as discord
from nextcord import *
from nextcord.ext import commands
from nextcord import Interaction as init, SlashOption
from modules.Nexon import *
import ollama
import os
import json

models = [model["name"].split(":")[0] for model in ollama.list()["models"]]


class AI(commands.Cog):
    def __init__(self, client:Client):
        self.client = client
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
        await ctx.response.defer(ephemeral=True)
        # name = ctx.user.global_name if ctx.user.global_name != None else ctx.user.display_name
        # if name == "HackedMahiro": name = "Mahiro"
        # logger.info(f"{name}: {message}")
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

    @commands.Cog.listener()
    async def on_message(self, message:Message):
        if message.mention_everyone: return
        elif not self.client.user.mentioned_in(message): return  # Check if the bot is mentioned in the message
        skip = True if isinstance(message.channel, nextcord.DMChannel) and message.author.id in AI_AllowedUsersID else False
        if not skip:
            try: featureInside(message.guild.id,self)
            except: return
            try: 
                if message.guild.id not in AI_AllowedServers :return
            except: return
        content = message.content.replace(f"<@{self.client.user.id}>","Negomi")\
            .replace("  ", " ").replace("  ", " ")
        await message.channel.trigger_typing()  # Ensure this always runs
        emoji = "<a:loading:1308521205308854353>"
        if not skip:
            await message.add_reaction(emoji)

        try:
            name = get_name(message.author)
            if name == "HackedMahiro Hachiro":
                name = "Mahiro"

            channel = message.channel
            previousContent = None
            if (self.started == False) and (message.reference):
                self.started = True
                reference = await channel.fetch_message(message.reference.message_id)
                if reference.author.id == self.client.user.id:
                    previousContent = reference.content

            # Generate response
            response = get_response(
                message.author.id, f"{name}: {content}", content, previousContent
                )

            if response is False:
                await message.reply(embed=debug_embed("Conversation history cleared!"))
                return
            
            if not response:  # Handle empty or invalid responses
                await message.reply(embed=error_embed("I couldn't generate a response, sorry!"))
                return

            logger.info(response)
            await message.reply(response)

        except Exception as e:
            logger.error(f"Error in talk: {e}")
            await message.reply(embed=error_embed("Something went wrong!"))

        finally:
            # Always remove reaction
            logger.info("Do this")
            if not skip:
                logger.info("Remove")
                await message.remove_reaction(emoji, self.client.user)
            logger.info("Do this 2")

        

    
        


    
    

def setup(client):
    client.add_cog(AI(client))