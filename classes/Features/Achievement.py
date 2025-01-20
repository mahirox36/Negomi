from modules.Nexon import *



class Achievement(commands.Cog):
    def __init__(self, client:Bot):
        self.client = client
    
    

def setup(client):
    client.add_cog(Achievement(client))