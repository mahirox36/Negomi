import platform
import psutil
from modules.Nexon import *
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
    
    def debugEmbed(self, user: Member | User) -> Embed:
        embed = Embed(title="🔧 System Diagnostics", color=int(colors.Debug.value))
        
        # System Status
        uptime = time.time() - self.start_time
        days, remainder = divmod(uptime, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        process = psutil.Process()
        mem_info = process.memory_info()
        cpu_percent = psutil.cpu_percent(interval=1)
        
        status = (
            f"🟢 **Uptime:** {int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s\n"
            f"🔄 **CPU:** {cpu_percent}% | 💾 **RAM:** {mem_info.rss / 1024 ** 2:.1f}MB\n"
            f"📡 **Latency:** {(self.client.latency * 1000):.1f}ms"
        )
        embed.add_field(name="System Status", value=status, inline=False)

        # Bot Statistics
        total_guilds = len(self.client.guilds)
        total_members = sum(guild.member_count or 0 for guild in self.client.guilds)
        avg_members = total_members / total_guilds if total_guilds else 0
        
        stats = (
            f"🏠 **Servers:** {total_guilds:,}\n"
            f"👥 **Total Members:** {total_members:,}\n"
            f"📊 **Avg Members/Server:** {avg_members:.1f}\n"
            f"✉️ **Messages Handled:** {self.message_count:,}"
        )
        embed.add_field(name="Bot Statistics", value=stats, inline=False)

        # Technical Details
        tech = (
            f"🐍 **Python:** {platform.python_version()}\n"
            f"🛠️ **Nexon:** {nexon_version}\n"
            f"💻 **OS:** {platform.system()} {platform.release()}\n"
            f"🔌 **Architecture:** {platform.machine()}"
        )
        embed.add_field(name="Technical Details", value=tech, inline=False)

        # Active Modules
        modules = ", ".join(f"`{cog}`" for cog in sorted(self.client.cogs.keys()))
        embed.add_field(name="Active Modules", value=modules or "None", inline=False)

        # Set timestamp and footer
        embed.timestamp = utils.utcnow()
        embed.set_footer(
            text=f"Requested by {user.display_name}",
            icon_url=user.avatar.url if user.avatar else None
        )
        
        return embed
    
    @slash_command(name="debug",description="Displays detailed debug information about the bot.")
    async def debugSlash(self,ctx:init):
        if not ctx.user:
            return await ctx.send("This command can only by a user",ephemeral=True)
        await ctx.send(embed=self.debugEmbed(ctx.user),ephemeral=True)

def setup(client):
    client.add_cog(Debug(client))