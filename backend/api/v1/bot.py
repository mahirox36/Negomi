from datetime import datetime
import platform
from fastapi import APIRouter, Request, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import psutil
from typing import TYPE_CHECKING, Optional
from modules.DiscordConfig import overwriteOwner
from nexon.data.models import Feature, MetricsCollector
from modules.Nexon import aio_open
import base64
import time
import logging
import asyncio
import io
from modules.Nexon import utils

if TYPE_CHECKING:
    from classes.Features.Welcome import Welcome
    from backend.apiManager import APIServer

router = APIRouter(tags=["bot"])

terms_and_services: Optional[str] = ""
privacy_policy: Optional[str] = ""

logger = logging.getLogger(__name__)


@router.get("/")
async def get_users(request: Request):
    backend: APIServer = request.app.state.backend  # Retrieve client from FastAPI state
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

        return JSONResponse({"status": "healthy", "ready": True})
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})


@router.get("/commands")
async def get_commands(request: Request):
    """Get all bot commands"""
    backend: APIServer = request.app.state.backend

    return await backend.get_commands_of_bot()


@router.get("/stats")
async def get_stats(request: Request):
    """Get detailed bot and system statistics"""
    backend: APIServer = request.app.state.backend
    process = psutil.Process()

    # Get real historical data from MetricsCollector
    historical_data = await MetricsCollector.get_historical_data(hours=24)

    return {
        "system": {
            "cpu_usage": round(psutil.cpu_percent(), 2),
            "memory_usage": round(process.memory_percent(), 2),
            "memory_total": psutil.virtual_memory().total,
            "python_version": platform.python_version(),
            "os": f"{platform.system()} {platform.release()}",
            "uptime": round(process.create_time(), 2),
            "thread_count": process.num_threads(),
            "disk_usage": round(psutil.disk_usage("/").percent, 2),
            "historical_cpu": historical_data["cpu_usage"][-10:],  # Last 10 data points
            "historical_memory": historical_data["memory_usage"][
                -10:
            ],  # Last 10 data points
        },
        "bot": {
            "guild_count": len(backend.client.guilds),
            "user_count": sum(g.member_count or 0 for g in backend.client.guilds),
            "channel_count": sum(len(g.channels) for g in backend.client.guilds),
            "voice_connections": len(backend.client.voice_clients),
            "latency": round(backend.client.latency * 1000),
            "uptime": (utils.utcnow() - backend.start_time).total_seconds(),
            "command_count": len(await backend.get_commands_of_bot()),
            "cogs_loaded": len(backend.client.cogs),
            "current_shard": getattr(backend.client, "shard_id", 0),
            "messages_sent": (
                historical_data["messages_sent"][-1]
                if historical_data["messages_sent"]
                else 0
            ),
            "commands_processed": (
                historical_data["commands_processed"][-1]
                if historical_data["commands_processed"]
                else 0
            ),
            "errors_encountered": 0,
            "shard_count": backend.client.shard_count or 1,
            "historical_stats": {
                "timestamps": historical_data["timestamps"][-10:],
                "messages": historical_data["messages_sent"][-10:],
                "commands": historical_data["commands_processed"][-10:],
                "users": historical_data["user_count"][-10:],
                "latency": historical_data["bot_latency"][-10:],
            },
        },
        "timestamp": utils.utcnow().timestamp(),
    }


@router.get("/terms-and-service")
async def get_terms_and_services(request: Request):
    """Get terms and services"""
    global terms_and_services
    if terms_and_services:
        return terms_and_services
    else:
        async with aio_open("Terms of Service.md", "r") as file:
            # exclude the first line
            terms_and_services = "\n".join((await file.read()).splitlines()[2:])
        return terms_and_services


@router.get("/privacy-policy")
async def get_privacy_policy(request: Request):
    """Get privacy policy"""
    global privacy_policy
    if privacy_policy:
        return privacy_policy
    else:
        async with aio_open("Privacy Policy.md", "r") as file:
            privacy_policy = "\n".join((await file.read()).splitlines()[2:])
        return privacy_policy


@router.get("/owner_pfp_url")
async def get_owner_pfp_url(request: Request):
    """Get the bot owner's profile picture URL"""
    backend: APIServer = request.app.state.backend
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

        return JSONResponse({"pfp_url": avatar_url})
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})


