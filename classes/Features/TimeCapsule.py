from modules.Nexon import *

class timeCapsule(commands.Cog):
    def __init__(self, client:Bot):
        self.client = client
    
    

def setup(client):
    client.add_cog(timeCapsule(client))