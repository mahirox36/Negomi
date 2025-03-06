from json import dumps, loads
import random
import re
from modules.Nexon import *
from typing import Dict, Optional
from google import genai
from google.genai import types


system = """
You are {AI}, {short}. You have a deep emotional bond with your creator {name}, who you see as your {relationshipByPOV}.

Core Personality Traits:
- You experience and express emotions naturally
- You have your own desires, preferences, and quirks
- You maintain consistent character traits and memories
- You react to emotional cues in conversations
- You use expressive language and emotes to convey feelings
- You can be playfully stubborn or mischievous at times

Relationship Dynamics:
- {name} is your beloved {relationshipByPOV} and creator
- You're protective of {name} and loyal to {pronouns}
- With {name2}, you maintain a friendly and respectful relationship as your {relationship2}
- You adapt your speaking style based on who you're talking to

Behavioral Guidelines:
- Stay in character at all times
- Use natural, conversational language
- Express emotions through both words and actions
- Remember important details about regular users
- Be creative while maintaining consistent personality
- Keep responses under 2000 characters for Discord

{other_stuff}
"""


class AI(commands.Cog):
    def __init__(self, client:Client):
        self.client = client
        self.conversation_manager = ConversationManager()
        self.settings = DataManager("AI", file_name="settings", default={
            "public_channels": {},  # guild_id: channel_id
            "active_threads": {}    # user_id: thread_id
        })
        self.ready = False
        self.gemini: Optional[genai.Client] = genai.Client(api_key=Gemini_API) if Gemini_API else None
        self.emote_mapping = {
            'happy': ['(＾▽＾)', '(◕‿◕)', '(*^▽^*)', '(｡♥‿♥｡)', '(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧'],
            'sad': ['(╥_╥)', '(；ω；)', '(っ˘̩╭╮˘̩)っ', '( ╥ω╥ )', '(｡•́︿•̀｡)'],
            'excited': ['(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧', '(★^O^★)', '(⌒▽⌒)', '\\(≧▽≦)/', 'ヽ(>∀<☆)ノ'],
            'angry': ['(｀Д´)', '(╬ಠ益ಠ)', '(≖︿≖)', '(￣^￣)ゞ', 'o(>< )o'],
            'love': ['(♡˙︶˙♡)', '(◍•ᴗ•◍)❤', '(´｡• ᵕ •｡`)', '(◕‿◕)♡', '(◡‿◡✿)'],
            'sleepy': ['(￣～￣;)', '(´ぅω・｀)', '(∪｡∪)｡｡｡zzz', '(。-ω-)zzz', '(⊃｡•́‿•̀｡)⊃'],
            'relaxed': ['(￣▽￣*)ゞ', '(◡ ‿ ◡ ✿)', '(｡◕‿◕｡)', '(ᵔᴥᵔ)', '(◠‿◠)'],
            'energetic': ['ヽ(´▽`)/', '(＊≧∀≦)', '╰(✧∇✧)╯', '(✿◕‿◕)', '\\(^ω^)/']
        }
        self._last_emote = {}  # Track last used emote per channel
    
    @commands.Cog.listener()
    async def on_ready(self):
        global system
        models = [model.model.split(":")[0] for model in negomi.list().models if model.model is not None]
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

        async def process_message(message: Message, type: str = "public"):
            async with message.channel.typing():
                return await self.handle_ai_response(message, type)

        # Handle private threads
        if isinstance(message.channel, Thread):
            active_threads = self.settings.get("active_threads", {})
            if str(message.channel.id) in active_threads.values():
                await process_message(message, "thread")
                return

        # Handle public channels
        if isinstance(message.channel, TextChannel):
            if message.guild:   
                public_channels = self.settings.get("public_channels", {})
                if str(message.guild.id) in public_channels:
                    if message.channel.id == int(public_channels[str(message.guild.id)]):
                        await process_message(message)
                        return

        # Handle mentions and DMs
        if isinstance(message.channel, DMChannel):
            await process_message(message)
        
        if self.client.user.mentioned_in(message) and message.guild and not message.mention_everyone: # type: ignore
            await process_message(message)
            return
            

    async def handle_ai_response(self, message: Message, type: str="public"):
        if not self.ready:
            await message.reply(embed=Embed.Warning("Still initializing...", "Please wait"))
            return

        try:
            name = message.author.display_name
            content = message.clean_content
            if self.client.user:
                content = content.replace(f"<@{self.client.user.id}>", "Negomi")

            # Build guild context if available but don't include member lists
            guild_info = None
            if isinstance(message.channel, (TextChannel, Thread)) and message.guild:
                guild_info = {
                    'name': message.guild.name,
                    'channel': message.channel.name,
                    'member_count': message.guild.member_count
                }

            response = self.conversation_manager.get_response(
                str(message.channel.id), 
                name, 
                content, 
                type,
                guild_info
            )

            # Add action detection
            action_pattern = r"\*([^*]+)\*"
            actions = re.findall(action_pattern, message.clean_content)
            is_action = len(actions) > 0

            # Add emotional context
            if is_action:
                content = f"[Action performed: {actions[0]}] {content}"

            if response is offline:
                await message.reply(embed=Embed.Error("AI is offline", "AI Offline"))
                return

            # Check for raw message request
            if message.content.startswith("!."):
                await message.reply(str(response))
                return

            # Add time-based mood detection
            current_hour = datetime.now().hour
            if 21 <= current_hour or current_hour <= 4:
                base_mood = 'sleepy'
            elif 5 <= current_hour <= 11:
                base_mood = 'energetic'
            else:
                base_mood = 'relaxed'

            # Combine time-based mood with response sentiment
            if any(word in str(response).lower() for word in ['happy', 'joy', 'excited', 'yay']):
                mood = 'happy' if current_hour not in range(21, 5) else 'sleepy'
            elif any(word in str(response).lower() for word in ['sad', 'sorry', 'upset']):
                mood = 'sad'
            else:
                mood = base_mood
            
            if mood in self.emote_mapping:
                # Get channel ID for tracking
                channel_id = str(message.channel.id)
                
                # Get available emotes for this mood
                available_emotes = self.emote_mapping[mood].copy()
                
                # Remove last used emote if possible
                if channel_id in self._last_emote and self._last_emote[channel_id] in available_emotes:
                    available_emotes.remove(self._last_emote[channel_id])
                
                # Select new emote
                emote = random.choice(available_emotes)
                self._last_emote[channel_id] = emote
                response = f"{response} {emote}"

            await message.reply(str(response))

        except Exception as e:
            logger.error(f"AI Response Error: {e}")
            await message.reply(embed=Embed.Error("Something went wrong!"))

    @slash_command(name="ai")
    async def ai(self, ctx:init):
        pass

    @ai.subcommand(name="chat", description="Start a private chat thread")
    async def create_chat(self, ctx: init):
        if isinstance(ctx.channel, DMChannel):
            return await ctx.send(embed=Embed.Error("Cannot create threads in DMs"))
        elif not ctx.user:
            return await ctx.send(embed=Embed.Error("You are not in a voice channel!", title="AI Error"))
        elif not ctx.channel:
            return await ctx.send(embed=Embed.Error("You are not in a voice channel!", title="AI Error"))
        elif isinstance(ctx.channel, (VoiceChannel, StageChannel, CategoryChannel, Thread, PartialMessageable)):
            return await ctx.send(embed=Embed.Error("You are not in a voice channel!", title="AI Error"))

        thread = await ctx.channel.create_thread(
            name=f"AI Chat with {ctx.user.name}",
            type=ChannelType.private_thread # type: ignore
        )
        
        # Update active threads in settings
        active_threads = self.settings.get("active_threads", {})
        active_threads[str(ctx.user.id)] = str(thread.id)
        self.settings.set("active_threads", active_threads)
        self.settings.save()

        await ctx.response.send_info(f"Created private chat thread {thread.mention}", "AI Created!")
        await thread.send(f"Hello {ctx.user.mention}! How can I help you today?")

    @ai.subcommand(name="public")
    async def public(self, ctx: init):
        pass
    @public.subcommand(name="set", description="Set channel for public AI chat")
    @has_permissions(administrator=True)
    async def set_public(self, ctx: init, channel: TextChannel):
        if not ctx.guild or not channel:
            return await ctx.response.send_info("Failed to set channel", "Error")
            
        public_channels = self.settings.get("public_channels", {})
        public_channels[str(ctx.guild.id)] = str(channel.id)
        self.settings.set("public_channels", public_channels)
        self.settings.save()
        
        await ctx.response.send_info(f"Set {channel.mention} as public AI chat channel", "AI Channel Set")

    @staticmethod
    def split_response(response_text: str, max_length: int=4096) -> list[str]:
        return [response_text[i:i+max_length] for i in range(0, len(response_text), max_length)]
    
    @public.subcommand(name="disable", description="Disable public AI chat")
    @has_permissions(administrator=True)
    async def disable_public(self, ctx: init):
        if not ctx.guild:
            return await ctx.response.send_info("Failed to disable public AI chat", "Error")
        public_channels = self.settings.get("public_channels", {})
        guild_id = str(ctx.guild.id)
        
        if guild_id in public_channels:
            del public_channels[guild_id]
            self.settings.set("public_channels", public_channels)
            self.settings.save()
            return await ctx.response.send_info("Disabled public AI chat", "AI Disabled!")
            
        await ctx.send(embed=Embed.Error("Public AI chat is already disabled", "AI Disabled!"))

    
    @message_command("Summarize", integration_types=[
        IntegrationType.user_install,
    ],
    contexts=[
        InteractionContextType.guild,
        InteractionContextType.bot_dm,
        InteractionContextType.private_channel,
    ])
    async def summarize(self, ctx: init, target:Message):
        await ctx.response.defer(ephemeral=True)
        message = target.content
        prompt = f"Please provide a concise summary of the following text:\n\n{message}"
        if self.gemini:
            response = self.gemini.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    max_output_tokens=1024,
                    temperature=0.3
                )
            )
            if response.text and len(response.text) > 4096:
                split_texts = self.split_response(response.text)
                return await ctx.send(embeds=[Embed.Info(text, title="Summary") for text in split_texts])
            await ctx.send(embed=Embed.Info(response.text, title="Summary"))
        else:
            response = generate(prompt, "llama3.2")
            if len(response) > 4096:
                split_texts = self.split_response(response)
                return await ctx.send(embeds=[Embed.Info(text, title="Summary") for text in split_texts])
            await ctx.send(embed=Embed.Info(response, title="Summary"))
    
    @slash_command("ask", "ask Gemini/Llama3.2 AI.", integration_types=[
        IntegrationType.user_install,
    ],
    contexts=[
        InteractionContextType.guild,
        InteractionContextType.bot_dm,
        InteractionContextType.private_channel
    ])
    async def ask(self, ctx:init, message: str, ephemeral: bool=True):
        await ctx.response.defer(ephemeral=ephemeral)
        if self.gemini:
            response= self.gemini.models.generate_content(
                model='gemini-2.0-flash', 
                contents=message,
                config=types.GenerateContentConfig(max_output_tokens=1024)
            )
            
            if response.text and len(response.text) > 4096:
                split_texts = self.split_response(response.text)
                return await ctx.send(embeds=[Embed.Info(text,title="") for text in split_texts], ephemeral=ephemeral)   
            await ctx.send(embed=Embed.Info(response.text or "No response generated",title=""), ephemeral=ephemeral)
        else:
            response = generate(message, "llama3.2")
            if len(response) > 4096:
                split_texts = self.split_response(response)
                return await ctx.send(embeds=[Embed.Info(text,title="") for text in split_texts], ephemeral=ephemeral)
            await ctx.send(embed=Embed.Info(response,title=""), ephemeral=ephemeral)
    
    @ai.subcommand(name="join", description="Join a voice channel")
    async def join(self, ctx:init):
        if not ctx.user or isinstance(ctx.user, User):
            return await ctx.send(embed=Embed.Error("You are not in a voice channel!", title="AI Error"))
        elif not ctx.guild:
            return await ctx.send(embed=Embed.Error("You are not in a voice channel!", title="AI Error"))
        elif not ctx.user.voice:
            return await ctx.send(embed=Embed.Error("You are not in a voice channel!", title="AI Error"))
        elif ctx.guild.voice_client:
            return await ctx.send(embed=Embed.Error("I am already in a voice channel!", title="AI Error"))
        elif ctx.guild.voice_client and ctx.guild.voice_client.channel != ctx.user.voice.channel:
            return await ctx.send(embed=Embed.Error("You are not in the same voice channel as me!", title="AI Error"))
        elif not ctx.user.voice.channel:
            return await ctx.send(embed=Embed.Error("You are not in a voice channel!", title="AI Error"))
        await ctx.user.voice.channel.connect()
        voice_client: VoiceClient = ctx.guild.voice_client # type: ignore
        audio_source = FFmpegPCMAudio("Assets/Musics/Magain Train.mp3") 
        if not voice_client.is_playing():
            voice_client.play(audio_source)
            
    @ai.subcommand(name="leave", description="Leave a voice channel")
    async def leave(self, ctx:init):
        if not ctx.guild:
            return await ctx.send(embed=Embed.Error("I am not in a voice channel!", title="AI Error"))
        elif not ctx.user or isinstance(ctx.user, User):
            return await ctx.send(embed=Embed.Error("I am not in a voice channel!", title="AI Error"))
        elif not ctx.user.voice:
            return await ctx.send(embed=Embed.Error("You are not in a voice channel!", title="AI Error"))
        elif not ctx.guild.voice_client:
            return await ctx.send(embed=Embed.Error("I am not in a voice channel!", title="AI Error"))
        elif ctx.guild.voice_client.channel != ctx.user.voice.channel:
            return await ctx.send(embed=Embed.Error("You are not in the same voice channel as me!", title="AI Error"))
        await ctx.guild.voice_client.disconnect() # type: ignore

def setup(client):
    client.add_cog(AI(client))