import typing

from lightbulb import Command, Group, WrappedArg
from lightbulb.errors import ConverterFailure

from yami.subclasses.plugin import Plugin


async def pluginish_converter(arg: WrappedArg) -> typing.Union[Plugin, Group, Command]:
    pluginish = arg.context.bot.get_plugin(arg.data) or arg.context.bot.get_command(
        arg.data
    )
    if not pluginish:
        raise ConverterFailure(f"Failed to get plugin or command with arg {arg}")
    return pluginish


if typing.TYPE_CHECKING:
    pluginish_converter = typing.Union[Plugin, Group, Command]
