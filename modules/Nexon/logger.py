"""Setup Rich logging with proper formatting"""
from datetime import datetime
import logging
import os
import sys
from typing import Dict, List
from rich.logging import RichHandler
from rich.console import Console
from .config import Format
class InfoAndErrorFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        # Allow only INFO and ERROR level messages
        return record.levelno in (logging.INFO, logging.ERROR, logging.DEBUG)

def setup_logger(names: list[str] = ["negomi", "nextcord"], level: int = logging.INFO) -> Dict[str, logging.Logger]:
    """
    Set up comprehensive loggers with Rich formatting and file logging
    
    Args:
        names (list): List of logger names
        level (int): Logging level (default: logging.INFO)
    
    Returns:
        dict: Dictionary of configured logger instances
    """
    # Create console and datetime variables
    console = Console()
    current_datetime = datetime.now()
    date = current_datetime.strftime("%Y-%m-%d")
    timed = current_datetime.strftime("%H-%M-%S-%f")

    # Create log directory
    os.makedirs(f"logs/{date}/", exist_ok=True)

    # Rich console handler with filter
    rich_handler = RichHandler(
        markup=True,
        level=logging.INFO, 
        rich_tracebacks=True, 
        console=console,
    )
    rich_handler.addFilter(InfoAndErrorFilter())
    
    # File handler
    file_handler = logging.FileHandler(f'logs/{date}/output_{timed}.log',encoding="utf-8'")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(Format, datefmt="[%X]"))

    # Create loggers
    loggers = {}
    for name in names:
        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.handlers.clear()  # Clear any existing handlers

        
        # Add handlers
        logger.addHandler(rich_handler)
        logger.addHandler(file_handler)

        # Prevent propagation of log messages to parent loggers
        logger.propagate = False
        
        loggers[name] = logger

    return loggers

# Create logger instances
loggers = setup_logger()
logger = loggers['negomi']
nextcord_logger = loggers['nextcord']

def print(string: str, logger=None):
    """
    Custom print method that logs messages
    
    Args:
        string (str): Message to log
        logger (logging.Logger, optional): Specific logger to use. Defaults to negomi logger.
    """
    (logger or logger).info(string)