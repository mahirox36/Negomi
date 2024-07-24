import os
import json
from .select import Menu
# from rich import print
from .richer import Console, Table, console
class CommandNotFoundError(Exception): 
    def __init__(self, command:str):
        self.command = command
    def __str__(self):
        return f"Command not found: {self.command}"
class DuplicateCommandError(Exception): 
    def __init__(self, command):
        self.command = command
    def __str__(self):
        return f"Duplicate command found: {self.command}"
class DuplicatePluginError(Exception): 
    def __init__(self, plugin):
        self.plugin = plugin
    def __str__(self):
        return f"Duplicate plugin found: {self.plugin}"
class FailedToLoadPluginError(Exception): 
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return "Failed to load plugin: " + self.message
class FailedToUnloadPluginError(Exception): 
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return "Failed to unload plugin: " + self.message
class NoMorePluginsError(Exception): 
    def __str__(self):
        return "No more plugins to load"

commands = {}
def command():
    def decorator(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator