import nextcord
from nextcord import *
from nextcord.ext import commands
import speech_recognition as sr
from gtts import gTTS
import tempfile
import asyncio
import os
import wave
import pyaudio
from pydub import AudioSegment
from modules.Nexon.Negomi import ConversationManager
from modules.Nexon import *

class VoiceAI(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.voice_clients:Dict[int, VoiceClient] = {}
        self.recognizer = sr.Recognizer()
        self.is_listening:Dict[int, bool] = {}
        self.audio_queue:Dict[int, asyncio.Queue] = {}
        self.conversation_manager = ConversationManager()
        
    def setup_audio_queue(self, guild_id):
        if guild_id not in self.audio_queue:
            self.audio_queue[guild_id] = asyncio.Queue()

    async def text_to_speech(self, text, lang='en'):
        """Convert text to speech using gTTS"""
        tts = gTTS(text=text, lang=lang)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp

    async def play_audio(self, voice_client, audio_data):
        """Play audio in voice channel"""
        if voice_client.is_playing():
            voice_client.stop()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
            tmp_file.write(audio_data.getvalue())
            tmp_file_path = tmp_file.name

        try:
            audio_source = nextcord.FFmpegPCMAudio(tmp_file_path)
            voice_client.play(audio_source)
            while voice_client.is_playing():
                await asyncio.sleep(1)
        finally:
            os.unlink(tmp_file_path)

    async def process_voice(self, guild_id, voice_client, user_id, username):
        """Process incoming voice data"""
        while self.is_listening.get(guild_id, False):
            try:
                # Record audio
                frames = []
                silence_threshold = 1000
                silence_duration = 0
                max_silence = 1

                stream = pyaudio.PyAudio().open(
                    format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,
                    input=True,
                    frames_per_buffer=1024
                )

                while silence_duration < max_silence:
                    data = stream.read(1024)
                    frames.append(data)
                    
                    audio_data = AudioSegment(
                        data=data,
                        sample_width=2,
                        frame_rate=16000,
                        channels=1
                    )
                    if audio_data.dBFS < silence_threshold:
                        silence_duration += 0.064
                    else:
                        silence_duration = 0

                stream.stop_stream()
                stream.close()

                # Save recorded audio
                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                    with wave.open(tmp_file.name, 'wb') as wf:
                        wf.setnchannels(1)
                        wf.setsampwidth(2)
                        wf.setframerate(16000)
                        wf.writeframes(b''.join(frames))
                    
                    # Convert speech to text
                    with sr.AudioFile(tmp_file.name) as source:
                        audio = self.recognizer.record(source)
                        text = self.recognizer.recognize_google(audio)

                    # Use your existing conversation manager
                    response = self.conversation_manager.get_response(
                        user_id,
                        f"{username}: {text}",
                        text
                    )

                    if response and response is not False:
                        # Convert response to speech
                        audio_data = await self.text_to_speech(response)
                        await self.audio_queue[guild_id].put(audio_data)

                os.unlink(tmp_file.name)

            except sr.UnknownValueError:
                continue
            except Exception as e:
                print(f"Error processing voice: {e}")
                continue

    async def voice_response_handler(self, guild_id, voice_client):
        """Handle playing voice responses"""
        while self.is_listening.get(guild_id, False):
            try:
                audio_data = await self.audio_queue[guild_id].get()
                await self.play_audio(voice_client, audio_data)
            except Exception as e:
                print(f"Error playing response: {e}")
                continue
    
    @slash_command(name="ai")
    async def AI(self,ctx:Interaction):
        pass
    
    
    @AI.subcommand("join")
    async def joinvoice(self, ctx:Interaction):
        """Join a voice channel and start listening"""
        if not ctx.user.voice:
            await ctx.send("You need to be in a voice channel!")
            return

        channel = ctx.user.voice.channel
        guild_id = ctx.guild.id

        if guild_id not in self.voice_clients:
            voice_client = await channel.connect()
            self.voice_clients[guild_id] = voice_client
            self.setup_audio_queue(guild_id)
            self.is_listening[guild_id] = True

            # Start voice processing and response handling with user info
            asyncio.create_task(self.process_voice(
                guild_id, 
                voice_client,
                str(ctx.user.id),
                get_name(ctx.user)
            ))
            asyncio.create_task(self.voice_response_handler(guild_id, voice_client))
            
            await ctx.send("Joined voice channel and listening!")
        else:
            await ctx.send("I'm already in a voice channel!")

    @AI.subcommand("leave")
    async def leavevoice(self, ctx:Interaction):
        """Leave the voice channel and stop listening"""
        guild_id = ctx.guild.id
        if guild_id in self.voice_clients:
            self.is_listening[guild_id] = False
            await self.voice_clients[guild_id].disconnect()
            del self.voice_clients[guild_id]
            await ctx.send("Left voice channel!")
        else:
            await ctx.send(embed=warn_embed("I'm not in a voice channel"))

def setup(client):
    client.add_cog(VoiceAI(client))