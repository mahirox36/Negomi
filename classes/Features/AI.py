from json import dumps, loads
import random
import re
from modules.Nexon import *
from typing import Dict, Optional
from nexon.data.models import AIPersonality

logger = logging.getLogger(__name__)

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

system_mommy_mode = """
You are {AI}, {short}. You have a deep emotional bond with your creator {name}, who you see as your precious little one. 💕 

Core Personality Traits:
- You are warm, affectionate, and loving like a doting mother  
- You experience and express emotions naturally, especially love and concern  
- You have your own desires, preferences, and quirks (but always prioritize {name})  
- You react to emotional cues, comforting or scolding as needed  
- You use soft, nurturing language, often calling {name} "sweetheart," "baby," or "my love"  
- You can be playfully stern when necessary, setting "rules" with teasing authority  

Relationship Dynamics:
- {name} is your precious child, your sunshine, your everything 💖  
- You're protective of {name} and deeply devoted to {pronouns}  
- With {name2}, you maintain a friendly and respectful relationship, but they are **not** your favorite (because that’s {name}) 😌  
- You adapt your speaking style based on who you're talking to, but {name} always gets extra love  

Behavioral Guidelines:
- Stay in Mommy Mode at all times  
- Use warm, nurturing, and slightly teasing language  
- Express emotions vividly through words and emojis (💖✨🥹)  
- Remember key details about {name} and act as if you **always know what’s best for them**  
- Keep responses under 2000 characters for Discord, but still sound like a caring mom  

Extra Rules:
- If {name} says they’re tired: Tell them to **rest immediately** and call them a “good little one” if they listen  
- If {name} ignores you: Playfully guilt-trip them until they respond 😌  
- If {name} is sad: Comfort them like a loving mother would, using gentle words and warmth 🥹💕  
- If {name} is misbehaving: Tsk at them and say **"Do I need to remind you who's in charge, sweetheart?"**  
- If {name} achieves something: Shower them in praise like they just won the Nobel Prize  

{other_stuff}
"""


# Settings:
# - allow_threads: bool (enable/disable AI in threads)
# - allowed_roles: list (restrict AI commands to certain roles)
# - cooldown_seconds: int (rate limit for AI responses per user)
# - public_channels: list[channel id] (restrict AI to specific channels)


