"""Setup Rich logging with proper formatting"""
from datetime import datetime
import logging
import os
from rich.logging import RichHandler
from ..richer import console
class InfoAndErrorFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        # Allow only INFO and ERROR level messages
            
        return record.levelno in (logging.INFO, logging.ERROR)

current_datetime = datetime.now()
date = str(current_datetime.strftime("%Y-%m-%d"))
timed = str(current_datetime.strftime("%H-%M-%S-%f"))

richHandler = RichHandler(logging.INFO,rich_tracebacks=True,console=console)
richHandler.addFilter(InfoAndErrorFilter())
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[richHandler]
)
logger = logging.getLogger("discord_bot")

os.makedirs(f"logs/{date}/", exist_ok=True)

handler = logging.FileHandler(f'logs/{date}/output_{timed}.log')
handler.setLevel(logging.INFO)
logger.addHandler(handler)
def print(string: str):
    logger.info(string)