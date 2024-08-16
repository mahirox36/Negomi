import nextcord
import nextcord as discord
from nextcord import *
from nextcord.ext import commands
from nextcord.ext.application_checks import *
from nextcord.ext.commands import Context, command, Bot
from nextcord import Interaction as init
from Lib.Side import *
from Lib.Logger import *
import os
import json



class Plugins(commands.Cog):
    def __init__(self, client: Bot):
        self.client = client
    
    

def setup(client):
    client.add_cog(Plugins(client))