from fastapi import APIRouter
from . import admin, auth, baseModels, bot, guilds, layout

router = APIRouter(prefix="/api/v1")

router.include_router(auth.router, prefix="/auth")
router.include_router(guilds.router, prefix="/guilds")
router.include_router(admin.router, prefix="/admin")
router.include_router(layout.router, prefix="/layout")
router.include_router(bot.router, prefix="/bot")

__all__ = ["router"]