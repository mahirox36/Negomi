from enum import Enum
from typing import Tuple, List, Dict, Any, Union, Optional


class WelcomeStyle(Enum):
    """Welcome message style options"""

    IMAGE = "image"
    TEXT = "text"
    EMBED = "embed"
    ANIMATED = "animated"
    CAROUSEL = "carousel"


class ImageElementType(Enum):
    """Types of elements that can be added to welcome images"""

    TEXT = "text"
    AVATAR = "avatar"
    RECTANGLE = "rectangle"
    CIRCLE = "circle"
    SERVER_ICON = "server_icon"
    IMAGE = "image"
    GRADIENT = "gradient"
    BLUR = "blur"
    OVERLAY = "overlay"
    SHAPE = "shape"


class TextEffectType(Enum):
    """Types of text effects for welcome messages"""

    SHADOW = "shadow"
    OUTLINE = "outline"
    GRADIENT = "gradient"
    GLOW = "glow"
    STROKE = "stroke"


class AnimationType(Enum):
    """Types of animations for welcome messages"""

    FADE = "fade"
    SLIDE = "slide"
    BOUNCE = "bounce"
    SCALE = "scale"
    ROTATE = "rotate"
    PARTICLES = "particles"


# Type definitions for welcome elements
TextElement = Dict[str, Any]  # text, position, size, color, font, shadow, shadow_offset
CustomElement = Dict[str, Any]  # type, position, size, color, opacity, outline_color
ImageSettings = Dict[str, Any]  # All image generation settings

# Type aliases for improved code readability
TextEffect = Dict[str, Any]  # effect_type, parameters
Animation = Dict[str, Any]  # animation_type, duration, parameters
Position = Tuple[float, float]  # x, y coordinates (0-1 range)
Size = Tuple[int, int]  # width, height in pixels
Color = str  # hex color code
