from modules.Nexon import *

class Updates(commands.Cog):
    def __init__(self, client:Bot):
        self.client = client
        
    @commands.Cog.listener()
    async def on_message(self, message:Message):
        if message.author.bot:
            return
        userData = UserData(message.author)
        userData.incrementMessageCount(message)
    
    
    @slash_command()
    async def account(ctx):
        await ctx.respond(f"Hello !")
    
    

def setup(client):
    client.add_cog(Updates(client))