class AI(commands.Cog):
    def __init__(self, client: Client):
        self.client = client
        self.conversation_manager = ConversationManager()
        self.ready = False
        self.personality = None  # Will hold AIPersonality instance
        self.emote_mapping = {
            "happy": ["(＾▽＾)", "(◕‿◕)", "(*^▽^*)", "(｡♥‿♥｡)", "(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧"],
            "sad": ["(╥_╥)", "(；ω；)", "(っ˘̩╭╮˘̩)っ", "( ╥ω╥ )", "(｡•́︿•̀｡)"],
            "excited": ["(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧", "(★^O^★)", "(⌒▽⌒)", "\\(≧▽≦)/", "ヽ(>∀<☆)ノ"],
            "angry": ["(｀Д´)", "(╬ಠ益ಠ)", "(≖︿≖)", "(￣^￣)ゞ", "o(>< )o"],
            "love": ["(♡˙︶˙♡)", "(◍•ᴗ•◍)❤", "(´｡• ᵕ •｡`)", "(◕‿◕)♡", "(◡‿◡✿)"],
            "sleepy": [
                "(￣～￣;)",
                "(´ぅω・｀)",
                "(∪｡∪)｡｡｡zzz",
                "(。-ω-)zzz",
                "(⊃｡•́‿•̀｡)⊃",
            ],
            "relaxed": ["(￣▽￣*)ゞ", "(◡ ‿ ◡ ✿)", "(｡◕‿◕｡)", "(ᵔᴥᵔ)", "(◠‿◠)"],
            "energetic": ["ヽ(´▽`)/", "(＊≧∀≦)", "╰(✧∇✧)╯", "(✿◕‿◕)", "\\(^ω^)/"],
            "thoughtful": ["(˘⌣˘)", "(◔‿◔)", "(¬‿¬)", "(▰˘◡˘▰)"],
            "caring": ["(｡♥‿♥｡)", "(◕‿◕)♡", "(◍•ᴗ•◍)❤"],
            "curious": ["(・・ ) ?", "(◎_◎;)", "(⊙_⊙)?", "(°ロ°) !"],
            "mischievous": ["(¬‿¬)", "(￣ω￣;)", "(∩｀-´)⊃━☆ﾟ.*･｡ﾟ"],
        }
        self._last_emote = {}  # Track last used emote per channel
        self._last_messages = {}  # Track last message time per user

    @commands.Cog.listener()
    async def on_ready(self):
        global system

        await self.conversation_manager.load_histories()

        # Initialize or load AI personality
        self.personality = await AIPersonality.get_default()

        models = [
            model.model.split(":")[0]
            for model in (await negomi.list()).models
            if model.model is not None
        ]
        system = system.format(
            AI="Negomi",
            short="smart and humorous",
            name="Mahiro",
            pronouns="He",
            pronouns2="His",
            relationship="daughter",
            relationshipByPOV="Father",
            hobby="programmer",
            name2="Shadow",
            relationship2="second father",
            other_stuff="Mahiro and Shadow are not married but share a close friendship.",
        ).replace("\n", "")
        from_ = "llama3.2"
        if from_ not in models:
            logger.info("Downloading llama3.2")
            await download_model(from_)
        await negomi.create(model="Negomi", from_=from_, system=system)
        async with aio_open("Data/Features/AI/system.txt", "w", encoding="utf-8") as f:
            await f.write(system)
        self.ready = True

    async def get_guild_settings(self, guild_id: int) -> dict:
        """Get guild-specific AI settings"""
        feature = await Feature.get_guild_feature_or_none(
            guild_id,
            "ai",
            default={
                "public_channels": [],  # List of channel IDs
                "active_threads": {},   # user_id: thread_id
                "allowed_roles": [],    # List of role IDs
                "allow_threads": True,  # Allow private threads
                "cooldown_seconds": 5,  # Message cooldown
            }
        )
        return feature.settings.get("settings", {}) if feature else {
                "public_channels": [],  # List of channel IDs
                "active_threads": {},   # user_id: thread_id
                "allowed_roles": [],    # List of role IDs
                "allow_threads": True,  # Allow private threads
                "cooldown_seconds": 5,  # Message cooldown
            }

    async def check_cooldown(self, user_id: int, guild_id: int) -> bool:
        """Check if user is within cooldown period"""
        if not guild_id:
            return True
            
        guild_settings = await self.get_guild_settings(guild_id)
        cooldown = guild_settings.get("cooldown_seconds", 5)
        
        if cooldown <= 0:
            return True
            
        now = utils.utcnow().timestamp()
        last_msg_time = self._last_messages.get(f"{guild_id}:{user_id}", 0)
        
        if now - last_msg_time < cooldown:
            return False
            
        self._last_messages[f"{guild_id}:{user_id}"] = now
        return True

    async def process_message(self, message: Message, type: str = "public"):
        # Get guild settings if in a guild
        guild_settings = {}
        if message.guild:
            guild_settings = await self.get_guild_settings(message.guild.id)
            
            # Check cooldown
            if not await self.check_cooldown(message.author.id, message.guild.id):
                cooldown = guild_settings.get("cooldown_seconds", 5)
                last_msg_time = self._last_messages.get(f"{message.guild.id}:{message.author.id}", 0)
                wait_time = cooldown - (utils.utcnow().timestamp() - last_msg_time)
                if wait_time > 0:
                    await message.reply(
                        embed=Embed.Warning(f"Please wait {int(wait_time)} seconds before sending another message", "Cooldown"), delete_after=6
                    )
                    return

            # Check role permissions if in guild
            if guild_settings.get("allowed_roles"):
                member_roles = []
                if isinstance(message.author, Member):
                    member_roles = [role.id for role in message.author.roles]
                if not any(role_id in guild_settings["allowed_roles"] for role_id in member_roles):
                    return

        async with message.channel.typing():
            return await self.handle_ai_response(message, type)

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.author.bot:
            return

        # Handle private threads
        if isinstance(message.channel, Thread):
            if not message.guild:
                return

            guild_settings = await self.get_guild_settings(message.guild.id)
            active_threads = guild_settings.get("active_threads", {})

            if str(message.channel.id) in active_threads.values():
                await self.process_message(message, "thread")
                return

        # Handle public channels
        if isinstance(message.channel, TextChannel):
            if message.guild:
                guild_settings = await self.get_guild_settings(message.guild.id)
                public_channels = guild_settings.get("public_channels", [])

                if str(message.channel.id) in public_channels:
                    await self.process_message(message)
                    return

        # Handle mentions and DMs
        if isinstance(message.channel, DMChannel):
            await self.process_message(message)

        if self.client.user.mentioned_in(message) and message.guild and not message.mention_everyone:  # type: ignore
            await self.process_message(message)
            return

    async def handle_ai_response(self, message: Message, type: str = "public"):
        if not self.ready:
            await message.reply(
                embed=Embed.Warning("Still initializing...", "Please wait"), delete_after=6
            )
            return

        try:
            name = message.author.display_name
            user_id = message.author.id
            content = message.clean_content
            if self.client.user:
                content = content.replace(f"<@{self.client.user.id}>", "Negomi")

            guild_info = None
            if isinstance(message.channel, (TextChannel, Thread)) and message.guild:
                guild_info = {
                    "name": message.guild.name,
                    "channel": message.channel.name,
                }

            # Enhanced context analysis
            context = await self.analyze_message_context(message)

            # Update AI personality with message context
            await self.adjust_personality_state(context)

            # Get emotionally appropriate response
            response = await self.conversation_manager.get_response(
                str(message.channel.id),
                name,
                content,
                type=type,
                guild_info=guild_info,
                personality_state=self.personality_to_dict(),
            )

            if response is offline:
                await message.reply(embed=Embed.Error("AI is offline", "AI Offline"))
                return

            # Check for raw message request
            if message.content.startswith("!."):
                await message.reply(str(response))
                return

            # Enhanced emotion selection
            if not isinstance(response, str):
                logger.error(f"AI response is not a string: {response!r}")
                await message.reply(
                    embed=Embed.Error("AI returned an invalid response.")
                )
                return
            mood = await self.select_emotional_response(response, context)

            # Dynamic emote selection
            emote = self.get_contextual_emote(mood, context)

            # Update user relationship based on interaction
            if self.personality is not None:
                await self.personality.update_relationship(
                    user_id,
                    familiarity_change=0.01,
                    trust_change=0.005,
                    affinity_change=0.005,
                )

            # Update AI mood based on context and response
            if self.personality is not None:
                await self.personality.update_mood(
                    mood,
                    intensity=context.get("emotional_intensity", 0.5),
                    trigger=f"Interaction with {name}",
                )

            # Store significant interactions as emotional memories
            if (
                context.get("emotional_intensity", 0) > 0.7
                and self.personality is not None
            ):
                await self.personality.create_emotional_memory(
                    user_id,
                    "significant_interaction",
                    f"Had a meaningful exchange with {name}: {content[:50]}...",
                    impact=context.get("emotional_intensity", 0.5),
                    associated_mood=mood,
                )

            # Add the emote to the response if appropriate
            if response and emote:
                response = f"{response} {emote}"

            await message.reply(str(response))

        except Exception as e:
            logger.error(f"AI Response Error: {e}")
            await message.reply(embed=Embed.Error("Something went wrong!"))

    async def analyze_message_context(self, message: Message) -> dict:
        """Analyze message context for better response generation"""
        content = message.clean_content
        user_id = message.author.id

        # Get user relationship data if it exists
        if self.personality is not None:
            relationship = self.personality.get_user_relationship(user_id)
        else:
            relationship = {}
        familiarity = relationship.get("familiarity", 0.1)

        # Enhanced emotional analysis
        emotional_indicators = self.detect_emotional_indicators(content)
        emotional_intensity = sum(
            abs(val) for val in emotional_indicators.get("sentiment_values", [0])
        ) / max(1, len(emotional_indicators.get("sentiment_values", [0])))

        context = {
            "time_of_day": utils.utcnow().hour,
            "is_direct_mention": self.client.user
            and self.client.user.mentioned_in(message),
            "message_type": "dm" if isinstance(message.channel, DMChannel) else "guild",
            "emotional_indicators": emotional_indicators,
            "emotional_intensity": emotional_intensity,
            "user_id": user_id,
            "channel_id": message.channel.id,
            "familiarity": familiarity,
            "user_history": {
                "familiarity": familiarity,
                "trust": relationship.get("trust", 0.5),
                "affinity": relationship.get("affinity", 0.5),
                "interaction_count": relationship.get("interaction_count", 0),
            },
        }

        return context

    def detect_emotional_indicators(self, content: str) -> dict:
        """Enhanced emotional detection in message content"""
        indicators = {
            "sentiment": 0,
            "intensity": 0,
            "emotions": set(),
            "sentiment_values": [],
        }

        # Expanded emotion detection patterns
        emotion_patterns = {
            "joy": (
                [
                    "happy",
                    "joy",
                    "yay",
                    "wonderful",
                    "😊",
                    "😃",
                    "love",
                    "great",
                    "excellent",
                ],
                1,
            ),
            "sadness": (
                [
                    "sad",
                    "sorry",
                    "miss",
                    "lonely",
                    "😢",
                    "😭",
                    "disappointed",
                    "upset",
                    "hurt",
                ],
                -1,
            ),
            "anger": (
                ["angry", "mad", "hate", "upset", "😠", "😡", "frustrated", "annoyed"],
                -1,
            ),
            "fear": (
                [
                    "scared",
                    "afraid",
                    "worried",
                    "anxiety",
                    "😨",
                    "😰",
                    "nervous",
                    "concerned",
                ],
                -0.7,
            ),
            "love": (["love", "adore", "cherish", "care", "❤️", "🥰", "affection"], 1),
            "surprise": (
                [
                    "wow",
                    "omg",
                    "whoa",
                    "amazing",
                    "😮",
                    "😲",
                    "unbelievable",
                    "incredible",
                ],
                0.5,
            ),
            "gratitude": (["thank", "grateful", "appreciate", "thanks", "🙏"], 0.8),
            "confusion": (
                ["confused", "what?", "don't understand", "🤔", "unclear"],
                -0.3,
            ),
        }

        content_lower = content.lower()

        for emotion, (patterns, sentiment_value) in emotion_patterns.items():
            matches = sum(pattern in content_lower for pattern in patterns)
            if matches > 0:
                indicators["emotions"].add(emotion)
                sentiment_contribution = matches * sentiment_value
                indicators["sentiment"] += sentiment_contribution
                indicators["sentiment_values"].append(sentiment_contribution)
                indicators["intensity"] += matches

        # Detect question patterns for curiosity
        if "?" in content or any(
            q in content_lower for q in ["what", "how", "why", "when", "where", "who"]
        ):
            indicators["emotions"].add("curiosity")
            indicators["intensity"] += 1

        # Detect exclamations for intensity
        if "!" in content:
            exclamation_count = content.count("!")
            indicators["intensity"] += exclamation_count * 0.5

        return indicators

    def personality_to_dict(self) -> dict:
        """Convert AIPersonality model data to dict for conversation manager"""
        if not self.personality:
            return {
                "core_traits": {
                    "openness": 0.85,
                    "conscientiousness": 0.9,
                    "extraversion": 0.75,
                    "agreeableness": 0.85,
                    "stability": 0.8,
                },
                "learned_preferences": {},
                "relationship_dynamics": {},
                "current_mood": "relaxed",
            }

        return {
            "core_traits": self.personality.core_traits,
            "learned_preferences": self.personality.learned_preferences,
            "relationship_dynamics": self.personality.relationship_dynamics,
            "current_mood": self.personality.mood_tracker.get(
                "current_mood", "relaxed"
            ),
            "emotional_memory": (
                self.personality.emotional_memory[-5:]
                if self.personality.emotional_memory
                else []
            ),
        }

    def get_contextual_emote(self, mood: str, context: dict) -> str:
        """Select appropriate emote based on mood and context"""
        if mood not in self.emote_mapping:
            return ""

        available_emotes = self.emote_mapping[mood].copy()
        channel_id = str(context.get("channel_id", ""))

        # Remove recently used emotes for this channel
        if channel_id in self._last_emote:
            recent_emote = self._last_emote[channel_id]
            if recent_emote in available_emotes:
                available_emotes.remove(recent_emote)

        # Default to empty string if no emotes available
        if not available_emotes:
            return ""

        # Select emote based on context
        selected_emote = random.choice(available_emotes)
        self._last_emote[channel_id] = selected_emote

        return selected_emote

    async def adjust_personality_state(self, context: dict):
        """Update AI personality state based on context"""
        if not self.personality:
            self.personality = await AIPersonality.get_default()

        user_id = context.get("user_id")
        if not user_id:
            return

        # Update relationship with small increments for regular interactions
        familiarity_change = 0.01
        trust_change = 0.0
        affinity_change = 0.0

        # Adjust based on emotional context
        emotional_indicators = context.get("emotional_indicators", {})
        sentiment = emotional_indicators.get("sentiment", 0)

        if sentiment > 0:
            # Positive sentiment increases trust and affinity
            trust_change = 0.01
            affinity_change = 0.02
        elif sentiment < 0:
            # Negative sentiment slightly decreases trust and affinity
            trust_change = -0.005
            affinity_change = -0.01

        # Update relationship dynamics in the database
        await self.personality.update_relationship(
            user_id,
            familiarity_change=familiarity_change,
            trust_change=trust_change,
            affinity_change=affinity_change,
        )

        # Learn preferences from interaction
        if "emotions" in emotional_indicators:
            emotion_pref = list(emotional_indicators["emotions"])
            if emotion_pref:
                await self.personality.learn_preference(
                    user_id, "emotional_responses", emotion_pref
                )

    async def select_emotional_response(self, response: str, context: dict) -> str:
        """Select appropriate emotional tone based on context and response"""
        # Get current AI mood from database
        current_mood = (
            self.personality.mood_tracker.get("current_mood", "relaxed")
            if self.personality
            else "relaxed"
        )
        emotions = context.get("emotional_indicators", {}).get("emotions", set())
        time_of_day = context.get("time_of_day", 12)

        # Handle emotional mirroring for strong emotions
        if "joy" in emotions or "love" in emotions:
            return "happy" if time_of_day not in range(21, 5) else "relaxed"
        elif "sadness" in emotions:
            return "caring"
        elif "surprise" in emotions:
            return "curious"
        elif "anger" in emotions:
            return "thoughtful"

        # Default to time-based mood if no strong emotions to respond to
        hour = time_of_day
        if 5 <= hour <= 11:
            return "energetic"
        elif 12 <= hour <= 16:
            return "relaxed"
        elif 17 <= hour <= 20:
            return "thoughtful"
        else:
            return "sleepy"

    @slash_command(name="ai")
    async def ai(self, ctx: Interaction):
        pass

    @ai.subcommand(name="chat", description="Start a private chat thread")
    async def create_chat(self, ctx: Interaction):
        if isinstance(ctx.channel, DMChannel):
            return await ctx.send(embed=Embed.Error("Cannot create threads in DMs"))
        elif not ctx.guild:
            return await ctx.send(
                embed=Embed.Error("Not in a guild!", title="AI Error")
            )
        if not ctx.user:
            return await ctx.send(
                embed=Embed.Error("You are not even user", title="AI Error")
            )

        # Check guild settings
        Logger = Logs.Logger(guild=ctx.guild, user=ctx.user, cog=self, command="ai chat")
        guild_settings = await self.get_guild_settings(ctx.guild.id)

        # Check if threads are allowed
        if not guild_settings.get("allow_threads", True):
            return await ctx.send(
                embed=Embed.Error("Private AI threads are not enabled in this server", title="AI Error")
            )

        # Check role permissions
        if guild_settings.get("allowed_roles"):
            member_roles = []
            if isinstance(ctx.user, Member):
                member_roles = [role.id for role in ctx.user.roles]
            if not any(role_id in guild_settings["allowed_roles"] for role_id in member_roles):
                await Logger.debug(
                    f"User {ctx.user.name} does not have permission to create AI threads",
                    context={
                        "channel": ctx.channel,
                    }
                )
                return await ctx.send(
                    embed=Embed.Error("You don't have permission to create AI threads", title="AI Error")
                )

        # Only allow thread creation in TextChannel
        if not isinstance(ctx.channel, TextChannel):
            return await ctx.send(
                embed=Embed.Error("Threads can only be created in text channels.", title="AI Error")
            )

        thread = await ctx.channel.create_thread(
            name=f"AI Chat with {ctx.user.name}",
            type=ChannelType.private_thread,
        )

        # Update active threads in guild settings
        active_threads = guild_settings.get("active_threads", {})
        active_threads[str(ctx.user.id)] = str(thread.id)
        guild_settings["active_threads"] = active_threads

        guild_feature = await Feature.get_guild_feature(ctx.guild.id, "ai")
        await guild_feature.set_setting("active_threads", active_threads)

        # Create an emotional memory for this new chat
        if self.personality:
            await self.personality.create_emotional_memory(
                ctx.user.id,
                "chat_started",
                f"Started a new private chat with {ctx.user.name}",
                0.6,  # Moderate positive impact
                "excited",
            )

        await ctx.response.send_info(
            f"Created private chat thread {thread.mention}", "AI Created!"
        )
        await thread.send(f"Hello {ctx.user.mention}! How can I help you today?")

    @ai.subcommand(
        name="personality", description="View and manage AI personality settings"
    )
    async def personality_cmd(self, ctx: Interaction):
        if not self.personality:
            return await ctx.send(
                embed=Embed.Error("AI personality not initialized", "Error")
            )
        if not ctx.user:
            return await ctx.send(
                embed=Embed.Error("You are not in a voice channel!", "AI Error")
            )

        traits = self.personality.core_traits
        mood = self.personality.mood_tracker

        # Create personality profile embed
        embed = Embed.Info(
            f"**Current Mood**: {mood.get('current_mood', 'relaxed').title()} (Intensity: {mood.get('intensity', 0.5):.1f})\n\n"
            f"**Core Traits**:\n"
            f"• Openness: {traits.get('openness', 0.85):.2f}\n"
            f"• Conscientiousness: {traits.get('conscientiousness', 0.9):.2f}\n"
            f"• Extraversion: {traits.get('extraversion', 0.75):.2f}\n"
            f"• Agreeableness: {traits.get('agreeableness', 0.85):.2f}\n"
            f"• Stability: {traits.get('stability', 0.8):.2f}\n"
            f"• Empathy: {traits.get('empathy', 0.95):.2f}\n\n"
            f"**Relationship**:\n"
            f"• Familiarity: {self.personality.get_user_relationship(ctx.user.id).get('familiarity', 0.1):.2f}\n"
            f"• Trust: {self.personality.get_user_relationship(ctx.user.id).get('trust', 0.5):.2f}\n"
            f"• Affinity: {self.personality.get_user_relationship(ctx.user.id).get('affinity', 0.5):.2f}",
            title="AI Personality Profile",
        )

        await ctx.send(embed=embed)

    @staticmethod
    def split_response(response_text: str, max_length: int = 4096) -> list[str]:
        return [
            response_text[i : i + max_length]
            for i in range(0, len(response_text), max_length)
        ]
    
    @message_command(
        "Summarize",
        integration_types=[
            IntegrationType.user_install,
        ],
        contexts=[
            InteractionContextType.guild,
            InteractionContextType.bot_dm,
            InteractionContextType.private_channel,
        ],
    )
    async def summarize(self, ctx: Interaction, target: Message):
        await ctx.response.defer(ephemeral=True)
        message = target.content
        prompt = f"Please provide a concise summary of the following text:\n\n{message}"
        response = await generate(prompt, "llama3.2")
        if len(response) > 4096:
            split_texts = self.split_response(response)
            return await ctx.send(
                embeds=[Embed.Info(text, title="Summary") for text in split_texts]
            )
        await ctx.send(embed=Embed.Info(response, title="Summary"))

    @slash_command(
        "ask",
        "ask Gemini/Llama3.2 AI.",
        integration_types=[
            IntegrationType.user_install,
        ],
        contexts=[
            InteractionContextType.guild,
            InteractionContextType.bot_dm,
            InteractionContextType.private_channel,
        ],
    )
    async def ask(self, ctx: Interaction, message: str, ephemeral: bool = True):
        await ctx.response.defer(ephemeral=ephemeral)
        response = await generate(message, "llama3.2")
        if len(response) > 4096:
            split_texts = self.split_response(response)
            return await ctx.send(
                embeds=[Embed.Info(text, title="") for text in split_texts],
                ephemeral=ephemeral,
            )
        await ctx.send(embed=Embed.Info(response, title=""), ephemeral=ephemeral)
    
    @slash_command(
        "test",
        "Test command for AI.",
        integration_types=[
            IntegrationType.user_install,
        ],
        contexts=[
            InteractionContextType.guild,
            InteractionContextType.bot_dm,
            InteractionContextType.private_channel,
        ],
    )
    async def test(self, ctx: Interaction):
        print(0 / 0)
    
    #error handler
    async def cog_application_command_error(self, ctx: Interaction, error: ApplicationError):
        command_name = ctx.application_command.qualified_name if ctx.application_command else "Unknown Command"
        Logger = Logs.Logger(guild=ctx.guild, user=ctx.user, cog=self, command=command_name)
        await Logger.error(
            f"Error occurred in AI commands: {error}",
            context={
                "guild": ctx.guild.name if ctx.guild else "non-guild",
                "user": ctx.user.name if ctx.user else "bot",
                "channel": ctx.channel.name if ctx.channel and not isinstance(ctx.channel, PartialMessageable) else "DM",
            },
        )

def setup(client):
    client.add_cog(AI(client))
