"""Setup Rich logging with proper formatting and non-blocking command input"""
from datetime import datetime
import logging
import os
from typing import Dict
from rich.logging import RichHandler
from rich.console import Console
from rich.theme import Theme
from .config import Format, colors, Level



def setup_logger(names: list[str] = ["negomi", "nexon"], level: int = logging.INFO) -> tuple[logging.Logger, logging.Logger]:
    """
    Set up comprehensive loggers with Rich formatting and file logging
    
    Args:
        names (list): List of logger names
        level (int): Logging level (default: logging.INFO)
    
    Returns:
        dict: Dictionary of configured logger instances
    """
    global Level
    Level = Level.lower()
    if Level.startswith("n"): Level = logging.NOTSET
    elif Level.startswith("d"): Level = logging.DEBUG
    elif Level.startswith("i"): Level = logging.INFO
    elif Level.startswith("w"): Level = logging.WARNING
    elif Level.startswith("e"): Level = logging.ERROR
    elif Level.startswith("c"): Level = logging.CRITICAL
    else: Level = logging.INFO
    # Create custom theme for Rich
    custom_theme = Theme({
        "logging.level.debug": f"{colors.Debug}",
        "logging.level.info": f"{colors.Info}",
        "logging.level.warning": f"{colors.Warn}",
        "logging.level.error": f"{colors.Error}",
        "logging.level.critical": f"{colors.Error} bold",
    })
    
    console = Console(theme=custom_theme, force_terminal=True)
    current_datetime = datetime.now()
    date = current_datetime.strftime("%Y-%m-%d")
    timed = current_datetime.strftime("%H-%M-%S-%f")

    os.makedirs(f"logs/{date}/", exist_ok=True)

    rich_handler = RichHandler(
        console=console,
        markup=True,
        rich_tracebacks=True,
        level=level,
    )
    
    file_handler = logging.FileHandler(f'logs/{date}/output_{timed}.log', encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(Format, datefmt="[%X]"))

    loggers: Dict[str, logging.Logger] = {}
    for name in names:
        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.handlers.clear()
        
        logger.addHandler(rich_handler)
        logger.addHandler(file_handler)
        logger.propagate = False
        
        loggers[name] = logger

    return (loggers["negomi"], loggers['nexon'])

logger, nextcord_logger = setup_logger()

def print(string: str, logger_instance=None):
    """
    Custom print method that logs messages
    
    Args:
        string (str): Message to log
        logger_instance (logging.Logger, optional): Specific logger to use. Defaults to negomi logger.
    """
    (logger_instance or logger).info(string)