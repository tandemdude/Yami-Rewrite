import logging
import os
import typing

import hikari
from hikari import Message, UnauthorizedError

from yami.subclasses.bot import Yami


async def get_prefix(bot: Yami, message: Message) -> typing.List[str]:
    prefixes = [bot.me.mention, bot.me.mention + " "]
    if message.guild_id:
        bot.logger.warn("per-guild prefixes are not implemented yet.")
    else:
        prefixes.append("bb.")
    return prefixes


def run_bot(token, logger):
    bot = Yami(
        prefix=get_prefix,
        token=token,
        insensitive_commands=True,
        force_color=True,
        logs=logging.WARNING,
        intents=hikari.Intents.ALL,
    )
    logger.setLevel(logging.INFO)
    bot.load_and_reload_extensions()
    bot.run()


def main():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)
    logger = logging.getLogger("Yami")

    try:
        if token := os.getenv("YAMI_TOKEN"):
            run_bot(token, logger)
        else:
            token = input("Please input a token. ")
            run_bot(token, logger)
    except UnauthorizedError:
        raise ValueError("The provided token is invalid.")
