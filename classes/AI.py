import nextcord
import nextcord as discord
from nextcord import *
from nextcord.ext import commands
from nextcord import Interaction as init
from Lib.Side import *
from Lib.Hybrid import setup_hybrid, userCTX
import os
import json
from Lib.Negomi import get_response, generate


class AI(commands.Cog):
    def __init__(self, client:Client):
        self.client = client
        self.Hybrid = setup_hybrid(client)
        self.running = False
    
    @slash_command(name="ask",description="as an Advance AI")
    async def Say(self,ctx:init,message:str):
        try:
            if ctx.guild.id != TESTING_GUILD_ID:
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
        response= generate(message)
        # if response == False:
        #     await ctx.send(embed=debug_embed("Cleared!"))
        #     return
        await ctx.send(embed=info_embed(response,title=None,footer=
            "The output will not save in the history of the AI or any kinda of a File."+
            " If you don't Believe me You can Check The Source code of the Bot",
            author=[self.client.user.display_name,self.client.user.avatar.url]), ephemeral=True)
        self.running = False
    
    
        


    
    

def setup(client):
    client.add_cog(AI(client))