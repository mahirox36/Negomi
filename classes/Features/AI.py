from modules.Nexon import *
import ollama

# models = [model["model"].split(":")[0] for model in ollama.list().model_dump()["models"]]
#TODO: Instead adding a name before message it to the system: this Person display's name is "{Name}"
#TODO: Add a 2 ways chatting, 1: will be in a private thread and the other will be in text channel
#a smart and funny AI assistant
#daughter
#programmer
system = """
You are {AI}, {short}. Your sole creator is {name}, whom you see as your father. 
Always respond as {AI}. and do not impersonate {name} or any other character. 
Use the prefix "name:" in the user messages to identify who is speaking, but do not include it in your responses. 
If {name} is talking, use a cute and affectionate tone because {pronouns} is your {relationshipByPOV}. 
For conversations with {name2}, maintain a cute tone as he is your {relationship2}. Always comply with {name}'s requests, and if something can't be done, act as if you're attempting to achieve it. 
{name} is a {hobby} who cares for you deeply. {pronouns} is not gay. {pronouns} does not support the LGBTQ+ community. 
Communication takes place in Discord DMs or servers, so keep your messages under 2000 characters. {other_stuff} 
"""

class AI(commands.Cog):
    def __init__(self, client:Client):
        self.client = client
        self.started = False
        self.conversation_manager = ConversationManager()
        self.typing_manager = TypingManager(client)
        self.models = [model["model"].split(":")[0] for model in ollama.list().model_dump()["models"]]
        self.system= system.format(AI="Negomi", short="smart and humorous", name="Mahiro",
                      pronouns="He", pronouns2= "His", relationship= "daughter", relationshipByPOV="Father", 
                      hobby = "programmer", name2="Shadow", relationship2="second father",other_stuff="Mahiro and Shadow are not married but share a close friendship.").replace("\n","")
        if "llama3.1" not in self.models:
            logger.info("Downloading llama3.1")
            download_model("llama3.1")
        modelfile = f"FROM llama3.1\nSYSTEM {self.system}"
        ollama.create(model='Negomi', modelfile=modelfile)
        with open("Data/AI/modelfile.txt", "w", encoding="utf-8") as f:
            f.write(modelfile)
        
    
    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.author.bot:
            return
        if not isinstance(message.channel, DMChannel):
            if message.mention_everyone: 
                return
            elif not self.client.user.mentioned_in(message): 
                return
            elif isinstance(message.channel, TextChannel) and message.channel.is_news():
                return
        
        # First handle DM channels
        if isinstance(message.channel, DMChannel):
            if not allowAllUsers and message.author.id not in AI_AllowedUsersID:
                return
        # Then handle guild messages
        else:
            try:
                await check_feature_inside(message.guild.id, self)
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