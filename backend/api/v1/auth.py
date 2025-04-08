from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from modules.DiscordConfig import overwriteOwner, config
from typing import TYPE_CHECKING, Optional

from .baseModels import *
import time
from nexon.OAuth2 import OAuth2Client, OAuth2Session, OAuth2Token
from nexon.types.oauth2 import Guild, OAuth2Scope
import asyncio
import logging

if TYPE_CHECKING:
    from backend.apiManager import APIServer

router = APIRouter(tags=["auth"])
logger = logging.getLogger("bot")

# Cache structure to store guild data with timestamps
guild_cache = {}
CACHE_EXPIRE_TIME = 3600  # 1 hour in seconds
CACHE_CLEANUP_INTERVAL = 1800  # 30 minutes

async def get_cached_guilds(backend: 'APIServer', access_token: str) -> List[Guild]:
    current_time = time.time()
    cache_key = f"guilds_{access_token}"
    
    # Check if cached data exists and is still valid
    if cache_key in guild_cache:
        cached_data = guild_cache[cache_key]
        if current_time - cached_data['timestamp'] < CACHE_EXPIRE_TIME:
            return cached_data['guilds']
    
    # If no cache or expired, fetch new data
    oauth_token = OAuth2Token({
        'access_token': access_token,
        'token_type': 'Bearer',
    })
    session = OAuth2Session(backend.oauth_client, oauth_token)
    
    guilds = await session.fetch_guilds()
    
    # Update cache
    guild_cache[cache_key] = {
        'timestamp': current_time,
        'guilds': guilds
    }
    
    return guilds

async def check_owner(request: Request):
    """Check if the user is the bot owner"""
    backend: APIServer = request.app.state.backend
    try:
        access_token = await backend.verify_auth(request)
        if access_token is None:
            raise HTTPException(status_code=401, detail="Access token is missing")
        session = backend.oauth_sessions[access_token]
        
        # Get user data from OAuth session
        user = await session.fetch_user()
        user_id = int(user["id"])
        
        if user_id != overwriteOwner and user_id != backend.client.owner_id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        return True
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/discord/callback")
async def discord_callback(request: Request, data: DiscordCallbackRequest):
    """Handle Discord OAuth2 callback"""
    backend: APIServer = request.app.state.backend
    try:
        code = data.code
        
        # Get access token
        token = await backend.oauth_client.get_access_token(code)
        
        # Create new OAuth session
        session = OAuth2Session(backend.oauth_client, token)
        
        # Get user data
        user = await session.fetch_user()
        
        # Cache session and user data
        backend.oauth_sessions[token.access_token] = session
        
        response_data = {
            "user": user,
            "accessToken": token.access_token
        }
        
        return JSONResponse(response_data)
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/user")
async def get_user(request: Request):
    """Get authenticated user data"""
    backend: APIServer = request.app.state.backend
    try:
        access_token = await backend.verify_auth(request)
        if access_token is None:
            raise HTTPException(status_code=401, detail="Access token is missing")
        session = backend.oauth_sessions[access_token]
        
        
        # Get user data from OAuth session
        user = await session.fetch_user()
        return {"user": user}
        
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={"detail": str(e.detail)}
        )

@router.get("/user/dashboard")
async def get_user_dashboard(request: Request):
    """Get user dashboard information"""
    backend: APIServer = request.app.state.backend
    try:
        access_token = await backend.verify_auth(request)
        if access_token is None:
            raise HTTPException(status_code=401, detail="Access token is missing")
        session = backend.oauth_sessions[access_token]
        
        # Get user data
        user = await session.fetch_user()
        
        # Get guilds
        guilds = await session.fetch_guilds()
        
        # Get user data from bot
        bot_user = await backend.client.fetch_user(int(user["id"]))
        user_data = await bot_user.get_data()
        
        dashboard_data = {
            "guildsCount": len(guilds),
            "totalMessages": user_data.total_messages,
            "commandsUsed": user_data.commands_used_count,
        }
        
        return JSONResponse(dashboard_data)
    
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={"detail": str(e.detail)}
        )

@router.get("/user/guilds")
async def get_user_guilds(request: Request):
    """Get user's guilds where the user is an admin"""
    backend: APIServer = request.app.state.backend
    try:
        access_token = await backend.verify_auth(request)
        if access_token is None:
            raise HTTPException(status_code=401, detail="Access token is missing")
        session = backend.oauth_sessions[access_token]
        
        # Get guilds from OAuth session
        guilds = await session.fetch_guilds()
        
        # Filter guilds where the user is an admin
        admin_guilds = [
            guild for guild in guilds if (int(guild["permissions"]) & 0x8) == 0x8
        ]
        
        return {"guilds": admin_guilds}
            
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={"detail": str(e.detail)}
        )

@router.get("/discord/login")
async def get_discord_login(guild_id: Optional[str] = None):
    """Get Discord OAuth2 login URL"""
    SCOPES = ["identify", "email", "guilds"]
    base_url = "https://discord.com/api/oauth2/authorize"
    params = {
        "client_id": config.oauth.client_id,
        "redirect_uri": config.oauth.redirect_url if not config.debug else config.oauth.debug_redirect_url,
        "response_type": "code",
        "scope": " ".join(SCOPES)
    }
    
    if guild_id:
        params["disable_guild_select"] = "true"
        params["guild_id"] = guild_id
    
    auth_url = f"{base_url}?{'&'.join(f'{k}={v}' for k,v in params.items())}"
    
    return RedirectResponse(url=auth_url)

@router.post("/discord/logout")
async def logout(request: Request):
    """Log out user from Discord"""
    backend: APIServer = request.app.state.backend
    try:
        access_token = request.cookies.get("accessToken")
        if not access_token:
            return JSONResponse(status_code=401, content={"detail": "Not authenticated"})

        session = backend.oauth_sessions.get(access_token)
        if session:
            await session.revoke()

        response = JSONResponse({"success": True})
        response.delete_cookie("accessToken")
        response.delete_cookie("user_id")
        return response

    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)})

@router.get("/bot/invite")
async def get_bot_invite(request: Request, guild_id: Optional[str] = None):
    """Get bot invite URL with rate limiting and caching"""
    backend: APIServer = request.app.state.backend
    cache_key = f"invite_url_{guild_id}" if guild_id else "invite_url_default"
    
    # Generate invite URL
    SCOPES = ["bot", "applications.commands"]
    PERMISSIONS = "8"  # Administrator permissions
    
    params = {
        "client_id": config.oauth.client_id,
        "permissions": PERMISSIONS,
        "scope": " ".join(SCOPES)
    }
    
    if guild_id:
        params["disable_guild_select"] = "true"
        params["guild_id"] = guild_id
        
    url = f"https://discord.com/api/oauth2/authorize?{'&'.join(f'{k}={v}' for k, v in params.items())}"

    
    return JSONResponse(
        {"message": "Redirecting to bot invite URL"},
        headers={"Location": url},
        status_code=307
    )