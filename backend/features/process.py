from __future__ import annotations

from typing import Optional
import asyncio
import logging
import subprocess
from .utils import run_process, handle_process_output

logger = logging.getLogger(__name__)


class ProcessManager:
    """Manages frontend development server process"""

    def __init__(self, debug: bool = False) -> None:
        self.debug = debug
        self.npm_process: Optional[subprocess.Popen] = None
        self.npm_command = "npm run dev" if debug else "npm run start"

    async def start_frontend(self, frontend_dir: str = "Dashboard") -> None:
        """Start the frontend development server"""
        if self.npm_process:
            logger.warning("Frontend server already running")
            return

        try:
            self.npm_process = await run_process(
                cmd=f"cd {frontend_dir} && {self.npm_command}", cwd=None
            )

            # Handle process output
            asyncio.create_task(
                handle_process_output(self.npm_process, prefix="NPM", debug=self.debug)
            )

            logger.info("Frontend development server started")

        except Exception as e:
            logger.error(f"Failed to start frontend server: {str(e)}")
            if self.npm_process:
                self.npm_process.terminate()
                self.npm_process = None
            raise

    async def stop_frontend(self) -> None:
        """Stop the frontend development server"""
        if self.npm_process:
            try:
                self.npm_process.terminate()
                self.npm_process = None
                logger.info("Frontend development server stopped")
            except Exception as e:
                logger.error(f"Error stopping frontend server: {str(e)}")

    async def cleanup(self) -> None:
        """Clean up resources"""
        await self.stop_frontend()
