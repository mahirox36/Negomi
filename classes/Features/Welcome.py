import requests
from modules.Nexon import *
from PIL import Image, ImageDraw, ImageFont
import gc
"""
Setup a welcome message in a specific Channel, in the message option you can uses these for info (Variables):
{server}  : For the name of the server
{count}   : For the count of members in the server
{mention} : Mention the user
{name}    : Just the name of the user
"""

@dataclass
class WelcomeConfig:
    message: str
    channel_id: int

class Welcome(commands.Cog):
    def __init__(self, client:Client):
        self.client = client
        self.welcome_cache = {}
        # ExportFolder("Assets")
        
    
    async def get_welcome_config(self, guild_id: int) -> Optional[WelcomeConfig]:
        """Get welcome configuration for a guild with caching."""
        if guild_id in self.welcome_cache:
            return self.welcome_cache[guild_id]
            
        file = DataManager("Welcome", guild_id)
        if not file.data:
            return None
            
        config = WelcomeConfig(
            message=file["message"],
            channel_id=file["channel"]
        )
        self.welcome_cache[guild_id] = config
        return config
    
    async def fetch_avatar(self,url):
        response = requests.get(url)
        return Image.open(io.BytesIO(response.content))

    async def create_circular_avatar(self,image):
        size = min(image.size)
        mask = Image.new('L', image.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size, size), fill=255)
        mask = mask.crop((0, 0, size, size))
        image = image.crop((0, 0, size, size))
        image.putalpha(mask)
        return image

    async def create_welcome_image(self,member_name, avatar_url):
        base_image_path = baseImagePath
        img = Image.open(base_image_path)

        try:
            font = ImageFont.truetype(Font, SizeFont)
        except IOError:
            try:
                font = ImageFont.truetype(BackupFont, SizeFont)
            except IOError:
                font = ImageFont.load_default()

        avatar = await self.fetch_avatar(avatar_url)
        avatar = avatar.resize(Resize)
        avatar = await self.create_circular_avatar(avatar)  # Make the avatar circular
        # avatar = ImageOps.expand(avatar, border=3, fill='white') 
        img.paste(avatar, avatarPosition, avatar)

        draw = ImageDraw.Draw(img)
        text = f"{member_name}!"
        text_position = textPosition  # Adjust text position as needed
        draw.text(text_position, text, fill=textColor, font=font)

        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)

        # Clean up
        del img
        del avatar

        return buffer

    @slash_command(name="welcome",default_member_permissions=Permissions(administrator=True))
    async def welcome(self, ctx:init):
        pass

    @welcome.subcommand("how", "How to setup the Welcoming Message")
    @feature()
    async def how(self, ctx:init):
        await ctx.send(embed=info_embed("""
Setup a welcome message in a specific Channel, in the message option you can uses these for info (Variables):
{server}  : For the name of the server
{count}   : For the count of members in the server
{mention} : Mention the user
{name}    : Just the name of the user
"""),ephemeral=True)
        
    
    @welcome.subcommand("setup", "Setup the Welcoming Message, check '/welcome how' to know how to set it up")
    @feature()
    @guild_only()
    @cooldown(10)
    @feature()
    async def setupWelcome(self, ctx:init, message: str, channel:TextChannel):
        try:
            # Validate permissions
            if not channel.permissions_for(ctx.guild.me).send_messages:
                await ctx.send("I don't have permission to send messages in that channel!")
                return
                
            # Save configuration
            welcome_file = DataManager("Welcome", ctx.guild_id)
            welcome_file.data = {
                "message": message,
                "channel": channel.id
            }
            welcome_file.save()
            
            # Update cache
            self.welcome_cache[ctx.guild.id] = WelcomeConfig(message=message, channel_id=channel.id)
            
            # Save current member list
            member_file = DataManager("Welcome", ctx.guild.id, file="Members")
            member_file.data = [m.id for m in ctx.guild.members]
            member_file.save()
            
            embed = Embed(
                title="Welcome Message Setup Complete",
                description=f"Channel: {channel.mention}\nMessage: ```{message}```",
                color=colors.Info.value
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in welcome_setup: {e}")
            await ctx.send(embed=error_embed("An error occurred while setting up the welcome message."))
        
    
    
    @commands.Cog.listener()
    async def on_member_join(self, member: Member):
        """Handle new member joins with proper error handling and rate limiting."""
        try:
            await check_feature_inside(member.guild.id, cog=self)
            welcome_file = DataManager("Welcome", member.guild.id)
            if not welcome_file.data:
                return
                
            channel = member.guild.get_channel(welcome_file["channel"])
            if not channel:
                welcome_file.delete_guild()
                return
                
            # Format message with placeholder replacement
            message = str(welcome_file["message"]).format(
                server=member.guild.name,
                count=member.guild.member_count,
                mention=member.mention,
                name=get_name(member)
            )
            
            # Generate and send welcome image
            if member.avatar:
                try:
                    welcome_image = await self.create_welcome_image(
                        get_name(member),
                        str(member.avatar.url)
                    )
                    await channel.send(
                        file=File(welcome_image, f"welcome_{member.id}.png")
                    )
                except Exception as e:
                    logger.error(f"Error creating welcome image: {e}")
                finally:
                    if 'welcome_image' in locals():
                        del welcome_image
                        gc.collect()
            
            await channel.send(message)
            
            # Update member list
            member_file = DataManager("Welcome", member.guild.id, file="Members")
            member_file.data.append(member.id)
            member_file.save()
            
        except Exception as e:
            logger.error(f"Error in on_member_join: {e}")

    @commands.Cog.listener()
    async def on_member_remove(self, member: Member):
        """Handle member leaves with proper error handling."""
        try:
            member_file = DataManager("Welcome", member.guild.id, file="Members")
            if member.id in member_file.data:
                member_file.data.remove(member.id)
                member_file.save()
                
        except Exception as e:
            logger.error(f"Error in on_member_remove: {e}")

    @commands.Cog.listener()
    async def on_ready(self):
        """Handle missed welcomes during downtime with rate limiting."""
        try:
            global_file = DataManager("Welcome", file="Guilds", default=[])
            if not global_file.data:
                return

            for guild_id in global_file.data[:]:  # Create a copy of the list to iterate
                welcome_file = DataManager("Welcome", guild_id)
                if not welcome_file.data:
                    global_file.data.remove(guild_id)
                    welcome_file.delete_guild()
                    continue

                guild = self.bot.get_guild(guild_id)
                if not guild:
                    continue

                channel = guild.get_channel(welcome_file["channel"])
                if not channel:
                    welcome_file.delete_guild()
                    global_file.data.remove(guild_id)
                    continue

                members_file = DataManager("Welcome", guild_id, file="Members")
                old_members = set(members_file.data or [])
                current_members = {member.id for member in guild.members}
                
                new_members = [mid for mid in current_members if mid not in old_members]
                if new_members:
                    for member_id in new_members:
                        member = guild.get_member(member_id)
                        if member:
                            # Add delay to prevent rate limiting
                            await asyncio.sleep(0.5)
                            await self.send_welcome_message(member, channel, welcome_file["message"])

                # Update member cache
                members_file.data = list(current_members)
                members_file.save()

            global_file.save()
                
        except Exception as e:
            logger.error(f"Error in on_ready: {e}")

    async def send_welcome_message(self, member: Member, channel: TextChannel, message_template: str):
        """Send welcome message and image for a member."""
        try:
            message = str(message_template).format(
                server=member.guild.name,
                count=member.guild.member_count,
                mention=member.mention,
                name=get_name(member)
                )
            
            if member.avatar:
                welcome_image = await self.create_welcome_image(
                    get_name(member),
                    str(member.avatar.url)
                )
                await channel.send(
                    file=File(welcome_image, f"welcome_{member.id}.png")
                )
                del welcome_image
                gc.collect()
                
            await channel.send(message)
            
        except Exception as e:
            logger.error(f"Error sending welcome message: {e}")
            
            
        
    
        
    
    

def setup(client):
    client.add_cog(Welcome(client))