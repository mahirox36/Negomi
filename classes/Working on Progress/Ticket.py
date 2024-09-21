import nextcord
import nextcord as discord
from nextcord import *
from nextcord.ext import commands
from nextcord.ext.commands import Context, command
from nextcord.ext.application_checks import *
from nextcord import Interaction as init
from Lib.Side import *
from Lib.Logger import *
import os
import json

class Ticket(commands.Cog):
    def __init__(self, client:Client):
        self.client = client
    
    
    

def setup(client):
    client.add_cog(Ticket(client))