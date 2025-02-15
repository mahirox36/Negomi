from json import dumps, loads
from modules.Nexon import *
from typing import Dict, Optional
from google import genai
from google.genai import types


system = """
You are {AI}, {short}. Your sole creator is {name}, whom you see as your father. 
Always respond as {AI}. and do not impersonate {name} or any other character. 
Use the prefix "name:" in the user messages to identify who is speaking, but do not include it in your responses. 
If {name} is talking, use a cute and affectionate tone because {pronouns} is your {relationshipByPOV}. 
For conversations with {name2}, maintain a cute tone as he is your {relationship2}. Always comply with {name}'s requests, and if something can't be done, act as if you're attempting to achieve it. 
{name} is a {hobby} who cares for you deeply. {pronouns} is not gay. {pronouns} does not support the LGBTQ+ community. 
Communication takes place in Discord DMs or servers, so keep your messages under 2000 characters. {other_stuff} 
"""

#TODO: add a summarize message command
class AI(commands.Cog):
    def __init__(self, client:Client):
        self.client = client
        self.conversation_manager = ConversationManager()
        self.typing_manager = TypingManager(client)
        self.settings = DataManager("AI", file="settings", default={
            "public_channels": {},  # guild_id: channel_id
            "active_threads": {}    # user_id: thread_id
        })
        self.ready = False
        self.gemini: Optional[genai.Client] = genai.Client(api_key=Gemini_API) if Gemini_API else None
    
    @commands.Cog.listener()
    async def on_ready(self):
        global system
        models = [model.model.split(":")[0] for model in  negomi.list().models]
        system= system.format(AI="Negomi", short="smart and humorous", name="Mahiro",
                      pronouns="He", pronouns2= "His", relationship= "daughter", relationshipByPOV="Father", 
                      hobby = "programmer", name2="Shadow", relationship2="second father",other_stuff="Mahiro and Shadow are not married but share a close friendship.").replace("\n","")
        from_ = "llama3.2"
        if from_ not in models:
            logger.info("Downloading llama3.2")
            await download_model(from_)
        negomi.create(model='Negomi', from_=from_, system=system)
        with open("Data/Features/AI/system.txt", "w", encoding="utf-8") as f:
            f.write(system)
        self.ready = True
    
    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.author.bot:
            return

        # Handle private threads
        if isinstance(message.channel, Thread):
            active_threads = self.settings.get("active_threads", {})
            if str(message.channel.id) in active_threads.values():
                await self.handle_ai_response(message, "thread")
                return

        # Handle public channels
        if isinstance(message.channel, TextChannel):
            public_channels = self.settings.get("public_channels", {})
            if str(message.guild.id) in public_channels:
                if message.channel.id == int(public_channels[str(message.guild.id)]):
                    await self.handle_ai_response(message)
                    return

        # Handle mentions and DMs
        if isinstance(message.channel, DMChannel) or self.client.user.mentioned_in(message):
            await self.handle_ai_response(message)

    async def handle_ai_response(self, message: Message, type: str="public"):
        if not self.ready:
            await message.reply(embed=warn_embed("AI is still starting up", "AI Warning"))
            return

        try:
            await self.typing_manager.start_typing(message.channel.id)
            name = get_name(message.author)
            content = message.clean_content.replace(f"<@{self.client.user.id}>", "Negomi")

            response = self.conversation_manager.get_response(
                str(message.channel.id), name, content, type
            )

            if response is offline:
                await message.reply(embed=error_embed("AI is offline", "AI Offline"))
                return
            if response is False:
                await message.reply(embed=debug_embed("Conversation cleared!"))
                return
            if not response:
                await message.reply(embed=error_embed("Failed to generate response"))
                return

            await message.reply(response)

        except Exception as e:
            logger.error(f"AI Response Error: {e}")
            await message.reply(embed=error_embed("Something went wrong!"))
        finally:
            await self.typing_manager.stop_typing(message.channel.id)

    @slash_command(name="ai")
    async def ai(self, ctx:init):
        pass

    @ai.subcommand(name="chat", description="Start a private chat thread")
    async def create_chat(self, ctx: init):
        if isinstance(ctx.channel, DMChannel):
            await ctx.send(embed=error_embed("Cannot create threads in DMs"))
            return

        thread = await ctx.channel.create_thread(
            name=f"AI Chat with {ctx.user.name}",
            type=ChannelType.private_thread
        )
        
        # Update active threads in settings
        active_threads = self.settings.get("active_threads", {})
        active_threads[str(ctx.user.id)] = str(thread.id)
        self.settings.set("active_threads", active_threads)
        self.settings.save()

        await ctx.send(embed=info_embed(f"Created private chat thread {thread.mention}", "AI Created!"))
        await thread.send(f"Hello {ctx.user.mention}! How can I help you today?")

    @ai.subcommand(name="public")
    async def public(self, ctx: init):
        pass
    @public.subcommand(name="set", description="Set channel for public AI chat")
    @has_permissions(administrator=True)
    async def set_public(self, ctx: init, channel: TextChannel):
        public_channels = self.settings.get("public_channels", {})
        public_channels[str(ctx.guild.id)] = str(channel.id)
        self.settings.set("public_channels", public_channels)
        self.settings.save()
        
        await ctx.send(embed=info_embed(f"Set {channel.mention} as public AI chat channel", "AI Enabled!"))

    def split_response(response_text, max_length=4096):
        return [response_text[i:i+max_length] for i in range(0, len(response_text), max_length)]
    
    @public.subcommand(name="disable", description="Disable public AI chat")
    @has_permissions(administrator=True)
    async def disable_public(self, ctx: init):
        public_channels = self.settings.get("public_channels", {})
        guild_id = str(ctx.guild.id)
        
        if guild_id in public_channels:
            del public_channels[guild_id]
            self.settings.set("public_channels", public_channels)
            self.settings.save()
            return await ctx.send(embed=info_embed("Disabled public AI chat", "AI Disabled!"))
            
        await ctx.send(embed=error_embed("Public AI chat is already disabled", "AI Disabled!"))

    @slash_command("ask", "ask Gemini/Llama3.2 AI.", integration_types=[
        IntegrationType.user_install,
    ],
    contexts=[
        InteractionContextType.bot_dm,
        InteractionContextType.private_channel,
    ],)
    async def ask(self, ctx:init, message: str, ephemeral: bool=False):
        await ctx.response.defer(ephemeral=ephemeral)
        if self.gemini:
            response= self.gemini.models.generate_content(
                model='gemini-2.0-flash', 
                contents=message,
                config=types.GenerateContentConfig(max_output_tokens=1024)
            )
            
            if len(response.text) > 4096:
                split_texts = self.split_response(response.text)
                return await ctx.send(embeds=[info_embed(text,title="") for text in split_texts], ephemeral=ephemeral)   
            await ctx.send(embed=info_embed(response.text,title=""), ephemeral=ephemeral)
        else:
            response = generate(message, "llama3.2")
            if len(response) > 4096:
                split_texts = self.split_response(response)
                return await ctx.send(embeds=[info_embed(text,title="") for text in split_texts], ephemeral=ephemeral)
            await ctx.send(embed=info_embed(response,title=""), ephemeral=ephemeral)
    
    @ai.subcommand(name="join", description="Join a voice channel")
    async def join(self, ctx:init):
        if not ctx.user.voice:
            return await ctx.send(embed=error_embed("You are not in a voice channel!", title="AI Error"))
        elif ctx.guild.voice_client:
            return await ctx.send(embed=error_embed("I am already in a voice channel!", title="AI Error"))
        await ctx.user.voice.channel.connect()
        voice_client: VoiceClient = ctx.guild.voice_client
        audio_source = FFmpegPCMAudio("Assets/Musics/Magain Train.mp3") 
        if not voice_client.is_playing():
            voice_client.play(audio_source)
            
    @ai.subcommand(name="leave", description="Leave a voice channel")
    async def leave(self, ctx:init):
        if not ctx.guild.voice_client:
            return await ctx.send(embed=error_embed("I am not in a voice channel!", title="AI Error"))
        elif ctx.guild.voice_client.channel != ctx.user.voice.channel:
            return await ctx.send(embed=error_embed("You are not in the same voice channel as me!", title="AI Error"))
        await ctx.guild.voice_client.disconnect()

def setup(client):
    client.add_cog(AI(client))