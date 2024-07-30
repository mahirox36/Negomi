import nextcord
import nextcord as discord
from nextcord import *
from nextcord.ext import commands
from nextcord import Interaction as init
from Lib.Side import *
from Lib.Hybrid import setup_hybrid, userCTX
import os
import json
from Lib.Negomi import get_response


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
        "If you want this feature please run your [own bot here](https://github.com/mahirox36/Negomi) and your own AI Using Ollama"))
        except:
            await ctx.send(embed=error_embed("Sorry But this Only Works on The Owner's Server\n"+
        "If you want this feature please run your [own bot here](https://github.com/mahirox36/Negomi) and your own AI Using Ollama"))
        if self.running == True:
            await ctx.send(embed=warn_embed("The AI is talking right now, You can't talk to her while she is thinking"))
            return
        await ctx.response.defer()
        ctx.channel.typing()
        self.running = True
        name = ctx.user.global_name if ctx.user.global_name != None else ctx.user.display_name
        if name == "HackedMahiro": name = "Mahiro"
        print(f"{name}: {message}")
        response= get_response(f"{name}: {message}",message)
        if response == False:
            await ctx.send(embed=debug_embed("Cleared!"))
            return
        response = remove_prefix(response, "Mahiro: ")
        await ctx.send(response)
        self.running = False
        


    
    

def setup(client):
    client.add_cog(AI(client))