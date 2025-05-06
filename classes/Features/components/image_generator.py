import io
import PIL
import aiohttp
import traceback
import logging
from typing import Tuple, Optional
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
from PIL.ImageFont import FreeTypeFont, truetype, load_default

from .cache_manager import WelcomeCacheManager

logger = logging.getLogger("welcome.image")


class WelcomeImageGenerator:
    """Handles welcome image generation with advanced customization"""

    def __init__(self, cache_manager: WelcomeCacheManager):
        """Initialize image generator with cache manager"""
        self.cache_manager = cache_manager
        self.session = aiohttp.ClientSession()
        self.effects = {
            "blur": ImageFilter.GaussianBlur,
            "sharpen": ImageFilter.SHARPEN,
            "edge_enhance": ImageFilter.EDGE_ENHANCE,
            "emboss": ImageFilter.EMBOSS,
        }

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()

    async def cleanup(self):
        """Clean up resources"""
        if not self.session.closed:
            await self.session.close()

    async def fetch_avatar(self, url: str) -> Image.Image:
        """Fetch avatar with caching and error handling"""
        try:
            # Check cache first
            cached_avatar = self.cache_manager.get_cached_avatar(url)
            if cached_avatar:
                return cached_avatar

            async with self.session.get(url) as response:
                if response.status != 200:
                    raise ValueError(f"Failed to fetch avatar: {response.status}")

                image_data = await response.read()
                # Ensure high quality avatar by keeping original size initially
                image = Image.open(io.BytesIO(image_data)).convert("RGBA")
                self.cache_manager.cache_avatar(url, image)
                return image.copy()
        except Exception as e:
            logger.error(f"Avatar fetch error: {e}")
            return Image.new("RGBA", (128, 128), "#36393F")

    async def create_circular_avatar(
        self,
        image: Image.Image,
        border_color: Optional[str] = None,
        border_width: int = 0,
    ) -> Image.Image:
        """Create circular avatar with optional border"""
        try:
            size = min(image.size)

            # Create a square image with transparent background
            square = Image.new("RGBA", (size, size), (0, 0, 0, 0))

            # If border is requested, create it first
            if border_color and border_width > 0:
                # Create mask for border
                border_size = size + (border_width * 2)
                border_image = Image.new(
                    "RGBA", (border_size, border_size), (0, 0, 0, 0)
                )
                border_draw = ImageDraw.Draw(border_image)

                # Draw circular border
                border_draw.ellipse(
                    [0, 0, border_size - 1, border_size - 1], fill=border_color
                )

                # Create mask for inner circle
                inner_mask = Image.new("L", (size, size), 0)
                inner_draw = ImageDraw.Draw(inner_mask)
                inner_draw.ellipse([0, 0, size - 1, size - 1], fill=255)

                # Resize and center the avatar
                avatar_square = Image.new("RGBA", (size, size), (0, 0, 0, 0))
                avatar_square.paste(
                    image.resize((size, size), Image.Resampling.LANCZOS), (0, 0)
                )

                # Apply circular mask to avatar
                output = Image.new("RGBA", (border_size, border_size), (0, 0, 0, 0))
                output.paste(border_image, (0, 0))
                output.paste(avatar_square, (border_width, border_width), inner_mask)

                return output

            # If no border, just create circular avatar
            mask = Image.new("L", (size, size), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse([0, 0, size - 1, size - 1], fill=255)

            # Apply the mask to the image
            output = Image.new("RGBA", (size, size), (0, 0, 0, 0))
            output.paste(image.resize((size, size), Image.Resampling.LANCZOS), (0, 0))
            output.putalpha(mask)

            return output

        except Exception as e:
            logger.error(f"Avatar circle error: {e}")
            return image

    async def _get_background(
        self, url: str, target_size: tuple = (1600, 900)
    ) -> Image.Image:
        """Get background image with caching and dynamic sizing"""
        try:
            if not url:
                return Image.new("RGBA", target_size, "#36393F")

            # Check cache with size in key
            cache_key = f"{url}_{target_size[0]}x{target_size[1]}"
            cached_bg = self.cache_manager.get_cached_background(cache_key)
            if cached_bg:
                return cached_bg

            async with self.session.get(
                url, timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status != 200:
                    logger.error(
                        f"Failed to fetch background. Status: {response.status}, URL: {url}"
                    )
                    return Image.new("RGBA", target_size, "#36393F")

                image_data = await response.read()
                image = Image.open(io.BytesIO(image_data)).convert("RGBA")

                # Calculate new size maintaining aspect ratio
                orig_width, orig_height = image.size
                target_width, target_height = target_size
                ratio = max(target_width / orig_width, target_height / orig_height)
                new_size = (int(orig_width * ratio), int(orig_height * ratio))

                # Resize and crop to target size
                image = image.resize(new_size, Image.Resampling.LANCZOS)
                if new_size != target_size:
                    left = (new_size[0] - target_width) / 2
                    top = (new_size[1] - target_height) / 2
                    image = image.crop(
                        (left, top, left + target_width, top + target_height)
                    )

                self.cache_manager.cache_background(cache_key, image)
                return image.copy()

        except Exception as e:
            logger.error(f"Background fetch error: {e}")
            return Image.new("RGBA", target_size, "#36393F")

    async def _get_font(self, size: int, font_name: str = "arial") -> FreeTypeFont:
        """Get font with caching"""
        try:
            cache_key = f"font_{font_name}_{size}"
            cached_font = self.cache_manager.get_cached_font(cache_key)
            if cached_font:
                if isinstance(cached_font, FreeTypeFont):
                    return cached_font
                else:
                    return truetype(
                        "Assets/font/arial.ttf", size
                    )  # Fallback to arial with specified size

            # Map font name to file path
            font_paths = {
                "arial": "Assets/font/arial.ttf",
                "times": "Assets/font/times.ttf",
                "roboto": "Assets/font/Roboto-Regular.ttf",
                "opensans": "Assets/font/OpenSans-Regular.ttf",
                "montserrat": "Assets/font/Montserrat-Regular.ttf",
            }

            font_path = font_paths.get(font_name.lower(), "Assets/font/arial.ttf")
            font = truetype(font_path, size)
            self.cache_manager.cache_font(cache_key, font)
            return font
        except Exception as e:
            logger.error(f"Font error: {e}")
            return truetype(
                "Assets/font/arial.ttf", size
            )  # Fallback to arial with specified size

    def _adjust_color(self, color: str, amount: int) -> str:
        """Adjust color brightness"""
        try:
            rgb = tuple(int(color.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4))
            rgb = tuple(max(0, min(255, c + amount)) for c in rgb)
            return "#{:02x}{:02x}{:02x}".format(*rgb)
        except:
            return color

    def _hex_to_rgba(
        self, hex_color: str, opacity: int = 255
    ) -> Tuple[int, int, int, int]:
        """Convert hex color to RGBA tuple"""
        hex_color = hex_color.lstrip("#")
        if len(hex_color) == 3:
            hex_color = "".join([c * 2 for c in hex_color])
        r, g, b = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
        return (r, g, b, opacity)

    def _create_fallback_image(self, member_name: str) -> io.BytesIO:
        """Create simple fallback image"""
        img = Image.new("RGBA", (800, 400), "#36393F")
        draw = ImageDraw.Draw(img)
        font = load_default()
        draw.text(
            (400, 200), f"Welcome {member_name}!", font=font, fill="white", anchor="mm"
        )
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer

    async def _apply_effects(self, image: Image.Image, effects: dict) -> Image.Image:
        """Apply multiple effects to an image"""
        try:
            if not effects:
                return image

            img = image.copy()

            if effects.get("blur"):
                img = img.filter(ImageFilter.GaussianBlur(effects["blur"]))
            if effects.get("brightness"):
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(effects["brightness"])
            if effects.get("contrast"):
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(effects["contrast"])
            if effects.get("saturation"):
                enhancer = ImageEnhance.Color(img)
                img = enhancer.enhance(effects["saturation"])
            if effects.get("overlay_color"):
                overlay = Image.new("RGBA", img.size, effects["overlay_color"])
                img = Image.blend(img, overlay, effects.get("overlay_opacity", 0.5))
            if effects.get("rotation"):
                img = img.rotate(effects["rotation"], expand=True)

            return img
        except Exception as e:
            logger.error(f"Effect application error: {e}")
            return image

    async def _draw_shape(self, draw: ImageDraw.ImageDraw, shape: dict):
        """Draw various shapes on the image"""
        try:
            shape_type = shape.get("type", "rectangle")
            coords = shape.get("coordinates", [0, 0, 100, 100])
            color = shape.get("color", "#FFFFFF")
            opacity = shape.get("opacity", 255)
            outline = shape.get("outline")
            width = shape.get("width", 1)

            rgba_color = self._hex_to_rgba(color, opacity)

            if shape_type == "rectangle":
                draw.rectangle(coords, fill=rgba_color, outline=outline, width=width)
            elif shape_type == "ellipse":
                draw.ellipse(coords, fill=rgba_color, outline=outline, width=width)
            elif shape_type == "polygon":
                draw.polygon(coords, fill=rgba_color, outline=outline, width=width)
            elif shape_type == "line":
                draw.line(coords, fill=rgba_color, width=width)

        except Exception as e:
            logger.error(f"Shape drawing error: {e}")

    async def _apply_text_effects(self, draw: ImageDraw.ImageDraw, text_obj: dict):
        """Apply advanced text effects"""
        try:
            text = text_obj.get("text", "")
            position = text_obj.get("position", (0, 0))
            font = await self._get_font(
                text_obj.get("size", 48), text_obj.get("font", "arial")
            )
            color = text_obj.get("color", "#FFFFFF")

            # Text effects
            if text_obj.get("shadow"):
                shadow_offset = text_obj.get("shadow_offset", 2)
                shadow_color = text_obj.get(
                    "shadow_color", self._adjust_color(color, -50)
                )
                draw.text(
                    (position[0] + shadow_offset, position[1] + shadow_offset),
                    text,
                    font=font,
                    fill=shadow_color,
                )

            if text_obj.get("outline"):
                outline_size = text_obj.get("outline_size", 1)
                outline_color = text_obj.get("outline_color", "#000000")
                for offset_x in range(-outline_size, outline_size + 1):
                    for offset_y in range(-outline_size, outline_size + 1):
                        if offset_x == 0 and offset_y == 0:
                            continue
                        draw.text(
                            (position[0] + offset_x, position[1] + offset_y),
                            text,
                            font=font,
                            fill=outline_color,
                        )

            if text_obj.get("gradient"):
                # Create gradient text
                gradient = Image.new(
                    "RGBA", (draw.im.size[0], int(font.size)), "#00000000"
                )
                gradient_draw = ImageDraw.Draw(gradient)
                gradient_draw.text(position, text, font=font, fill="#FFFFFF")

                start_color = text_obj["gradient"].get("start_color", "#FFFFFF")
                end_color = text_obj["gradient"].get("end_color", "#000000")
                direction = text_obj["gradient"].get("direction", "horizontal")

                # Apply gradient overlay
                gradient_overlay = self._create_gradient(
                    gradient.size, start_color, end_color, direction
                )
                gradient.paste(gradient_overlay, mask=gradient)
                draw.im.paste(gradient, mask=gradient)
            else:
                draw.text(position, text, font=font, fill=color)

        except Exception as e:
            logger.error(f"Text effect error: {e}")

    def _create_gradient(
        self,
        size: tuple,
        start_color: str,
        end_color: str,
        direction: str = "horizontal",
    ) -> Image.Image:
        """Create a gradient image"""
        gradient = Image.new("RGBA", size)
        draw = ImageDraw.Draw(gradient)

        start_rgb = self._hex_to_rgba(start_color)[:3]
        end_rgb = self._hex_to_rgba(end_color)[:3]

        if direction == "horizontal":
            for x in range(size[0]):
                r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * x / size[0])
                g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * x / size[0])
                b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * x / size[0])
                draw.line([(x, 0), (x, size[1])], fill=(r, g, b))
        else:
            for y in range(size[1]):
                r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * y / size[1])
                g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * y / size[1])
                b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * y / size[1])
                draw.line([(0, y), (size[0], y)], fill=(r, g, b))

        return gradient

    async def create_welcome_image(
        self, member_name: str, avatar_url: str, settings: dict
    ) -> io.BytesIO:
        """Create welcome image with improved file handling and dynamic sizing"""
        background = None
        avatar = None
        buffer = None

        try:
            # Get canvas size from settings or use default
            canvas_size = tuple(settings.get("canvas_size", (1600, 900)))

            # Fetch and process background
            background_url = settings.get("background_url") or ""
            background = await self._get_background(background_url, canvas_size)

            # Apply enhancements
            if settings.get("blur_background"):
                blur_amount = settings.get("blur_amount", 5)
                background = background.filter(ImageFilter.GaussianBlur(blur_amount))

            if settings.get("background_brightness") is not None:
                brightness = settings.get("background_brightness", 0.8)
                enhancer = ImageEnhance.Brightness(background)
                background = enhancer.enhance(brightness)

            if settings.get("overlay_opacity", 0) > 0:
                overlay = Image.new(
                    "RGBA",
                    canvas_size,
                    (0, 0, 0, int(255 * settings.get("overlay_opacity", 0) / 100)),
                )
                background = Image.alpha_composite(background, overlay)

            # Process avatar
            avatar = await self.fetch_avatar(avatar_url)
            if avatar:
                # Convert relative positions to absolute
                avatar_size_raw = settings.get("avatar_size", (20, 20))
                avatar_size = tuple(
                    int(x * canvas_size[i] / 100) for i, x in enumerate(avatar_size_raw)
                )
                # Ensure avatar_size is exactly two elements
                avatar_size = (avatar_size[0], avatar_size[1])
                avatar_pos_raw = settings.get("avatar_position", (10, 10))
                avatar_pos = tuple(
                    int(x * canvas_size[i] / 100) for i, x in enumerate(avatar_pos_raw)
                )
                avatar_pos = (avatar_pos[0], avatar_pos[1])

                # Create circular avatar
                avatar = await self.create_circular_avatar(
                    avatar,
                    border_color=(
                        settings.get("border_color")
                        if settings.get("avatar_border")
                        else None
                    ),
                    border_width=(
                        settings.get("border_width", 0)
                        if settings.get("avatar_border")
                        else 0
                    ),
                )
                avatar = avatar.resize(avatar_size, Image.Resampling.LANCZOS)
                background.paste(avatar, avatar_pos, avatar)

            # Process text elements
            draw = ImageDraw.Draw(background)
            text_elements = settings.get("text_elements", [])

            for element in text_elements:
                # Convert relative position to absolute
                pos = tuple(
                    int(x * canvas_size[i] / 100)
                    for i, x in enumerate(element.get("position", (30, 50)))
                )
                font_size = int(element.get("size", 48) * min(canvas_size) / 1000)
                font = await self._get_font(font_size, element.get("font", "arial"))
                text = str(element.get("text", "Welcome!")).format(member=member_name)

                if element.get("shadow", True):
                    shadow_offset = element.get("shadow_offset", 2)
                    shadow_color = self._adjust_color(
                        element.get("color", "#FFFFFF"), -50
                    )
                    draw.text(
                        (pos[0] + shadow_offset, pos[1] + shadow_offset),
                        text,
                        font=font,
                        fill=shadow_color,
                    )

                draw.text(
                    (pos[0], pos[1]),
                    text,
                    font=font,
                    fill=element.get("color", "#FFFFFF"),
                )

            # Save to buffer
            buffer = io.BytesIO()
            background.save(buffer, format="PNG", optimize=True)
            buffer.seek(0)
            return buffer

        except Exception as e:
            logger.error(f"Error creating welcome image: {e}")
            return self._create_fallback_image(member_name)

        finally:
            if avatar:
                avatar.close()
            if background:
                background.close()
