from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
import uvicorn
from nextcord.ext import ipc
import asyncio
from modules.Nexon import logger, BotConfig

class Dashboard:
    def __init__(self):
        self.app = FastAPI()
        self.logger = logger
        self.ipc = ipc.Client(
            secret_key=BotConfig.IPC.secret,
            port=BotConfig.IPC.port or 25401
        )
        
        # Setup routes
        self.app.mount("/static", StaticFiles(directory="Dashboard/web/static"), name="static")
        self.templates = Jinja2Templates(directory="Dashboard/web")
        self.setup_routes()

    def setup_routes(self):
        @self.app.get("/")
        async def home(request: Request):
            try:
                stats = await self.ipc.request("get_bot_stats")
                return self.templates.TemplateResponse(
                    "index.html", 
                    {"request": request, "stats": stats}
                )
            except Exception as e:
                self.logger.error(f"Dashboard error: {str(e)}")
                return {"error": "Failed to load dashboard"}

        @self.app.get("/commands")
        async def about(request: Request):
            try:
                stats = await self.ipc.request("get_commands")
                return self.templates.TemplateResponse(
                    "commands.html", 
                    {"request": request, "stats": stats}
                )
            except Exception as e:
                self.logger.error(f"Dashboard error: {str(e)}")
                return {"error": "Failed to load dashboard"}

    async def start(self):
        """Start the dashboard"""
        config = uvicorn.Config(
            self.app,
            host=BotConfig.Dashboard.host or "0.0.0.0",
            port=BotConfig.Dashboard.port or 25400,
            log_config=None  # Disable uvicorn's logging
        )
        server = uvicorn.Server(config)
        
        self.logger.info(f"Starting dashboard on http://{config.host if not "0.0.0.0" else "127.0.0.1"}:{config.port}")
        await server.serve()

def run_dashboard():
    """Helper function to run dashboard in separate process"""
    dashboard = Dashboard()
    asyncio.run(dashboard.start())

if __name__ == "__main__":
    run_dashboard()