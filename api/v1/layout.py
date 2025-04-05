from enum import StrEnum
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import TYPE_CHECKING
from modules.Nexon import colours
from .baseModels import *
from nexon.enums import RequirementType

if TYPE_CHECKING:
    from classes.Other.Dashboard import DashboardCog
    
class Types(StrEnum):
    header = "header"
    cards = "cards"
    panel = "panel"

router = APIRouter()

# [GET] /settings/sidebar
# [GET] /settings/{page}
# [GET] /settings/server/{page}

pages: Dict[str, List] = {
    "overview": [
        {
            "type": Types.header,
            "text": "Overview",
            "subtext": "General information about the server",
            "icon": "fa-solid fa-gauge" 
        },
        {
            "type": Types.cards,
            "interaction": "link_button",
            "buttons": [
                {
                    "text": "AI",
                    "subtext": "Configure AI settings and responses",
                    "icon": "fa-solid fa-robot",
                    "link": "/ai",
                    "buttonText": "Configure AI"
                },
                {
                    "text": "Auto Role",
                    "subtext": "Manage automatic role assignment",
                    "icon": "fa-solid fa-user-plus",
                    "link": "/auto_role",
                    "buttonText": "Configure Auto Role"
                },
                {
                    "text": "Welcome",
                    "subtext": "Customize welcome messages and images",
                    "icon": "fa-solid fa-gift",
                    "link": "/welcome", 
                    "buttonText": "Configure Welcome"
                },
                {
                    "text": "Badges",
                    "subtext": "Manage achievement badges",
                    "icon": "fa-solid fa-medal",
                    "link": "/badges",
                    "buttonText": "Configure Badges"
                },
                {
                    "text": "Leveling",
                    "subtext": "Configure XP and level settings",
                    "icon": "fa-solid fa-trophy",
                    "link": "/leveling",
                    "buttonText": "Configure Leveling"
                },
                {
                    "text": "Temp Channels",
                    "subtext": "Manage temporary voice channels",
                    "icon": "fa-solid fa-headset",
                    "link": "/temp-voice",
                    "buttonText": "Configure Temp Channels"
                }
            ]
        }
    ],
    "basic-settings": [
        {
            "type": Types.header,
            "text": "Basic Settings",
            "subtext": "Core server configuration",
            "icon": "fa-solid fa-cog"
        },
        {
            "type": Types.panel,
            "text": "Embed Appearance",
            "icon": "fa-solid fa-palette",
            "subtext": "Customize bot message appearances",
            "settings": [
                {
                    "name": "Info Embed Color",
                    "type": "color",
                    "value": colours.Info.hex,
                    "description": "Color for informational messages"
                },
                {
                    "name": "Warning Embed Color",
                    "type": "color", 
                    "value": colours.Warn.hex,
                    "description": "Color for warning messages"
                },
                {
                    "name": "Error Embed Color",
                    "type": "color",
                    "value": colours.Error.hex,
                    "description": "Color for error messages"
                }
            ]
        },
        {
            "type": Types.panel,
            "text": "Badge Appearance",
            "icon": "fa-solid fa-medal",
            "subtext": "Customize badge appearances",
            "settings": [
                {
                    "name": "Badge Common Color",
                    "type": "color",
                    "value": colours.Common.hex,
                    "description": "Color for success messages"
                },
                {
                    "name": "Badge Uncommon Color",
                    "type": "color",
                    "value": colours.Uncommon.hex,
                    "description": "Color for uncommon badges"
                },
                {
                    "name": "Badge Rare Color",
                    "type": "color",
                    "value": colours.Rare.hex,
                    "description": "Color for rare badges"
                },
                {
                    "name": "Badge Epic Color",
                    "type": "color",
                    "value": colours.Epic.hex,
                    "description": "Color for epic badges"
                },
                {
                    "name": "Badge Legendary Color",
                    "type": "color",
                    "value": colours.Legendary.hex,
                    "description": "Color for legendary badges"
                }
            ]
        }
    ],
    "auto-role": [
        {
            "type": Types.header,
            "text": "Auto Role",
            "subtext": "Configure roles that are automatically assigned to new members",
            "icon": "fa-solid fa-user-tag"
        },
        {
            "type": Types.panel,
            "text": "Member Auto Roles",
            "subtext": "Roles that will be automatically assigned to new members when they join",
            "icon": "fa-solid fa-users",
            "settings": [
                {
                    "name": "userRoles",
                    "type": "select",
                    "multiple": True,
                    "searchable": True
                }
            ]
        },
        {
            "type": Types.panel,
            "text": "Bot Auto Roles",
            "subtext": "Roles that will be automatically assigned to new bots when they are added",
            "icon": "fa-solid fa-robot",
            "settings": [
                {
                    "name": "botRoles",
                    "type": "select",
                    "multiple": True,
                    "searchable": True
                }
            ]
        }
    ]
}

@router.get("/settings/sidebar")
async def get_sidebar():
    """Get sidebar settings"""
    return {
            "General": [
                {
                    "name": "Overview",
                    "icon": "fa-solid fa-gauge",
                },
                {
                    "name": "Basic Settings",
                    "icon": "fa-solid fa-cog",
                },
                {
                    "name": "Badges",
                    "icon": "fa-solid fa"
                }
            ]
    }

@router.get("/settings/server/sidebar")
async def get_server_sidebar():
    """Get server sidebar settings"""
    return {
            "General": [
                {
                    "name": "Overview",
                    "link": "overview",
                    "icon": "fa-solid fa-gauge",
                },
                {
                    "name": "Basic Settings",
                    "link": "basic-settings",
                    "icon": "fa-solid fa-cog"
                }
            ],
            "Features": [
                # {
                #     "name": "AI",
                #     "link": "ai",
                #     "icon": "fa-solid fa-robot"
                # },
                {
                    "name": "Auto Role",
                    "link": "auto-role",
                    "icon": "fa-solid fa-user-plus"
                },
                {
                    "name": "Backup",
                    "link": "backup",
                    "icon": "fa-solid fa-hdd"
                },
                {
                    "name": "Custom Roles",
                    "link": "custom-roles",
                    "icon": "fa-solid fa-user-tag"
                },
                {
                    "name": "Temporary Voice",
                    "link": "temp-voice",
                    "icon": "fa-solid fa-headset"
                },
                {
                    "name": "Welcome",
                    "link": "welcome",
                    "icon": "fa-solid fa-gift"
                },
                {
                    "name": "Leveling",
                    "link": "leveling",
                    "icon": "fa-solid fa-trophy"
                },
                {
                    "name": "Badges",
                    "link": "badges",
                    "icon": "fa-solid fa-medal"
                }
            ]
        }
@router.get("/settings/server/{page}")
async def get_server_settings_page(page: str):
    """Get server settings page"""
    return pages[page]
@router.get("/badges/requirements")
async def get_badges_requirements():
    return [requirement.value for requirement in RequirementType]