import logging
import os
import typing

import lightbulb
import hikari
from hikari import Message, UnauthorizedError

from yami.subclasses.bot import Bot


async def get_prefix(bot: Bot, message: Message) -> typing.List[str]:
    prefixes = []
    if message.guild_id:
        bot.logger.warn("per-guild prefixes are not implemented yet.")
    else:
        prefixes.append("yr.")
    return lightbulb.when_mentioned_or(prefixes)


def run_bot(token, logger):
    bot = Bot(
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
