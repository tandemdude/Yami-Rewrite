import abc
import logging

from lightbulb import plugins

from yami.subclasses.bot import Bot


class Plugin(plugins.Plugin, abc.ABC):
    def __init__(self, *, bot: Bot, logger: logging.Logger = None, name: str = None):
        super().__init__(name=name)
        self.bot = bot
        self.logger = logger or logging.getLogger(f"Yami.{self.name}")
