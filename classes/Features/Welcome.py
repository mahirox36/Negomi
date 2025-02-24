from enum import Enum
import PIL
import aiohttp
import requests
from modules.Nexon import *
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import gc

class WelcomeStyle(Enum):
    IMAGE = "image"
    TEXT = "text"
    EMBED = "embed"
    

class Welcome(commands.Cog):
    def __init__(self, client: Bot):
        self.client = client
        self.font_cache = {}
        self.avatar_cache = {}
        self.welcome_cache = {}
        self.image_cache = {}
        self.background_cache = {}
        self.session = aiohttp.ClientSession()
        self._cache_version = 0  # Add version tracking for cache invalidation

    def invalidate_caches(self, guild_id: int = None):
        """Invalidate all relevant caches for a guild"""
        if guild_id:
            if guild_id in self.welcome_cache:
                del self.welcome_cache[guild_id]
            # Clear image cache entries for this guild
            self.image_cache = {k: v for k, v in self.image_cache.items() 
                              if not k.startswith(f"{guild_id}_")}
        else:
            self.welcome_cache.clear()
            self.image_cache.clear()
        self._cache_version += 1

    async def save_welcome_config(self, guild_id: int, config: dict):
        """Save welcome configuration and invalidate caches"""
        file = DataManager("Welcome", guild_id)
        file.data = config
        file.save()
        self.invalidate_caches(guild_id)  # Clear caches when config changes
        self.welcome_cache[guild_id] = config  # Update with new config

    async def fetch_avatar(self, url: str) -> Image:
        """Fetch avatar with caching and error handling."""
        try:
            if url in self.avatar_cache:
                return self.avatar_cache[url].copy()

            async with self.session.get(url) as response:
                if response.status != 200:
                    raise ValueError(f"Failed to fetch avatar: {response.status}")
                    
                image_data = await response.read()
                # Ensure high quality avatar by keeping original size initially
                image = Image.open(io.BytesIO(image_data)).convert('RGBA')
                self.avatar_cache[url] = image
                return image.copy()
        except Exception as e:
            logger.error(f"Avatar fetch error: {e}")
            return Image.new('RGBA', (128, 128), '#36393F')

    async def create_circular_avatar(self, image: Image, border_color: str = None, border_width: int = 0) -> Image:
        """Create circular avatar with circular border."""
        try:
            size = min(image.size)
            
            # Create a square image with transparent background
            square = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            
            # If border is requested, create it first
            if border_color and border_width > 0:
                # Create mask for border
                border_size = size + (border_width * 2)
                border_image = Image.new('RGBA', (border_size, border_size), (0, 0, 0, 0))
                border_draw = ImageDraw.Draw(border_image)
                
                # Draw circular border
                border_draw.ellipse([0, 0, border_size-1, border_size-1], 
                                  fill=border_color)
                
                # Create mask for inner circle
                inner_mask = Image.new('L', (size, size), 0)
                inner_draw = ImageDraw.Draw(inner_mask)
                inner_draw.ellipse([0, 0, size-1, size-1], fill=255)
                
                # Resize and center the avatar
                avatar_square = Image.new('RGBA', (size, size), (0, 0, 0, 0))
                avatar_square.paste(image.resize((size, size), Image.LANCZOS), (0, 0))
                
                # Apply circular mask to avatar
                output = Image.new('RGBA', (border_size, border_size), (0, 0, 0, 0))
                output.paste(border_image, (0, 0))
                output.paste(avatar_square, (border_width, border_width), inner_mask)
                
                return output
            
            # If no border, just create circular avatar
            mask = Image.new('L', (size, size), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse([0, 0, size-1, size-1], fill=255)
            
            # Apply the mask to the image
            output = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            output.paste(image.resize((size, size), Image.LANCZOS), (0, 0))
            output.putalpha(mask)
            
            return output
            
        except Exception as e:
            logger.error(f"Avatar circle error: {e}")
            return image

    async def create_welcome_image(self, member_name: str, avatar_url: str, settings: dict) -> io.BytesIO:
        """Create welcome image with improved file handling and buffer management."""
        background = None
        avatar = None
        buffer = None
        
        try:
            # Fetch and validate background
            background = await self._get_background(settings["background_url"])
            if not background:
                background = Image.new('RGBA', (800, 400), '#36393F')
            background = background.resize((800, 400), Image.LANCZOS)
    
            # Apply enhancements if needed
            if settings.get("blur_background"):
                background = background.filter(ImageFilter.GaussianBlur(5))
                enhancer = ImageEnhance.Brightness(background)
                background = enhancer.enhance(0.8)
    
            # Process avatar
            avatar = await self.fetch_avatar(avatar_url)
            if avatar:
                # Create circular avatar with border
                avatar = await self.create_circular_avatar(
                    avatar, 
                    border_color=settings.get("border_color") if settings.get("avatar_border") else None,
                    border_width=settings.get("border_width", 0) if settings.get("avatar_border") else 0
                )
                
                # Ensure avatar_size is a tuple
                avatar_size = tuple(settings.get("avatar_size", (128, 128)))
                avatar = avatar.resize(avatar_size, Image.LANCZOS)
    
                # Calculate position with border offset
                x, y = settings.get("avatar_position", (100, 100))
                if settings.get("avatar_border"):
                    x -= settings.get("border_width", 0)
                    y -= settings.get("border_width", 0)
    
                # Paste avatar onto background
                background.paste(avatar, (x, y), avatar)
    
            # Add text
            draw = ImageDraw.Draw(background)
            font = await self._get_font(settings.get("font_size", 48))
            text = f"Welcome {member_name}!"
            text = str(settings.get("text", "Welcome {member}!")).format(member=member_name)
            
            # Add text shadow
            shadow_color = self._adjust_color(settings.get("font_color", "#FFFFFF"), -50)
            text_pos = settings.get("text_position", (250, 150))
            offset = 2
            
            # Draw shadow and main text
            draw.text((text_pos[0] + offset, text_pos[1] + offset), text, font=font, fill=shadow_color)
            draw.text(text_pos, text, font=font, fill=settings.get("font_color", "#FFFFFF"))
    
            # Save to buffer with explicit cleanup
            buffer = io.BytesIO()
            background.save(buffer, format='PNG', optimize=True, quality=95)
            buffer.seek(0)
            
            # Create a new buffer with the contents to ensure it's not tied to the original images
            final_buffer = io.BytesIO(buffer.getvalue())
            return final_buffer
    
        except Exception as e:
            logger.error(f"Welcome image creation error: {str(e)}")
            # Create a simple fallback image if the main one fails
            return self._create_fallback_image(member_name)
            
        finally:
            # Cleanup resources
            if avatar:
                avatar.close()
            if background:
                background.close()
            if buffer:
                buffer.close()
            gc.collect()

    async def _get_background(self, url: str) -> Image:
        """Get background image with caching."""
        try:
            # First check if URL is None or empty
            if not url:
                logger.warning("No background URL provided")
                return Image.new('RGBA', (800, 400), '#36393F')

            # Check cache
            if url in self.background_cache:
                logger.debug(f"Using cached background for URL: {url}")
                return self.background_cache[url].copy()

            
            # Validate URL format
            if not url.startswith(('http://', 'https://')):
                logger.error(f"Invalid URL format: {url}")
                return Image.new('RGBA', (800, 400), '#36393F')

            async with self.session.get(url, timeout=30) as response:
                if response.status != 200:
                    logger.error(f"Failed to fetch background. Status: {response.status}, URL: {url}")
                    raise ValueError(f"Failed to fetch background: {response.status}")
                
                image_data = await response.read()
                if not image_data:
                    logger.error("Received empty image data")
                    raise ValueError("Empty image data received")

                # Try to open the image data
                image = Image.open(io.BytesIO(image_data))
                
                # Check if image was actually loaded
                if not image:
                    logger.error("Failed to open image data")
                    raise ValueError("Failed to open image data")

                # Convert to RGBA and verify the conversion
                image = image.convert('RGBA')
                if image.mode != 'RGBA':
                    logger.error(f"Failed to convert image to RGBA mode. Current mode: {image.mode}")
                    raise ValueError("Failed to convert image to RGBA")
                
                # Cache the successful image
                self.background_cache[url] = image
                return image.copy()

        except aiohttp.ClientError as e:
            logger.error(f"Network error while fetching background: {str(e)}")
            return Image.new('RGBA', (800, 400), '#36393F')
        except PIL.UnidentifiedImageError as e:
            logger.error(f"Invalid image format: {str(e)}")
            return Image.new('RGBA', (800, 400), '#36393F')
        except TimeoutError as e:
            logger.error(f"Timeout while fetching background: {str(e)}")
            return Image.new('RGBA', (800, 400), '#36393F')
        except Exception as e:
            logger.error(f"Unexpected error while fetching background: {str(e)}")
            return Image.new('RGBA', (800, 400), '#36393F')

    async def _get_font(self, size: int) -> ImageFont:
        """Get font with caching."""
        try:
            cache_key = f"font_{size}"
            if cache_key in self.font_cache:
                return self.font_cache[cache_key]

            # Use a default system font
            font = ImageFont.truetype("arial.ttf", size)
            self.font_cache[cache_key] = font
            return font
        except:
            return ImageFont.load_default()

    def _adjust_color(self, color: str, amount: int) -> str:
        """Adjust color brightness."""
        try:
            rgb = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
            rgb = tuple(max(0, min(255, c + amount)) for c in rgb)
            return '#{:02x}{:02x}{:02x}'.format(*rgb)
        except:
            return color

    def _create_fallback_image(self, member_name: str) -> io.BytesIO:
        """Create simple fallback image."""
        img = Image.new('RGBA', (800, 400), '#36393F')
        draw = ImageDraw.Draw(img)
        font = ImageFont.load_default()
        draw.text((400, 200), f"Welcome {member_name}!", font=font, fill='white', anchor='mm')
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        return buffer

    def __del__(self):
        """Cleanup resources."""
        if hasattr(self, 'session'):
            asyncio.create_task(self.session.close())

    def get_default_settings(self) -> dict:
        """Get default welcome settings"""
        return {
            "message": "Welcome {mention} to {server}!",
            "channel_id": None,
            "style": WelcomeStyle.IMAGE.value,
            "enabled": True,
            "embed_color": colors.Info.value,
            "image_settings": {
                "background_url": "https://raw.githubusercontent.com/mahirox36/Negomi/refs/heads/main/Assets/img/Welcome.png",
                "text": "Welcome {member}!",
                "avatar_size": [128, 128],
                "avatar_position": [100, 100],
                "text_position": [250, 150],
                "font_size": 48,
                "font_color": "#FFFFFF",
                "blur_background": False,
                "avatar_border": True,
                "border_color": "#FFFFFF",
                "border_width": 3
            }
        }
        
    async def get_welcome_config(self, guild_id: int) -> Optional[dict]:
        """Get welcome configuration with defaults"""
        if guild_id in self.welcome_cache:
            return self.welcome_cache[guild_id]
            
        file = DataManager("Welcome", guild_id)
        if not file.data:
            return None
            
        # Merge with defaults to ensure all fields exist
        config = self.get_default_settings()
        config.update(file.data)
        
        # Convert lists back to tuples for image processing
        img_settings = config["image_settings"]
        img_settings["avatar_size"] = tuple(img_settings["avatar_size"])
        img_settings["avatar_position"] = tuple(img_settings["avatar_position"])
        img_settings["text_position"] = tuple(img_settings["text_position"])
        
        self.welcome_cache[guild_id] = config
        return config
    
    @slash_command(name="welcome",default_member_permissions=Permissions(administrator=True))
    async def welcome(self, ctx:init):
        pass

    @welcome.subcommand("how", "Learn how to configure welcome messages")
    @feature()
    async def how(self, ctx: init):
        embed = Embed.Info(
            title="Welcome Message Configuration Guide",
            description="Use these variables in your welcome message:"
        )
        embed.add_field(name="Available Variables", value="""
• `{server}` - Server name
• `{count}` - Total member count 
• `{mention}` - Member mention
• `{name}` - Member name
        """)
        embed.add_field(name="Example", value="`Welcome {mention} to {server}! You are member #{count}`")
        await ctx.send(embed=embed, ephemeral=True)

    @welcome.subcommand("setup", "Configure the welcome message system")
    @feature()
    @guild_only()
    @cooldown(10)
    async def setupWelcome(self, ctx: init, 
                          message: str = SlashOption(description="Welcome message using variables like {mention}"),
                          channel: TextChannel = SlashOption(description="Channel to send welcome messages")):
        try:
            await ctx.response.defer()
            # Validate channel permissions
            required_perms = ['send_messages', 'embed_links', 'attach_files']
            missing_perms = [perm for perm in required_perms 
                           if not getattr(channel.permissions_for(ctx.guild.me), perm)]
            
            if missing_perms:
                await ctx.send(embed=Embed.Error(
                    f"I need the following permissions in {channel.mention}: " +
                    ", ".join(missing_perms).replace('_', ' ').title(),"Missing Permissions"),
                    ephemeral=True
                )
                return

            # Validate message length
            if len(message) > 2000:
                await ctx.send("Message too long! Must be 2000 characters or less.", ephemeral=True)
                return

            # Save configuration
            welcome_file = DataManager("Welcome", ctx.guild_id)
            settings = self.get_default_settings()
            settings["message"] = message
            settings["channel_id"] = channel.id
            welcome_file.data = settings
            welcome_file.save()

            # Update cache
            self.welcome_cache[ctx.guild.id] = settings

            # Save current members
            member_file = DataManager("Welcome", ctx.guild_id, file="Members")
            member_file.data = [m.id for m in ctx.guild.members]
            member_file.save()

            # Send confirmation with preview
            embed = Embed.Info(
                title="✅ Welcome System Configured",
                description=f"Channel: {channel.mention}\nMessage Preview:"
            )
            embed.add_field(
                name="Sample Output", 
                value=message.format(
                    server=ctx.guild.name,
                    count=ctx.guild.member_count,
                    mention=ctx.user.mention,
                    name=ctx.user.display_name
                )
            )
            embed.set_footer(text="Use /welcome customize to personalize the appearance")
            
            await ctx.send(embed=embed,ephemeral=True)
            
        except Exception as e:
            logger.error(f"Welcome setup error in {ctx.guild_id}: {e}")
            await ctx.send(
                embed=Embed.Error("Failed to setup welcome system. Please try again."),
                ephemeral=True
            )

    @welcome.subcommand("preview", "Preview your welcome message")
    @feature()
    @guild_only()
    async def preview(self, ctx: init):
        await ctx.response.defer(ephemeral=True)
        config = await self.get_welcome_config(ctx.guild_id)
        if not config:
            await ctx.send("Please set up welcome message first using /welcome setup", ephemeral=True)
            return
            
        channel = ctx.channel
        await self.send_welcome_message(ctx.user, channel, config, ctx=ctx)
    
    @welcome.subcommand("customize", "Customize your welcome message appearance")
    @feature()
    @guild_only()
    async def customize(self, ctx: init):
        config = await self.get_welcome_config(ctx.guild.id)
        if not config:
            await ctx.send("Please set up welcome message first using /welcome setup", ephemeral=True)
            return

        embed = Embed.Info(
            title="Welcome Message Customization",
            description="Use the buttons below to customize your welcome message appearance:"
        )
        embed.add_field(name="Available Options", value="""
• Background - Set a custom background image
• Text - Set a custom Text inside of the image
• Text Position - Adjust where the welcome text appears
• Avatar Position - Adjust where the user's avatar appears
• Font Size - Adjust the font size
• Avatar Size - Adjust user's pfp size
• Colors - Change text and border colors
        """)

        await ctx.send(embed=embed, view=WelcomeCustomizer(config), ephemeral=True)

    @welcome.subcommand("style", "Change welcome message style")
    @feature()
    async def style(self, ctx: init, style: str = SlashOption(
        name="style",
        choices={"Image with Text": "image", "Text Only": "text", "Embed": "embed"}
    )):
        welcome_file = DataManager("Welcome", ctx.guild_id)
        if not welcome_file.data:
            await ctx.send("Please set up welcome message first using /welcome setup", ephemeral=True)
            return

        welcome_file.data["style"] = style
        welcome_file.save()
        await ctx.send(f"Welcome message style updated to: {style}", ephemeral=True)
        
    @commands.Cog.listener()
    async def on_member_join(self, member: Member):
        """Handle new member joins with caching and rate limiting."""
        if member.bot:
            return

        try:
            # Check feature and get cached config
            await check_feature_inside(member.guild.id, cog=self)
            config = await self.get_welcome_config(member.guild.id)
            if not config or not config.get("channel_id"):
                return

            # Get channel with validation
            channel = member.guild.get_channel(config.get("channel_id"))
            if not channel:
                logger.warning(f"Welcome channel {config.get("channel_id")} not found in {member.guild.id}")
                return

            # Send welcome message with proper rate limiting
            async with channel.typing():
                await self.send_welcome_message(member, channel, config)

            # Update member cache
            member_file = DataManager("Welcome", member.guild.id, file="Members")
            member_file.data = list(set(member_file.data + [member.id]))
            member_file.save()

        except Exception as e:
            logger.error(f"Welcome error in {member.guild.id} for {member.id}: {e}")

    @commands.Cog.listener() 
    async def on_member_remove(self, member: Member):
        """Track member leaves with optimized caching."""
        try:
            member_file = DataManager("Welcome", member.guild.id, file="Members")
            if member.id in member_file.data:
                member_file.data.remove(member.id)
                member_file.save()

        except Exception as e:
            logger.error(f"Member remove error in {member.guild.id}: {e}")

    @commands.Cog.listener()
    async def on_ready(self):
        """Process missed welcomes with smart batching and rate limiting."""
        try:
            # Get active welcome guilds
            global_file = DataManager("Welcome", file="Guilds", default=[])
            active_guilds = set(global_file.data)
            if not active_guilds:
                return

            for guild_id in active_guilds:
                try:
                    # Get guild and config
                    guild = self.client.get_guild(guild_id)
                    config = await self.get_welcome_config(guild_id)
                    if not guild or not config or not config.get("enabled"):
                        continue

                    # Validate channel
                    channel = guild.get_channel(config.get("channel_id"))
                    if not channel:
                        continue

                    # Process new members in batches
                    members_file = DataManager("Welcome", guild_id, file="Members")
                    old_members = set(members_file.data or [])
                    current_members = {m.id for m in guild.members}
                    
                    new_members = current_members - old_members
                    if new_members:
                        # Process in smaller batches to avoid rate limits
                        for batch in [list(new_members)[i:i+5] for i in range(0, len(new_members), 5)]:
                            for member_id in batch:
                                member = guild.get_member(member_id)
                                if member and not member.bot:
                                    await self.send_welcome_message(member, channel, config)
                                    await asyncio.sleep(1.5)  # Rate limit protection
                            
                            await asyncio.sleep(5)  # Batch cooldown

                    # Update member cache
                    members_file.data = list(current_members)
                    members_file.save()

                except Exception as e:
                    logger.error(f"Welcome ready error in guild {guild_id}: {e}")
                    continue

        except Exception as e:
            logger.error(f"Welcome ready error: {e}")

    async def send_welcome_message(self, member: Member, channel: TextChannel, config: dict, ctx: init = None):
        """Send welcome message with improved cache handling"""
        try:
            message = await self.format_welcome_message(member, config["message"])
            style = config["style"] or WelcomeStyle.TEXT.value
            
            match style:
                case WelcomeStyle.IMAGE.value:
                    if member.avatar:
                        # Include config version in cache key
                        cache_key = f"{member.guild.id}_{member.id}_{member.avatar.key}_{self._cache_version}"
                        welcome_image = None

                        if cache_key in self.image_cache:
                            # Verify cached image is still valid
                            cached = self.image_cache[cache_key]
                            try:
                                cached.seek(0)
                                welcome_image = io.BytesIO(cached.read())
                                cached.seek(0)
                            except (ValueError, OSError):
                                del self.image_cache[cache_key]
                                welcome_image = None

                        if not welcome_image:
                            welcome_image = await self.create_welcome_image(
                                member.display_name,
                                str(member.avatar.url),
                                config["image_settings"]
                            )
                            # Store a copy in cache
                            self.image_cache[cache_key] = io.BytesIO(welcome_image.getvalue())
                            welcome_image.seek(0)

                        if welcome_image.getbuffer().nbytes == 0:
                            raise ValueError("Generated image is empty")

                        await channel.send(
                            content=message,
                            file=File(welcome_image, f"welcome_{member.id}.png")
                        ) if ctx is None else await ctx.send(
                            content=message,
                            file=File(welcome_image, f"welcome_{member.id}.png"),
                            embed=Embed.Info("☝️ Above is how the welcome message will appear"),
                            ephemeral=True
                        )
                    else:
                        await channel.send(message)

                case WelcomeStyle.EMBED.value:
                    embed = Embed(
                        title=f"Welcome to {member.guild.name}!",
                        description=message,
                        color=config["embed_color"] or colors.Info.value
                    )
                    if member.avatar:
                        embed.set_thumbnail(url=member.avatar.url)
                    if config["image_settings"]["background_url"]:
                        embed.set_image(url=config["image_settings"]["background_url"])
                    await channel.send(embed=embed) if ctx is None else await ctx.send(embeds=[embed, Embed.Info("☝️ Above is how the welcome message will appear")], ephemeral=True)
                    
                case _:
                    await channel.send(message) if ctx is None else await ctx.send(message,embed=Embed.Info("☝️ Above is how the welcome message will appear"), ephemeral=True)

            # Cleanup cache if too large
            if len(self.image_cache) > 100:
                self.image_cache = {k: v for k, v in self.image_cache.items() 
                                  if k.split('_')[0] in self.welcome_cache}

        except Exception as e:
            logger.error(f"Welcome message error in {member.guild.id}: {e}", exc_info=True)
            if ctx:
                await ctx.send(
                    embed=Embed.Error("Failed to preview welcome message. Check permissions and settings."),ephemeral=True
                )

    async def format_welcome_message(self, member: Member, message: str) -> str:
        """Safely format welcome message with fallbacks."""
        try:
            return str(message).format(
                server=member.guild.name,
                count=member.guild.member_count,
                mention=member.mention,
                name=member.display_name
            )
        except Exception:
            return f"Welcome {member.mention} to {member.guild.name}!"

class WelcomeCustomizer(ui.View):
    def __init__(self, welcome_config: dict):
        super().__init__(timeout=300)
        self.config = welcome_config
        self.message = None

    @button(label="Background", style=ButtonStyle.blurple)
    async def background_button(self, button: Button, interaction: Interaction):
        modal = BackgroundModal(self)
        await interaction.response.send_modal(modal)
        
    @button(label="Text", style=ButtonStyle.blurple)
    async def text_change(self, button: Button, interaction: Interaction):
        modal = TextModal(self)
        await interaction.response.send_modal(modal)

    @button(label="Text Position", style=ButtonStyle.green)
    async def text_position(self, button: Button, interaction: Interaction):
        await interaction.response.send_message(
            "Use arrow buttons to adjust text position:",
            view=PositionEditor("text_position", self),
            ephemeral=True
        )

    @button(label="Avatar Position", style=ButtonStyle.green)
    async def avatar_position(self, button: Button, interaction: Interaction):
        await interaction.response.send_message(
            "Use arrow buttons to adjust avatar position:",
            view=PositionEditor("avatar_position", self),
            ephemeral=True
        )

    @button(label="Font Size", style=ButtonStyle.grey)
    async def font_size(self, button: Button, interaction: Interaction):
        await interaction.response.send_message(
            "Adjust font size:",
            view=SizeAdjuster("font_size", self),
            ephemeral=True
        )

    @button(label="Avatar Size", style=ButtonStyle.grey)
    async def avatar_size(self, button: Button, interaction: Interaction):
        await interaction.response.send_message(
            "Adjust avatar size:",
            view=SizeAdjuster("avatar_size", self),
            ephemeral=True
        )

    @button(label="Colors", style=ButtonStyle.grey)
    async def colors(self, button: Button, interaction: Interaction):
        await interaction.response.send_message(
            "Customize colors:",
            view=ColorPicker(self),
            ephemeral=True
        )

    async def update_config(self, interaction: Interaction, key: str, value: Any):
        """Update config with cache invalidation"""
        welcome_file = DataManager("Welcome", interaction.guild_id)
        if key.startswith("image_settings."):
            _, setting = key.split(".")
            welcome_file.data["image_settings"][setting] = value
        else:
            welcome_file.data[key] = value
        welcome_file.save()
        
        # Invalidate caches through the cog
        cog = interaction.client.get_cog("Welcome")
        if cog:
            cog.invalidate_caches(interaction.guild_id)

class SizeAdjuster(ui.View):
    def __init__(self, adjust_type: str, parent: WelcomeCustomizer):
        super().__init__()
        self.adjust_type = adjust_type
        self.parent = parent
        self.current_size = parent.config["image_settings"].get(adjust_type, 48 if adjust_type == "font_size" else [128, 128])

    @button(label="+", style=ButtonStyle.grey)
    async def increase(self, button: Button, interaction: Interaction):
        if self.adjust_type == "font_size":
            self.current_size += 2
        else:
            self.current_size[0] += 10
            self.current_size[1] += 10
        await self.update_size(interaction)

    @button(label="-", style=ButtonStyle.grey)
    async def decrease(self, button: Button, interaction: Interaction):
        if self.adjust_type == "font_size":
            self.current_size = max(8, self.current_size - 2)
        else:
            self.current_size[0] = max(32, self.current_size[0] - 10)
            self.current_size[1] = max(32, self.current_size[1] - 10)
        await self.update_size(interaction)

    async def update_size(self, interaction: Interaction):
        await self.parent.update_config(interaction, f"image_settings.{self.adjust_type}", self.current_size)

class PositionEditor(ui.View):
    def __init__(self, edit_type: str, parent: WelcomeCustomizer):
        super().__init__()
        self.edit_type = edit_type
        self.parent = parent
        self.position = list(parent.config["image_settings"][edit_type])

    @button(label="⬆️", style=ButtonStyle.grey)
    async def up(self, _, interaction: Interaction):
        self.position[1] -= 10
        await self.update_position(interaction)

    @button(label="⬇️", style=ButtonStyle.grey)
    async def down(self, _, interaction: Interaction):
        self.position[1] += 10
        await self.update_position(interaction)

    @button(label="⬅️", style=ButtonStyle.grey)
    async def left(self, _, interaction: Interaction):
        self.position[0] -= 10
        await self.update_position(interaction)

    @button(label="➡️", style=ButtonStyle.grey)
    async def right(self, _, interaction: Interaction):
        self.position[0] += 10
        await self.update_position(interaction)

    async def update_position(self, interaction: Interaction):
        await self.parent.update_config(interaction, f"image_settings.{self.edit_type}", self.position)

class BackgroundModal(ui.Modal):
    def __init__(self, parent: WelcomeCustomizer):
        super().__init__(title="Set Background Image")
        self.parent = parent
        self.url = ui.TextInput(
            label="Background Image URL",
            placeholder="https://example.com/image.png",
            required=True
        )
        self.add_item(self.url)

    async def callback(self, interaction: Interaction):
        await self.parent.update_config(interaction, "image_settings.background_url", self.url.value)

class TextModal(ui.Modal):
    def __init__(self, parent: WelcomeCustomizer):
        super().__init__(title="Set Text Image")
        self.parent = parent
        self.text = ui.TextInput(
            label="Text inside the Image",
            placeholder="Welcome {member}!",
            default_value="Welcome {member}!",
            required=True
        )
        self.add_item(self.text)

    async def callback(self, interaction: Interaction):
        await self.parent.update_config(interaction, "image_settings.text", self.text.value)

class ColorPicker(ui.View):
    def __init__(self, parent: WelcomeCustomizer):
        super().__init__()
        self.parent = parent
        self.add_item(ui.Select(
            placeholder="Choose text color",
            options=[
                SelectOption(label="White", value="#FFFFFF"),
                SelectOption(label="Black", value="#000000"),
                SelectOption(label="Blue", value="#0000FF"),
                SelectOption(label="Red", value="#FF0000"),
                SelectOption(label="Green", value="#00FF00"),
                SelectOption(label="Gold", value="#FFD700")
            ],
            custom_id="color_select"
        ))

    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.data["custom_id"] == "color_select":
            await self.parent.update_config(interaction, "image_settings.font_color", interaction.data["values"][0])
        return True

def setup(client):
    client.add_cog(Welcome(client))