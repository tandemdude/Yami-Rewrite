import logging
import os

from hikari import ShardReadyEvent
from lightbulb import Bot as lightBot
from lightbulb.errors import ExtensionAlreadyLoaded, ExtensionError


class Bot(lightBot):
    def __init__(self, prefix, *args, **kwargs):
        super().__init__(*args, prefix=prefix, **kwargs)
        self.logger = logging.getLogger("Yami")
        self.dispatcher.subscribe(ShardReadyEvent, self.on_ready)

    def load_and_reload_extensions(self):
        for plugin in filter(lambda f: f.endswith(".py"), os.listdir("plugins")):
            plugin = f"yami.plugins.{plugin[:-3]}"
            try:
                self.load_extension(plugin)
                self.logger.info("loaded %s", plugin)
            except ExtensionAlreadyLoaded:
                self.reload_extension(plugin)
                self.logger.info("reloaded %s", plugin)
            except ExtensionError:
                self.logger.error("Failed to load %s", plugin)

    async def on_ready(self, event=ShardReadyEvent):
        pass
