from __future__ import annotations

from typing import Any, Dict, Optional
from datetime import datetime
import asyncio
import logging
from fastapi import HTTPException
import subprocess
from modules.Nexon import utils

logger = logging.getLogger(__name__)


def format_error(message: str, code: Optional[int] = None) -> Dict[str, Any]:
    """Format an error response"""
    return {"detail": message, "code": code}


async def run_process(cmd: str, cwd: Optional[str] = None) -> subprocess.Popen:
    """Run a subprocess asynchronously"""
    try:
        process = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd
        )
        return process
    except Exception as e:
        logger.error(f"Failed to start process: {e}")
        raise HTTPException(status_code=500, detail="Failed to start process")


async def handle_process_output(
    process: subprocess.Popen, prefix: str = "", debug: bool = False
) -> None:
    """Handle subprocess output streams"""
    while True:
        if process.stdout:
            line = await asyncio.get_event_loop().run_in_executor(
                None, process.stdout.readline
            )
            if not line:
                break
            decoded = line.decode().strip()
            if "Warning" in decoded:
                logger.warning(f"[{prefix}] {decoded}")
            elif "[ERROR]" in decoded:
                logger.error(f"[{prefix}] {decoded}")
            elif debug:
                logger.info(f"[{prefix}] {decoded}")

        if process.stderr:
            line = await asyncio.get_event_loop().run_in_executor(
                None, process.stderr.readline
            )
            if not line:
                break
            decoded = line.decode().strip()
            logger.error(f"[{prefix}] {decoded}")


def get_uptime(start_time: datetime) -> str:
    """Calculate uptime from start time"""
    delta = utils.utcnow() - start_time
    days = delta.days
    hours = delta.seconds // 3600
    minutes = (delta.seconds // 60) % 60
    seconds = delta.seconds % 60

    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if seconds or not parts:
        parts.append(f"{seconds}s")

    return " ".join(parts)


def validate_permissions(required: list[str], provided: list[str]) -> bool:
    """Validate if provided permissions satisfy required ones"""
    return all(perm in provided for perm in required)
