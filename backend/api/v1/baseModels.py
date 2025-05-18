from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field

class ChannelID(BaseModel):
    channel_id: str

class OwnerCheckRequest(BaseModel):
    user_id: str

class BadgeRequirement(BaseModel):
    type: str
    value: int
    comparison: str
    specific_value: str = ""

class CreateBadgeRequest(BaseModel):
    name: str
    description: str
    icon_url: str
    rarity: int = Field(ge=1, le=5)
    requirements: List[Dict[str, Union[str, int]]]
    hidden: bool = False

class GuildsRequest(BaseModel):
    guilds: List[str]

class FeatureSetRequest(BaseModel):
    feature_name: str
    value: Union[str, bool, int, float]

class DiscordCallbackRequest(BaseModel):
    code: str
    
class MessageRequest(BaseModel):
    name: str
    channel_id: str
    content: str
    embeds: Optional[List[dict]] = None
    