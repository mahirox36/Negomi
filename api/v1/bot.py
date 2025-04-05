from datetime import datetime
import platform
from fastapi import APIRouter, Request, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import psutil
from typing import TYPE_CHECKING
from modules.DiscordConfig import overwriteOwner

if TYPE_CHECKING:
    from ...classes.Other.Dashboard import DashboardCog

router = APIRouter()

@router.get("/")
async def get_users(request: Request):
    backend: DashboardCog = request.app.state.backend  # Retrieve client from FastAPI state
    if backend:
        return {"message": f"Bot is running as {backend.client.user}"}
    return {"error": "Client not available"}

@router.get("/health")
async def health_check(request: Request):
    """Check if the bot is online and ready"""
    try:
        backend = request.app.state.backend
        if not backend or not backend.client:
            raise HTTPException(status_code=503, detail="Bot is not ready")
            
        return JSONResponse({
            "status": "healthy",
            "ready": True
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)}
        )

@router.get("/commands")
async def get_commands(request: Request):
    """Get all bot commands"""
    backend: DashboardCog = request.app.state.backend
    
    return {"commands": backend.get_commands_func()}

@router.get("/stats")
async def get_stats(request: Request):
    """Get detailed bot and system statistics"""
    backend: DashboardCog = request.app.state.backend
    process = psutil.Process()
    return {
        "system": {
            "cpu_usage": round(psutil.cpu_percent(), 2),
            "memory_usage": round(process.memory_percent(), 2),
            "memory_total": psutil.virtual_memory().total,
            "python_version": platform.python_version(),
            "os": f"{platform.system()} {platform.release()}",
            "uptime": round(process.create_time(), 2),
            "thread_count": process.num_threads(),
            "disk_usage": round(psutil.disk_usage('/').percent, 2)
        },
        "bot": {
            "guild_count": len(backend.client.guilds),
            "user_count": sum(g.member_count or 0 for g in backend.client.guilds),
            "channel_count": sum(len(g.channels) for g in backend.client.guilds),
            "voice_connections": len(backend.client.voice_clients),
            "latency": round(backend.client.latency * 1000),
            "uptime": (datetime.now() - backend.startTime).total_seconds(),
            "command_count": len(backend.get_commands_func()),
            "cogs_loaded": len(backend.client.cogs),
            "current_shard": getattr(backend.client, "shard_id", 0),
            "messages_sent": 0,
            "commands_processed": 0,
            "errors_encountered": 0,
            "shard_count": backend.client.shard_count or 1,
        },
        "timestamp": datetime.now().timestamp()
    }

@router.get("/terms-and-service")
async def get_terms_and_services(request: Request):
    """Get terms and services"""
    backend: DashboardCog = request.app.state.backend
    if backend.terms_and_services:
        return backend.terms_and_services
    else:
        with open("Terms of Service.md", "r") as file:
            backend.terms_and_services = file.read()
        return backend.terms_and_services

@router.get("/privacy-policy")
async def get_privacy_policy(request: Request):
    """Get privacy policy"""
    backend: DashboardCog = request.app.state.backend
    if backend.privacy_policy:
        return backend.privacy_policy
    else:
        with open("Privacy Policy.md", "r") as file:
            backend.privacy_policy = file.read()
        return backend.privacy_policy

@router.get("/owner_pfp_url")
async def get_owner_pfp_url(request: Request):
    """Get the bot owner's profile picture URL"""
    backend: DashboardCog = request.app.state.backend
    try:
        ownerID = overwriteOwner or backend.client.owner_id
        if not isinstance(ownerID, int):
            return {"url": None}
        owner = backend.client.get_user(ownerID)
        if not owner:
            owner = await backend.client.fetch_user(ownerID)
        if owner.avatar:
            return {"url": str(owner.avatar.url)}
        else:
            return {"url": None}
    except Exception as e:
        return {"url": None}

@router.get("/pfp_url")
async def get_bot_pfp(request: Request):
    """Get the bot's profile picture URL"""
    try:
        backend = request.app.state.backend
        if not backend or not backend.client:
            raise HTTPException(status_code=503, detail="Bot is not ready")
        
        bot_user = backend.client.user
        if not bot_user:
            raise HTTPException(status_code=503, detail="Bot user not available")

        avatar_url = str(bot_user.avatar.url) if bot_user.avatar else None
        
        return JSONResponse({
            "pfp_url": avatar_url
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)}
        )

@router.post("/upload")
async def upload_image_endpoint(request: Request, file: UploadFile = File(...)):
    """Upload an image file and return its URL"""
    backend: DashboardCog = request.app.state.backend
    
    # Validate file type
    if not file.content_type or not file.content_type.startswith('image/'):
        return {"error": "Only image files are allowed", "status": 400}, 400
        
    # Read file content
    content = await file.read()
    
    # Check file size (3MB limit)
    if len(content) > 3 * 1024 * 1024:
        return {"error": "File size must be less than 3MB", "status": 400}, 400
    
    try:
        # Reset file position after reading
        await file.seek(0)
        # Upload file using the provided function
        filename = file.filename or "uploaded_file"
        url, _ = backend.upload_image(file, filename)
        return {"url": url, "status": 200}
    except Exception as e:
        return {"error": str(e), "status": 500}, 500