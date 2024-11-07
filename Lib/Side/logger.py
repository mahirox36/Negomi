"""Setup Rich logging with proper formatting"""
import logging
from rich.logging import RichHandler
from ..richer import console
class InfoAndErrorFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        # Allow only INFO and ERROR level messages
        return record.levelno in (logging.INFO, logging.ERROR)
richHandler = RichHandler(logging.INFO,rich_tracebacks=True,console=console)
richHandler.addFilter(InfoAndErrorFilter())
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[richHandler]
)
logger = logging.getLogger("discord_bot")
def print(string: str):
    logger.info(string)