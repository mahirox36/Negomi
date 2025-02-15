from fastapi import FastAPI, Request
import uvicorn
from nextcord.ext import ipc
import asyncio
from modules.Nexon import logger

class Dashboard:
    def __init__(self):
        self.app = FastAPI()
        self.logger = logger
        self.ipc = ipc.Client(
            port=8765
        )
        
        # Setup routes
        self.setup_routes()

    def setup_routes(self):
        @self.app.get("/get_all_commands")
        async def get_all_commands(request: Request):
            stats = await self.ipc.request("get_commands")
            return stats
        @self.app.get("/get_detailed_stats")
        async def get_all_commands(request: Request):
            stats = await self.ipc.request("get_detailed_stats")
            return stats

    async def start(self):
        """Start the dashboard"""
        self.logger.info("Starting web dashboard...")

        # Start npm process
        npm_process = await asyncio.create_subprocess_shell(
            "cd Dashboard/web && npm run dev",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        # Start FastAPI server
        config = uvicorn.Config(
            app=self.app,
            host="127.0.0.1",
            log_config=None,
            port=25400,
        )
        server = uvicorn.Server(config)
        
        try:
            # Run both the npm process and FastAPI server
            self.logger.info("Web dashboard started.")
            await asyncio.gather(
                server.serve(),
                npm_process.communicate()
            )
        except Exception as e:
            self.logger.error(f"Error starting dashboard: {e}")
            if npm_process.returncode is None:
                npm_process.terminate()
            raise


def run_dashboard():
    """Helper function to run dashboard in separate process"""
    dashboard = Dashboard()
    asyncio.run(dashboard.start())

if __name__ == "__main__":
    run_dashboard()