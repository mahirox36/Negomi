from modules.Nexon import *
import json
__version__ = 2.2
__VersionsSupported__ = [2.2]

#TODO: Add Protected File Type
#TODO: Add if it should Include the Server Icon and banner (Only with the protected file type)
#TODO: Add roles permission support for channels
#TODO: make it that it also import the Rules channel

class ChannelTypeError(Exception):
    def __init__(self, channel_name: str, support: bool, *args):
        self.channel = channel_name
        self.support = support
        super().__init__(*args)
class Backup(commands.Cog):
    def __init__(self, client: Client):
        self.client = client

    
    @slash_command(name="backup", 
                  default_member_permissions=Permissions(administrator=True))
    async def backup(self, ctx:init):
        pass
    
    
    @backup.subcommand(name="export", description="Export server configuration including roles, categories, and channels")
    @feature()
    @cooldown(10)
    async def export(self, ctx: init):
        await ctx.response.defer(ephemeral=False)
        await self.exportFunction(ctx)

    async def exportFunction(self, ctx: init):
        data = {
            "Info": {
                "version": __version__,
                "isCommunityServer": "COMMUNITY" in ctx.guild.features,
                "features": ctx.guild.features
                },
            "Categories": [],
            "roles": [],
            "bot_name": []
        }

        # Export roles first
        for role in reversed(ctx.guild.roles):
            role_data = {
                "Name": role.name,
                "Color": f"{role.color.value:06x}",  # Convert to hex
                "Permission": role.permissions.value
            }
            data["roles"].append(role_data)

        # Handle channels with no category
        no_category_channels = []
        for channel in ctx.guild.channels:
            if channel.category is None:
                channel_data = await self.create_channel_data(channel)
                if channel_data:
                    no_category_channels.append(channel_data)

        if no_category_channels:
            data["Categories"].append({
                "channelsContains": no_category_channels
            })

        # Export categories with their channels
        for category in ctx.guild.categories:
            category_data = {
                "Name": category.name,
                "Permission": channel.permissions_for(channel.guild.default_role).value,
                "PermissionSynced": channel.permissions_synced,
                "channelsContains": []
            }

            for channel in category.channels:
                channel_data = await self.create_channel_data(channel)
                if channel_data:
                    category_data["channelsContains"].append(channel_data)

            data["Categories"].append(category_data)

        # Export bot names
        for member in ctx.guild.members:
            if member.bot:
                data["bot_name"].append(f"<@{member.id}> - {get_name(member)}")

        # Create and send the file
        file_data = io.StringIO()
        try:
            json.dump(data, file_data, indent=2, ensure_ascii=False)
            file_data.seek(0)
            filename = f"backup-v2-{ctx.guild.name}-{ctx.created_at.strftime('%Y-%m-%d_%H-%M-%S')}.json"
            discord_file = File(file_data, filename=filename)
            await ctx.send(file=discord_file)
        finally:
            file_data.close()

    async def create_channel_data(self, channel):
        if isinstance(channel, TextChannel):
            overwrites = channel.overwrites_for(channel.guild.default_role)
            permissions_dict = {
                "allow": overwrites.pair()[0].value,
                "deny": overwrites.pair()[1].value
            }
            return {
                "Name": channel.name,
                "Permission": permissions_dict,
                "PermissionSynced": channel.permissions_synced,
                "isAgeRestricted": channel.is_nsfw(),
                "isAnnouncement": channel.is_news(),
                "slowModeDuration": channel.slowmode_delay,
                "channelTopic": channel.topic or "",
                "type": "text"
            }
        elif isinstance(channel, VoiceChannel):
            overwrites = channel.overwrites_for(channel.guild.default_role)
            permissions_dict = {
                "allow": overwrites.pair()[0].value,
                "deny": overwrites.pair()[1].value
            }
            return {
                "Name": channel.name,
                "Permission": permissions_dict,
                "PermissionSynced": channel.permissions_synced,
                "userLimit": channel.user_limit,
                "type": "voice"
            }
        elif isinstance(channel, StageChannel):
            overwrites = channel.overwrites_for(channel.guild.default_role)
            permissions_dict = {
                "allow": overwrites.pair()[0].value,
                "deny": overwrites.pair()[1].value
            }
            return {
                "Name": channel.name,
                "Permission": permissions_dict,
                "PermissionSynced": channel.permissions_synced,
                "userLimit": channel.user_limit,
                "channelTopic": channel.topic or "",
                "nsfw": channel.is_nsfw(),
                "type": "stage"
            }
        return None

    @backup.subcommand(name="import",
                  description="Import server configuration from a backup file")
    @feature()
    async def imported(self, ctx: init, file: Attachment):
        if ctx.guild.owner_id != ctx.user.id:
            await ctx.send(embed=error_embed("Only the owner of the guild can import.", "Import Error"))
            return

        if not file.filename.endswith(".json"):
            await ctx.send(embed=error_embed("Invalid file type. Please upload a `.json` file.", "Error"))
            return

        created_roles = {}
        file_content = await file.read()
        data = json.loads(file_content)

        if data["Info"].get("version") not in __VersionsSupported__:
            await ctx.send(embed=error_embed("Unsupported backup version.", "Version Error"))
            return

        await ctx.send(embed=info_embed("Starting import process...", "Import Started"))

        # Create roles first
        for role_data in data["roles"]:
            if role_data["Name"] != "@everyone":
                role = await ctx.guild.create_role(
                    reason= "Importing from file",
                    name=role_data["Name"],
                    color=Colour(int(role_data["Color"], 16)),
                    permissions=Permissions(role_data["Permission"])
                )
                created_roles[role_data["Name"]] = role
            else:
                await ctx.guild.default_role.edit(
                    reason= "Importing from file",
                    permissions=Permissions(role_data["Permission"])
                )

        # Create categories and channels
        for category_data in data["Categories"]:
            if "Name" in category_data:  # If it's a named category
                category = await ctx.guild.create_category(
                    name=category_data["Name"],
                    overwrites={ctx.guild.default_role: PermissionOverwrite.from_pair(allow=Permissions(category_data["Permission"]), deny=Permissions.none())},
                    reason= "Importing from file"
                )
                parent = category
            else:  # For channels without category
                parent = None

            for channel_data in category_data["channelsContains"]:
                try:
                    await self.create_channel(ctx.guild, channel_data, parent, "COMMUNITY" in ctx.guild.features)
                except ChannelTypeError as e:
                    if e.support: await ctx.channel.send(
                        embed=warn_embed(f"Channel with the name `{e.channel}` cannot be imported due the channel type, you have to turn Community in your server"))
                    else: await ctx.channel.send(
                        embed=warn_embed(f"Channel with the name `{e.channel}` isn't supported yet"))
        bot_names = "Bots Names:\n" + "\n".join(data["bot_name"])
        await ctx.channel.send(bot_names)
        await ctx.send(embed=info_embed("Import completed successfully!", "Import Complete"))

    async def create_channel(self, guild: Guild, channel_data: dict, category, community: bool):
        channel_type = channel_data.get("type", None)
        allow_permissions = Permissions(channel_data["Permission"]["allow"])
        deny_permissions = Permissions(channel_data["Permission"]["deny"])
        overwrite = {guild.default_role: PermissionOverwrite.from_pair(allow=allow_permissions, deny=deny_permissions)} if not channel_data["PermissionSynced"] else {}
        if channel_type == "text":
            await guild.create_text_channel(
                name=channel_data.get("Name"),
                reason= "Importing from file",
                category=category,
                overwrites= overwrite,
                slowmode_delay= channel_data.get("slowModeDuration", 0),
                nsfw=channel_data.get("isAgeRestricted", False),
                topic=channel_data.get("channelTopic", ""))
        elif channel_type == "voice":
            await guild.create_voice_channel(
                name= channel_data.get("Name"),
                reason= "Importing from file",
                category=category,
                user_limit=channel_data.get("userLimit", 0),
                overwrites=overwrite)
        elif community: 
            if channel_type == "stage":
                await guild.create_stage_channel(
                name= channel_data.get("Name"),
                reason= "Importing from file",
                category=category,
                user_limit=channel_data.get("userLimit", 0),
                topic=channel_data.get("channelTopic", ""),
                nsfw=channel_data.get("nsfw", False),
                overwrites=overwrite)
            else: 
                raise ChannelTypeError(channel_data.get("Name"), False)
        else:
            if channel_type in ["stage", "forum"]:
                raise ChannelTypeError(channel_data.get("Name"), True)
            else:
                raise ChannelTypeError(channel_data.get("Name"), False)
                

def setup(client):
    client.add_cog(Backup(client))