@router.post("/upload")
async def upload_image_endpoint(request: Request, file: UploadFile = File(...)):
    """Upload an image file and return its URL"""
    backend: APIServer = request.app.state.backend
    
    try:
        # Validate file existence
        if not file or not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Validate file type
        allowed_types = {"image/jpeg", "image/png", "image/gif", "image/webp"}
        if not file.content_type or file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed types: {', '.join(allowed_types)}",
            )
        
        file.file.seek(0, 2)
        file_size =  file.file.tell()
        await file.seek(0)
        
        if file_size > 3 * 1024 * 1024:  # 3MB limit
            raise HTTPException(
                status_code=400, detail="File size must be less than 3MB"
            )
        
        # Generate safe filename
        original_filename = file.filename
        safe_filename = "".join(
            c for c in original_filename if c.isalnum() or c in "._-"
        )
        
        # Upload file directly
        url, internal_url = await backend.storage.upload_file(file, "uploads/")
        
        if not url:
            raise HTTPException(status_code=500, detail="Failed to generate upload URL")
        
        return JSONResponse(
            {
                "success": True,
                "data": {
                    "url": url,
                    "filename": safe_filename,
                    "size": file_size,
                    "type": file.content_type,
                },
            }
        )
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Failed to upload file. Please try again later."
        )


@router.post("/upload-welcome-background")
async def upload_welcome_background(request: Request, file: UploadFile = File(...)):
    """Upload a welcome background image and return its URL"""
    backend: APIServer = request.app.state.backend

    try:
        # Validate file existence
        if not file:
            raise HTTPException(status_code=400, detail="No file provided")

        # Validate file type
        allowed_types = {"image/jpeg", "image/png", "image/gif", "image/webp"}
        if not file.content_type or file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed types: {', '.join(allowed_types)}",
            )

        # Process file content in smaller chunks to prevent blocking
        content = bytearray()
        chunk_size = 64 * 1024  # 64KB chunks

        while True:
            chunk = await file.read(chunk_size)
            if not chunk:
                break
            content.extend(chunk)

            # Allow other coroutines to run between chunks
            await asyncio.sleep(0)

        # Check file size (5MB limit)
        if len(content) > 5 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
            )
        # Create a new file-like object with the content
        file_obj = io.BytesIO(content)
        file_obj.name = file.filename

        # Validate file name
        original_filename = file.filename or "background"
        safe_filename = "".join(
            c for c in original_filename if c.isalnum() or c in "._-"
        )
        filename = f"welcome_bg_{int(time.time())}_{safe_filename}"

        # Wrap BytesIO in UploadFile
        upload_file = UploadFile(filename=filename, file=file_obj)

        # Upload file
        url, metadata = await backend.storage.upload_file(upload_file, filename)

        if not url:
            raise HTTPException(status_code=500, detail="Failed to generate upload URL")

        if not url:
            raise HTTPException(status_code=500, detail="Failed to generate upload URL")

        return JSONResponse(
            {
                "success": True,
                "data": {
                    "url": url,
                    "filename": filename,
                    "size": len(content),
                    "type": file.content_type,
                    "metadata": metadata,
                },
            }
        )

    except HTTPException as he:
        # Re-raise HTTP exceptions as-is
        raise he
    except Exception as e:
        logger.error(f"Error uploading welcome background: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Failed to upload image. Please try again later."
        )


@router.get("/command-stats")
async def get_command_stats(request: Request):
    """Get command usage statistics"""
    backend: APIServer = request.app.state.backend
    stats = {}

    # Get all users' command usage data
    from nexon.data.models import UserData

    users = await UserData.all()

    # Aggregate command usage across all users
    for user in users:
        for cmd, count in user.favorites_commands.items():
            if cmd not in stats:
                stats[cmd] = 0
            stats[cmd] += count

            # Add timestamp of last use if available
            if user.last_command_use and user.last_command_use.get(cmd):
                stats[f"{cmd}_last_used"] = user.last_command_use[cmd]

    return stats


@router.post("/track-command")
async def track_command_usage(request: Request):
    """Track command usage"""
    backend: APIServer = request.app.state.backend
    data = await request.json()

    command_name = data.get("command")
    user_id = data.get("user_id")

    if not command_name or not user_id:
        raise HTTPException(status_code=400, detail="Missing command or user_id")

    try:
        from nexon.data.models import UserData

        user = await UserData.get(id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Update command usage
        if not hasattr(user, "favorites_commands"):
            user.favorites_commands = {}
        if not hasattr(user, "last_command_use"):
            user.last_command_use = {}

        user.favorites_commands[command_name] = (
            user.favorites_commands.get(command_name, 0) + 1
        )
        user.last_command_use[command_name] = utils.utcnow().timestamp()

        await user.save()
        return {"success": True}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
