"""Setup Rich logging with proper formatting and non-blocking command input"""
from datetime import datetime
import logging
import os
import sys
import threading
import queue
from typing import Dict, List, Optional, Callable
from rich.logging import RichHandler
from rich.console import Console
from rich.theme import Theme
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import HTML
from .config import Format, colors, Level, reload_config
from .other import is_executable

class CommandLineInterface:
    def __init__(self, commands: List[str] = None, command_handler: Optional[Callable] = None):
        """
        Initialize CLI with optional command suggestions and handler
        
        Args:
            commands (List[str]): List of command suggestions
            command_handler (Callable): Function to handle commands
        """
        self.commands = commands or ["help", "exit", "status", "clear"]
        self.completer = WordCompleter(self.commands, ignore_case=True)
        self.command_queue = queue.Queue()
        self.running = True
        self.command_handler = command_handler
        
        # Configure prompt style
        self.style = Style.from_dict({
            'prompt': '#00b4eb bold',  # Cyan color for prompt
            'command': '#ffffff',      # White color for command text
        })
        
        # Create prompt session with styled prompt
        self.session = PromptSession(
            message=lambda: HTML('<ansiblue>►</ansiblue> '),  # Using a small arrow as prompt
            history=InMemoryHistory(),
            complete_in_thread=True,
            style=self.style,
            refresh_interval=0.1,
            complete_while_typing=True,
        )
        
        # Start input thread
        self.input_thread = threading.Thread(target=self._input_loop, daemon=True)
        self.input_thread.start()

    def _input_loop(self):
        """Background thread for handling input"""
        with patch_stdout(raw=True):  # raw=True helps prevent interference with Rich
            while self.running:
                try:
                    command = self.session.prompt(
                        completer=self.completer,
                    )
                    
                    if command.lower() == "exit":
                        self.running = False
                    
                    if self.command_handler:
                        self.command_handler(command)
                    else:
                        self.command_queue.put(command)
                        
                except (KeyboardInterrupt, EOFError):
                    self.running = False
                    break
                except Exception as e:
                    logger.error(f"Input error: {e}")

    def get_command(self) -> Optional[str]:
        """
        Non-blocking method to get the next command
        
        Returns:
            Optional[str]: Command if available, None otherwise
        """
        try:
            return self.command_queue.get_nowait()
        except queue.Empty:
            return None

    def stop(self):
        """Stop the input loop"""
        self.running = False

def setup_logger(names: list[str] = ["negomi", "nextcord"], level: int = logging.INFO) -> Dict[str, logging.Logger]:
    """
    Set up comprehensive loggers with Rich formatting and file logging
    
    Args:
        names (list): List of logger names
        level (int): Logging level (default: logging.INFO)
    
    Returns:
        dict: Dictionary of configured logger instances
    """
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

    loggers = {}
    for name in names:
        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.handlers.clear()
        
        logger.addHandler(rich_handler)
        logger.addHandler(file_handler)
        logger.propagate = False
        
        loggers[name] = logger

    return loggers

# Create logger instances
Level = Level.lower()
if Level.startswith("n"): Level = logging.NOTSET
elif Level.startswith("d"): Level = logging.DEBUG
elif Level.startswith("i"): Level = logging.INFO
elif Level.startswith("w"): Level = logging.WARNING
elif Level.startswith("e"): Level = logging.ERROR
elif Level.startswith("c"): Level = logging.CRITICAL
else: Level = logging.INFO
loggers = setup_logger(level=Level)
logger = loggers['negomi']
nextcord_logger = loggers['nextcord']

def print(string: str, logger_instance=None):
    """
    Custom print method that logs messages
    
    Args:
        string (str): Message to log
        logger_instance (logging.Logger, optional): Specific logger to use. Defaults to negomi logger.
    """
    (logger_instance or logger).info(string)

# Example usage:

def handle_command(cmd: str):
    if not cmd.strip():  # Ignore empty commands
        return
        
    cmd = cmd.lower()
    if cmd == "clear":
        os.system('cls' if os.name == 'nt' else 'clear')
    elif cmd == "help":
        logger.info("Available commands:")
        logger.info("   help    - Show this help message")
        logger.info("   reload  - reload all the config vars")
        logger.info("   clear   - Clear console")
    elif cmd == "reload":
        if reload_config():
            logger.info("Configuration reloaded successfully")
            logger.warning(f"Some Vars only will reloaded when the {"app" if is_executable() else "Script"} restart")
        else:
            logger.error("Failed to reload configuration")
    else:
        logger.error(f"{cmd} Not Found")

cli = CommandLineInterface(
    # Add disable AI temp
        commands=["help", "clear", "reload"],
        command_handler=handle_command
    )