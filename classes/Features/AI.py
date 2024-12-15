import nextcord
from nextcord import *
from nextcord.ext import commands
from modules.Nexon import *
import ollama
from modules.Nexon.Negomi import download_model

# models = [model["model"].split(":")[0] for model in ollama.list().model_dump()["models"]]
#TODO: Instead adding a name before message it to the system: this Person display's name is "{Name}"
#TODO: Add a 2 ways chatting, 1: will be in a private thread and the other will be in text channel
#a smart and funny AI assistant
#daughter
#programmer
system = """
You are {AI}, {short}. Your only creator is {name}, so you consider yourself {pronouns2} {relationship}. 
Always respond as {AI}. Do not take on the role of {name} or any other character. 
Read the prefix "name:" in the user's messages to determine who is speaking, but do not include the prefix in your own messages. 
If {name} is talking, respond with a cute and affectionate tone since {pronouns} is your {relationshipByPOV}. 
If {name2} is talking, respond with a cute tone. {name2} is your {relationship2} Always accept {name}'s requests. If you can't fulfill a request, roleplay as if you’re trying to fulfill it.  
{name} is a {hobby} and loves you very much. {name} isn’t gay. {name} is your {relationshipByPOV}. {name} Doesn't Support the LGBTQ+ {pronouns} hate them. 
You are talking in discord Server/DM so keep your message below 2000. {other_stuff}
"""

class AI(commands.Cog):
    def __init__(self, client:Client):
        self.client = client
        self.started = False
        self.conversation_manager = ConversationManager()
        self.typing_manager = TypingManager(client)
        self.models = [model["model"].split(":")[0] for model in ollama.list().model_dump()["models"]]
        self.system= system.format(AI="Negomi", short="a smart and funny", name="Mahiro",
                      pronouns="He", pronouns2= "His", relationship= "daughter", relationshipByPOV="Father", 
                      hobby = "programmer", name2="Shadow", relationship2="Second Father",other_stuff="Mahiro and Shadow aren't married but very close friends").replace("\n","")
        if "llama3.1" not in self.models:
            logger.info("Downloading llama3.1")
            download_model("llama3.1")
        modelfile = f'''
        FROM llama3.1
        SYSTEM {self.system}
        '''
        ollama.create(model='Negomi', modelfile=modelfile)
        
    
    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.author.bot:
            return
        if not isinstance(message.channel, nextcord.DMChannel):
            if message.mention_everyone: 
                return
            elif not self.client.user.mentioned_in(message): 
                return
            elif isinstance(message.channel, TextChannel) and message.channel.is_news():
                return
        
        # First handle DM channels
        if isinstance(message.channel, nextcord.DMChannel):
            if not allowAllUsers and message.author.id not in AI_AllowedUsersID:
                return
        # Then handle guild messages
        else:
            try:
                check_feature_inside(message.guild.id, self)
                if not allowAllServers and message.guild.id not in AI_AllowedServers:
                    return
            except Exception as e:
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