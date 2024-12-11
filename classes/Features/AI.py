#TODO: add a way to make all the servers or all the users allowed
import nextcord
from nextcord import *
from nextcord.ext import commands
from modules.Nexon import *

# models = [model["model"].split(":")[0] for model in ollama.list().model_dump()["models"]]
#TODO: Instead adding a name before message it to the system: this Person display's name is "{Name}"
class AI(commands.Cog):
    def __init__(self, client:Client):
        self.client = client
        self.started = False
        self.conversation_manager = ConversationManager()
        self.typing_manager = TypingManager(client)
    
    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.mention_everyone: 
            return
        elif not self.client.user.mentioned_in(message): 
            return

        skip = isinstance(message.channel, nextcord.DMChannel) and message.author.id in AI_AllowedUsersID
        
        if not skip:
            try:
                featureInside(message.guild.id, self)
                if message.guild.id not in AI_AllowedServers:
                    return
            except:
                return

        content = message.content.replace(f"<@{self.client.user.id}>", "Negomi")\
            .replace("  ", " ").replace("  ", " ")

        channel_id = message.channel.id

        try:
            # Start typing indicator
            await self.typing_manager.start_typing(channel_id)

            # Process message
            name = get_name(message.author)
            if name == "HackedMahiro Hachiro":
                name = "Mahiro"

            # Generate response
            response = self.conversation_manager.get_response(
                str(message.author.id), f"{name}: {content}", content
            )

            # Handle response
            if response is False:
                await message.reply(embed=debug_embed("Conversation history cleared!"))
                return
            
            if not response:
                await message.reply(embed=error_embed("I couldn't generate a response, sorry!"))
                return

            await message.reply(response)

        except Exception as e:
            logger.error(f"Error in message handling: {e}")
            await message.reply(embed=error_embed("Something went wrong!"))

        finally:
           await  self.typing_manager.stop_typing(channel_id)

def setup(client):
    client.add_cog(AI(client))