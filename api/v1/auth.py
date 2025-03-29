from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from typing import TYPE_CHECKING, Optional
from .baseModels import *
from modules.DiscordConfig import config

if TYPE_CHECKING:
    from ...classes.Other.Dashboard import DashboardCog

router = APIRouter()

@router.post("/discord/callback")
async def discord_callback(request: Request,data: DiscordCallbackRequest):
    backend: DashboardCog = request.app.state.backend
    try:
        code = data.code
        
        # Check cache first
        if code in backend.token_cache:
            return JSONResponse(backend.token_cache[code])
        
        oauth_data = {
            "client_id": config.oauth.client_id,
            "client_secret": config.oauth.client_secret,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": config.oauth.redirect_url if not config.debug else config.oauth.debug_redirect_url,
        }
        
        session = await backend.get_session()
        async with session.post(
            "https://discord.com/api/oauth2/token",
            data=oauth_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        ) as response:
            if response.status != 200:
                error_data = await response.json()
                raise HTTPException(
                    status_code=response.status,
                    detail=f"Discord auth failed: {error_data.get('error_description', 'Unknown error')}"
                )
            
            tokens = await response.json()
            access_token = tokens["access_token"]
            
            # Get user data
            user = await backend.rate_limited_request(
                "/users/@me",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            response_data = {
                "user": user,
                "accessToken": access_token
            }
            
            # Cache the response
            backend.token_cache[code] = response_data
            backend.user_cache[access_token] = user
            
            return JSONResponse(response_data)
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/user")
async def get_user(request: Request):
    """Get authenticated user data"""
    backend: DashboardCog = request.app.state.backend
    try:
        access_token = await backend.verify_auth(request)
        
        # Return cached user data if available
        if access_token in backend.user_cache:
            return {"user": backend.user_cache[access_token]}
        
        # Should never reach here due to verify_auth, but just in case
        raise HTTPException(status_code=401, detail="Not authenticated")
        
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={"detail": str(e.detail)}
        )

@router.get("/user/guilds")
async def get_user_guilds(request: Request):
    """Get user's guilds"""
    backend: DashboardCog = request.app.state.backend
    try:
        access_token = await backend.verify_auth(request)
        
        session = await backend.get_session()
        async with session.get(
            "https://discord.com/api/users/@me/guilds",
            headers={"Authorization": f"Bearer {access_token}"}
        ) as response:
            if response.status != 200:
                raise HTTPException(
                    status_code=response.status,
                    detail="Failed to fetch guild information"
                )
                
            guilds = await response.json()
            return {"guilds": guilds}
            
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
        params["guild_id"] = guild_id
    
    auth_url = f"{base_url}?{'&'.join(f'{k}={v}' for k,v in params.items())}"
    
    return RedirectResponse(url=auth_url)
@router.post("/discord/logout")
async def logout(request: Request):
    """Log out user from Discord"""
    backend: DashboardCog = request.app.state.backend
    try:
        access_token = request.cookies.get("accessToken")
        if not access_token:
            return JSONResponse(status_code=401, content={"detail": "Not authenticated"})

        session = await backend.get_session()
        async with session.post(
            "https://discord.com/api/oauth2/token/revoke",
            data={
                "token": access_token,
                "client_id": config.oauth.client_id,
                "client_secret": config.oauth.client_secret,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        ) as response:
            if response.status != 200:
                backend.logger.error(f"Failed to revoke token: {await response.text()}")

        # Clear caches regardless of revoke success
        if access_token in backend.user_cache:
            del backend.user_cache[access_token]

        response = JSONResponse({"success": True})
        response.delete_cookie("accessToken")
        response.delete_cookie("user_id")
        return response

    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)})

@router.get("/bot/invite")
async def get_bot_invite(request: Request, guild_id: Optional[str] = None):
    """Get bot invite URL with rate limiting and caching"""
    backend: DashboardCog = request.app.state.backend
    cache_key = f"invite_url_{guild_id}" if guild_id else "invite_url_default"
    
    # Check cache
    if cache_key in backend.invite_url_cache:
        return {"url": backend.invite_url_cache[cache_key]}
    
    # Generate invite URL
    SCOPES = ["bot", "applications.commands"]
    PERMISSIONS = "8"  # Administrator permissions
    
    params = {
        "client_id": config.oauth.client_id,
        "permissions": PERMISSIONS,
        "scope": " ".join(SCOPES)
    }
    
    if guild_id:
        params["guild_id"] = guild_id
        
    url = f"https://discord.com/api/oauth2/authorize?{'&'.join(f'{k}={v}' for k, v in params.items())}"
    
    # Cache the URL
    backend.invite_url_cache[cache_key] = url
    
    return JSONResponse(
        {"message": "Redirecting to bot invite URL"},
        headers={"Location": url},
        status_code=307
    )