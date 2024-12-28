"""
Backup.py is for Backing up your server as a File"""
from modules.Nexon import *
import json
__version__ = 1.4
__VersionsSupported__= [1.4]

class Backup(commands.Cog):
    def __init__(self, client:Client):
        self.client = client
    @slash_command(name="export", description="this will export Roles, Channels, and Bots Names", default_member_permissions=Permissions(administrator=True))
    @feature()
    @cooldown(10)
    async def export(self, ctx: init):
        await ctx.response.defer()
        
        data: Dict[str, Union[
            str,  # Version string
            Dict[str, Dict[int, str]],  # Server structure with categories, channels, voice mappings
            Dict[str, List[Union[List[Union[str, int, None]], Dict[str, int]]]],  # Channel details
            List[Dict[str, Union[str, int]]]  # Role details
        ]] = {
            "version": __version__,
            "Categories": {}, # {category_id: category_name}
            "channels": {
                "Channels": [],  # [[channel_name, category_id, topic_or_None]]
                "Voice": []  # [[voice_channel_name, category_id]]
            },
            "roles": [],  # [[role_name, role_color, role_permissions]]
            "bot_name": []  # List of bot display names
        }
    
        # Add categories
        for category in ctx.guild.categories:
            data["Categories"][category.id] = category.name
    
        # Add text channels
        for category in ctx.guild.categories:
            for channel in category.text_channels:
                data["channels"]["Channels"].append([
                    channel.name, category.id, channel.topic or None
                ])
    
        # Add voice channels
        for category in ctx.guild.categories:
            for channel in category.voice_channels:
                data["channels"]["Voice"].append([channel.name, category.id])
    
        # Add roles in server order (reversed to match Discord's hierarchy)
        for role in ctx.guild.roles:
            data["roles"].append([role.name, role.color.value, role.permissions.value])
        data["roles"].reverse()
    
        # Add bot display names
        for member in ctx.guild.members:
            if member.bot:
                data["bot_name"].append(member.mention)
    
        # Create a temporary file-like object for JSON export
        file_data = io.StringIO()
        try:
            json.dump(data, file_data, indent=2, ensure_ascii=False)
            file_data.seek(0)
            filename = f"backup-{ctx.guild.name}-{ctx.created_at.strftime('%Y-%m-%d_%H-%M-%S')}.json"
            discord_file = File(file_data, filename=filename)
            await ctx.send(file=discord_file)
        finally:
            file_data.close()

    @slash_command(name="import",
                   description="This will import Roles, Channels, and Bots Names. You need to upload the file you made with export",
                   default_member_permissions=Permissions(administrator=True))
    @feature()
    async def imported(self,ctx:init, file: Attachment):
        if ctx.guild.owner_id != ctx.user.id:
            ctx.send(embed=error_embed("Only the owner of the guild can import.","Import Error"))
            return
        if not file.filename.endswith(".json"):
            await ctx.send(embed=error_embed("Invalid file type. Please upload a `.json` file that the command `/export` made", "Error"))
            return
        file = await file.read()
        data: Dict[str, Union[
            str,  # Version string
            Dict[str, Dict[int, str]],  # Server structure with categories, channels, voice mappings
            Dict[str, List[Union[List[Union[str, int, None]], Dict[str, int]]]],  # Channel details
            List[Dict[str, Union[str, int]]]  # Role details
        ]] = json.loads(file)

        # Check version compatibility
        if data.get("version") == __version__:
            await ctx.send(embed=info_embed("It will take some time to import everything.", "Okie UwU"))
        elif data.get("version") in __VersionsSupported__:
            await ctx.send(embed=warn_embed(
                "This version is outdated but still supported. Please create a new backup to update it.",
                title="⚠️ The Backup Version is Outdated ⚠️"
            ))
        else:
            await ctx.send(embed=error_embed(
                "Sorry, but this version of the backup is not supported.",
                title="⚠️ The Backup Version is Not Supported ⚠️"
            ))
            return

        # Create categories
        categories = {}
        for id, name in data["Categories"].items():
            category = await ctx.guild.create_category(name)
            categories[int(id)] = category

        # Create text channels
        for channel in data["channels"]["Channels"]:
            channel_name, category_id, topic = channel
            category = categories.get(category_id)
            await ctx.guild.create_text_channel(channel_name, category=category, topic=topic)

        # Create voice channels
        for channel in data["channels"]["Voice"]:
            channel_name, category_id = channel
            category = categories.get(category_id)
            await ctx.guild.create_voice_channel(channel_name, category=category)

        # Create roles
        for role in data["roles"]:
            role_name, color, permissions = role
            if role_name == "@everyone":
                await ctx.guild.default_role.edit(permissions=Permissions(permissions))
            else:
                await ctx.guild.create_role(
                    name=role_name,
                    color=Colour(color),
                    permissions=Permissions(permissions)
                )

        # Create a channel for more info
        final_channel = await ctx.guild.create_text_channel("more-info")
        bot_names = "Bots Names:\n" + "\n".join(data["bot_name"])
        await final_channel.send(bot_names)
        await final_channel.send("Finished everything.")

def setup(client):
    client.add_cog(Backup(client))