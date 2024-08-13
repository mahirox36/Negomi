from datetime import datetime
import logging
import os
import nextcord
from Lib.Side import Format, Logger_Enabled


handler = None
if Logger_Enabled:
    current_datetime = datetime.now()
    date = str(current_datetime.strftime("%Y-%m-%d"))
    timed = str(current_datetime.strftime("%H-%M-%S-%f"))
    # Create a LOGGER
    Logger = logging.getLogger('nextcord')
    Logger.setLevel(logging.DEBUG)
    os.makedirs(f"logs/{date}" ,exist_ok=True)
    # Create a file handler
    handler = logging.FileHandler(f'logs/{date}/output_{timed}.log')
    handler.setLevel(logging.INFO)
    # formatter
    formatter = logging.Formatter(Format)
    handler.setFormatter(formatter)
    Logger.addHandler(handler)

class Log:
    def __init__(self) -> None:
        global Logger
        self.logger = Logger
        self.DEBUG= logging.DEBUG
        self.INFO= logging.INFO
        self.WARN= logging.WARN
        self.ERROR= logging.ERROR

    def debug(self, msg:object):
        self.logger.debug(msg)
    def info(self,msg:object):
        self.logger.info(msg)
    def warn(self, msg:object):
        self.logger.warn(msg)
    def error(self, msg:object):
        self.logger.error(msg)


LOGGER = Log()