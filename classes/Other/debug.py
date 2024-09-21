import platform
import psutil
import nextcord
from nextcord import slash_command, Message, Member, Embed
from Lib.Side import *
from nextcord.ext import commands, application_checks as check
import time

class Debug(commands.Cog):
    def __init__(self, client:commands.Bot):
        self.client = client
        self.start_time = time.time()
        self.message_count = 0  # Track the number of messages the client has sent

        # Track sent messages by listening to the on_message event

    @commands.Cog.listener()
    async def on_message(self,message:Message):
        if message.author == self.client.user:
            self.message_count += 1
        # await self.client.process_commands(message)
    
    def debugEmbed(self, user: Member):
        embed = Embed(title="🔧 Bot Debug Information", color=Debug_Color)
        
        # Uptime
        uptime = time.time() - self.start_time
        days, remainder = divmod(uptime, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        embed.add_field(name="⏰ Uptime", value=f"**{int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s**", inline=False)

        # Memory Usage
        process = psutil.Process()
        mem_info = process.memory_info()
        embed.add_field(name="🧠 Memory Usage", value=f"**{mem_info.rss / 1024 ** 2:.2f} MB**", inline=True)

        # CPU Usage
        cpu_percent = psutil.cpu_percent(interval=1)
        embed.add_field(name="💻 CPU Usage", value=f"**{cpu_percent}%**", inline=True)

        # API & WebSocket Latency
        api_latency = self.client.latency * 1000  # Convert to ms
        embed.add_field(name="📡 Latency", value=f"API: **{api_latency:.2f} ms**", inline=False)

        # Number of Servers and Members
        total_guilds = len(self.client.guilds)
        total_members = sum(guild.member_count for guild in self.client.guilds)
        embed.add_field(name="🏠 Servers", value=f"**{total_guilds}**", inline=True)
        embed.add_field(name="👥 Total Members", value=f"**{total_members}**", inline=True)

        # Loaded Classes
        loaded_Classes = ", ".join(self.client.cogs.keys())
        embed.add_field(name="⚙️ Loaded Classes", value=f"**`{loaded_Classes if loaded_Classes else 'None'}`**", inline=False)

        # Python Version
        python_version = platform.python_version()
        embed.add_field(name="🐍 Python Version", value=f"**{python_version}**", inline=True)

        # Nextcord Version
        nextcord_version = nextcord.__version__
        embed.add_field(name="🛠 Nextcord Version", value=f"**{nextcord_version}**", inline=True)

        # System Info
        system_info = platform.uname()
        embed.add_field(name="🖥 System Info", value=f"**{system_info.system} {system_info.release}**", inline=False)

        # Messages Sent
        embed.add_field(name="✉️ Messages Sent", value=f"**{self.message_count}**", inline=False)

        # Footer with client Name
        embed.set_footer(text=f"Requested by {get_name(user)} ({user})", icon_url=user.avatar.url)
        return embed
    
    @slash_command(name="debug",description="Displays detailed debug information about the bot.")
    async def debugSlash(self,ctx:init):
        await ctx.send(embed=self.debugEmbed(ctx.user),ephemeral=True)

def setup(client):
    client.add_cog(Debug(client))