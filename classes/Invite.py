import nextcord
import nextcord as discord
from nextcord import *
from nextcord.ext import commands
from nextcord import Interaction as init
from Lib.Side import *
from Lib.Hybrid import setup_hybrid, userCTX
import os
import json

class Invite(commands.Cog):
    def __init__(self, client:Client):
        self.client = client
        self.Hybrid = setup_hybrid(client)
    
    

def setup(client):
    client.add_cog(Invite(client))