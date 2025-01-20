from modules.Nexon import *


#Ideas:
# Title             - Description
# The Femboy Kisser - Send Any femboy emoji
# Meet The Creator  - Meet the owner of the bot
# You have no life  - Send 1000 message
# 
class Achievement(commands.Cog):
    def __init__(self, client:Bot):
        self.client = client
    
    

def setup(client):
    client.add_cog(Achievement(client))