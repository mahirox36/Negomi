import aiohttp
from modules.Nexon import *
import json
from cryptography.fernet import Fernet
import base64
import os
import uuid
__version__ = 2.4
__VersionsSupported__ = [2.2, 2.3, 2.4]


class ChannelTypeError(Exception):
    def __init__(self, channel_name: str, support: bool, *args):
        self.channel = channel_name
        self.support = support
        super().__init__(*args)

class ChannelCreationError(Exception):
    def __init__(self, channel_name: str, error_message: str, *args):
        self.channel = channel_name
        self.message = f"Failed to create channel: {error_message}"
        super().__init__(*args)

class Backup(commands.Cog):
    def __init__(self, client: Client):
        self.client = client
        self.key = os.getenv('BACKUP_KEY', Fernet.generate_key())
        # Generate key based on MAC address
        def get_mac_based_key():
            mac = uuid.getnode()
            mac_bytes = mac.to_bytes(6, 'big')
            # Extend to 32 bytes for Fernet key
            extended = mac_bytes * 6  # 36 bytes
            return base64.urlsafe_b64encode(extended[:32])

        self.key = get_mac_based_key()
        self.cipher = Fernet(self.key)

    
    @slash_command(name="backup", 
                  default_member_permissions=Permissions(administrator=True))
    async def backup(self, ctx:init):
        pass
    
    
    @backup.subcommand(name="export", description="Export server configuration including roles, categories, and channels")
    @feature()
    @cooldown(15)
    async def export(self, ctx: init, encrypt: bool = False, include_assets: bool = False, creator_only: bool = False):
        await ctx.response.defer(ephemeral=False)
        await self.exportFunction(ctx, encrypt, include_assets, creator_only)

    async def exportFunction(self, ctx: init, encrypt: bool = False, include_assets: bool = False, creator_only: bool = False):
        data = {
            "Info": {
                "version": __version__,
                "isCommunityServer": "COMMUNITY" in ctx.guild.features,
                "features": ctx.guild.features,
                "creator_id": ctx.user.id if creator_only else None,
                "encrypted": encrypt
            },
            "Categories": [],
            "roles": [],
            "bot_name": []
        }

        if include_assets:
            data["Assets"] = {
                "icon_url": str(ctx.guild.icon.url) if ctx.guild.icon else None,
                "banner_url": str(ctx.guild.banner.url) if ctx.guild.banner else None,
                "splash_url": str(ctx.guild.splash.url) if ctx.guild.splash else None
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
                data["bot_name"].append(f"<@{member.id}> - {member.display_name}")

        # Create and send the file
        file_data = io.StringIO()
        try:
            json_data = json.dumps(data, indent=2, ensure_ascii=False)
            if encrypt:
                encrypted_data = self.cipher.encrypt(json_data.encode())
                file_data.write(base64.b64encode(encrypted_data).decode())
                ext = ".negomi"
            else:
                file_data.write(json_data)
                ext = ".json"
            
            file_data.seek(0)
            filename = f"backup-v{__version__}-{ctx.guild.name}-{ctx.created_at.strftime('%Y-%m-%d_%H-%M-%S')}{ext}"
            discord_file = File(file_data, filename=filename)
            await ctx.send(file=discord_file)
        finally:
            file_data.close()

    async def create_channel_data(self, channel):
        base_data = {
            "Name": channel.name,
            "Permission": await self.get_all_permission_overwrites(channel),
            "PermissionSynced": channel.permissions_synced,
        }

        if isinstance(channel, TextChannel):
            return {
                **base_data,
                "isAgeRestricted": channel.is_nsfw(),
                "isAnnouncement": channel.is_news(),
                "slowModeDuration": channel.slowmode_delay,
                "channelTopic": channel.topic or "",
                "type": "text",
                "defaultThreadSlowmode": channel.default_thread_slowmode_delay,
                "defaultAutoArchiveDuration": channel.default_auto_archive_duration
            }
        elif isinstance(channel, VoiceChannel):
            return {
                **base_data,
                "userLimit": channel.user_limit,
                "bitrate": channel.bitrate,
                "rtcRegion": channel.rtc_region,
                "videoQualityMode": channel.video_quality_mode,
                "type": "voice"
            }
        elif isinstance(channel, ForumChannel):
            channel.slowmode_delay
            return {
                **base_data,
                "type": "forum",
                "isAgeRestricted": channel.is_nsfw(),
                "guidelines": channel.topic or "",
                "defaultSlowMode": channel.default_thread_slowmode_delay,
                "SlowMode": channel.slowmode_delay,
                "defaultReactionEmoji": str(channel.default_reaction) if channel.default_reaction else None,
                "defaultLayout": channel.default_forum_layout.value if channel.default_forum_layout else 0,
                "defaultSortOrder": channel.default_sort_order.value if channel.default_sort_order else 0,
                "availableTags": [
                    {
                        "name": tag.name,
                        "moderated": tag.moderated,
                        "emoji": str(tag.emoji) if tag.emoji else None,
                    }
                    for tag in channel.available_tags
                ]
            }
        elif isinstance(channel, StageChannel):
            return {
                **base_data,
                "userLimit": channel.user_limit,
                "channelTopic": channel.topic or "",
                "nsfw": channel.is_nsfw(),
                "type": "stage"
            }
        return None

    async def get_all_permission_overwrites(self, channel):
        overwrites_data = {}
        for target, overwrite in channel.overwrites.items():
            key = f"role:{target.id}" if isinstance(target, Role) else f"member:{target.id}"
            overwrites_data[key] = {
                "allow": overwrite.pair()[0].value,
                "deny": overwrite.pair()[1].value,
                "name": target.name
            }
        return overwrites_data

    @backup.subcommand(name="import",
                  description="Import server configuration from a backup file")
    @feature()
    async def imported(self, ctx: init, file: Attachment):
        if ctx.guild.owner_id != ctx.user.id:
            await ctx.send(embed=error_embed("Only the owner of the guild can import.", "Import Error"))
            return

        if not (file.filename.endswith(".json") or file.filename.endswith(".negomi")):
            await ctx.send(embed=error_embed("Invalid file type. Please upload a .json or .negomi file.", "Error"))
            return

        file_content = await file.read()
        try:
            content_str = file_content.decode()
            try:
                # Try to decode as base64 and decrypt
                encrypted_data = base64.b64decode(content_str)
                decrypted_data = self.cipher.decrypt(encrypted_data)
                data = json.loads(decrypted_data)
            except:
                # If decryption fails, try parsing as plain JSON
                data = json.loads(content_str)
        except Exception as e:
            await ctx.send(embed=error_embed(f"Failed to parse backup file: {str(e)}", "Parse Error"))
            return

        # Check creator restriction
        if data["Info"].get("creator_id") and data["Info"]["creator_id"] != ctx.user.id:
            await ctx.send(embed=error_embed("This backup can only be imported by its creator.", "Permission Error"))
            return

        created_roles = {}
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
                except ChannelCreationError as e:
                    await ctx.channel.send(
                        embed=error_embed(e.message))
        
        # Import server assets if included
        if "Assets" in data and data["Assets"]:
            try:
                if data["Assets"]["icon_url"]:
                    icon_data = await self.download_asset(data["Assets"]["icon_url"])
                    await ctx.guild.edit(icon=icon_data)
                if data["Assets"]["banner_url"]:
                    banner_data = await self.download_asset(data["Assets"]["banner_url"])
                    await ctx.guild.edit(banner=banner_data)
                if data["Assets"]["splash_url"]:
                    splash_data = await self.download_asset(data["Assets"]["splash_url"])
                    await ctx.guild.edit(splash=splash_data)
            except Exception as e:
                await ctx.send(embed=warn_embed(f"Failed to import some server assets: {str(e)}"))

        bot_names = "Bots Names:\n" + "\n".join(data["bot_name"])
        await ctx.channel.send(bot_names)
        await ctx.send(embed=info_embed("Import completed successfully!", "Import Complete"))

    async def create_channel(self, guild: Guild, channel_data: dict, category, community: bool):
        channel_type = channel_data.get("type", None)
        overwrites = await self.build_permission_overwrites(guild, channel_data["Permission"])
        
        base_kwargs = {
            "name": channel_data["Name"],
            "reason": "Importing from file",
            "category": category,
            "overwrites": overwrites
        }

        try:
            # Check community-required channels first
            if not community and channel_type in ["forum", "stage"]:
                raise ChannelTypeError(channel_data.get("Name"), True)

            if channel_type == "text":
                return await guild.create_text_channel(
                    **base_kwargs,
                    slowmode_delay=channel_data.get("slowModeDuration", 0),
                    nsfw=channel_data.get("isAgeRestricted", False),
                    topic=channel_data.get("channelTopic", "")
                )
            elif channel_type == "voice":
                rtc_region= VoiceRegion(channel_data.get("rtcRegion")) if channel_data.get("rtcRegion", None) is not None else None
                return await guild.create_voice_channel(
                    **base_kwargs,
                    user_limit=channel_data.get("userLimit", 0),
                    bitrate=channel_data.get("bitrate", 64000),
                    rtc_region=rtc_region,
                    video_quality_mode=VideoQualityMode(channel_data.get("videoQualityMode", 1))
                )
            elif channel_type == "forum":
                tags = []
                for tag_data in channel_data.get("availableTags", []):
                    tags.append(ForumTag(
                        name=tag_data["name"],
                        moderated=tag_data["moderated"],
                        emoji=tag_data["emoji"] if tag_data["emoji"] else None
                    ))
                
                channel = await guild.create_forum_channel(
                    **base_kwargs,
                    topic=channel_data.get("guidelines", ""),
                    default_thread_slowmode_delay=channel_data.get("defaultSlowMode", 0),
                    available_tags=tags,
                    default_reaction=channel_data.get("defaultReactionEmoji", None),
                    default_forum_layout=ForumLayoutType(channel_data.get("defaultLayout", 0)),
                    default_sort_order=SortOrderType(channel_data.get("defaultSortOrder", 0))
                )
                await channel.edit(nsfw=channel_data.get("isAgeRestricted", False), slowmode_delay=channel_data.get("slowmode_delay", False))
                return channel
            elif channel_type == "stage":
                return await guild.create_stage_channel(
                    **base_kwargs,
                    user_limit=channel_data.get("userLimit", 0),
                    topic=channel_data.get("channelTopic", ""),
                    nsfw=channel_data.get("nsfw", False)
                )
            else:
                raise ChannelTypeError(channel_data.get("Name"), False)

        except Exception as e:
            raise ChannelCreationError(channel_data["Name"], str(e))

    async def build_permission_overwrites(self, guild: Guild, permission_data: dict):
        overwrites = {}
        for key, data in permission_data.items():
            target_type, target_id = key.split(":")
            target = None
            
            if target_type == "role":
                target = guild.get_role(int(target_id))
                if not target:
                    # Try to find role by name
                    target = utils.get(guild.roles, name=data["name"])
            else:  # member
                target = guild.get_member(int(target_id))

            if target:
                overwrites[target] = PermissionOverwrite.from_pair(
                    allow=Permissions(data["allow"]),
                    deny=Permissions(data["deny"])
                )
        
        return overwrites

    async def download_asset(self, url: str) -> bytes:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.read()
                raise Exception(f"Failed to download asset: {response.status}")

def setup(client):
    client.add_cog(Backup(client))