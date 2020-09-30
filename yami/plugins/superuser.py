import asyncio
import inspect
from datetime import datetime, timezone
from random import randint

import hikari
from lightbulb import Context, WrappedArg, checks, commands, text_channel_converter
from lightbulb.errors import NotOwner
from lightbulb.utils import EmbedNavigator, EmbedPaginator

from yami.subclasses.bot import Bot
from yami.subclasses.plugin import Plugin
from yami.utils.converters import code_converter, pluginish_converter


class SuperUser(Plugin):
    def __init__(self, *, bot: Bot):
        super().__init__(bot=bot)

    # noinspection PyProtectedMember
    async def plugin_check(self, context: Context) -> bool:
        try:
            await checks._owner_only(context)
        except NotOwner:
            return False
        return True

    @checks.owner_only()
    @commands.command(aliases=["exec", "evaluate", "eval", "sh", "shell"])
    async def execute(self, context: Context, *, body: code_converter):
        await body.run()

        def check(e: hikari.MessageUpdateEvent):
            return (
                e.message.id == context.message.id
                and e.message.content != context.message.content
            )

        try:
            event = await self.bot.wait_for(
                hikari.MessageUpdateEvent, timeout=60.0, predicate=check
            )
            message = await self.bot.rest.fetch_message(
                event.channel_id, event.message_id
            )
            message.guild_id = context.guild_id
            command_context = Context(
                self.bot, message, context.prefix, context.invoked_with, context.command
            )
            await context.command.invoke(
                command_context, body=message.content.lstrip(context.prefix)
            )

            channel: hikari.TextChannel = await text_channel_converter(
                WrappedArg(f"{context.channel_id}", context)
            )
            history = (
                channel.history(after=context.message_id)
                .filter(lambda m: m.author.id == self.bot.me.id)
                .take_until(lambda m: m.id < context.message.id)
            )
            await self.bot.rest.delete_messages(channel, *(await history))
        except (hikari.ForbiddenError, hikari.NotFoundError):
            pass
        except asyncio.TimeoutError:
            pass

    @checks.owner_only()
    @commands.command(aliases=["p"])
    async def panic(self, context: Context):
        m = await context.reply("Panicking...")
        self.bot.unload_extension("Yami.plugins.superuser")
        self.logger.info("Panicked, unloaded.")
        await m.edit("Panicked")

    @checks.owner_only()
    @commands.command(aliases=["rst"])
    async def restart(self, context: Context):
        await context.reply("Ja, matane")
        asyncio.create_task(self.bot.close())

    @checks.owner_only()
    @commands.command(aliases=["showcode", "codefor", "code", "source"])
    async def getcode(self, context: Context, child: pluginish_converter):
        # noinspection PyProtectedMember
        body = (
            inspect.getsource(child.__class__)
            if isinstance(child, Plugin)
            else inspect.getsource(child._callback)
        )
        paginator = EmbedPaginator(prefix="```py\n", suffix="```", max_lines=20)

        @paginator.embed_factory()
        def make_embed(index, page):
            return hikari.Embed(
                title=f"Code for {child.name}",
                description=page,
                colour=randint(0, 0xFFF),
                timestamp=datetime.now(tz=timezone.utc),
            ).set_footer(
                text=f"{index}/{len(paginator)}",
                icon=context.author.avatar_url,
            )

        paginator.add_line(body.replace("`", "ˋ"))
        navigator = EmbedNavigator(paginator.build_pages())
        await navigator.run(context)

    @checks.owner_only()
    @commands.command(name="selfclean", aliases=["sclean", "sclear"])
    async def self_clean(self, context: Context, amount: int = 30):
        # noinspection PyTypeChecker
        channel: hikari.TextChannel = context.bot.cache.get_guild_channel(
            context.channel_id
        ) or await context.bot.rest.fetch_channel(context.channel_id)

        history = (
            channel.history(before=context.message_id)
            .filter(lambda m: m.author.id == context.bot.me.id)
            .limit(amount)
        )

        if not isinstance(channel, hikari.DMChannel):
            await self.bot.rest.delete_messages(channel, *(await history))
        else:
            async for message in history:
                await message.delete()


def load(bot):
    bot.add_plugin(SuperUser(bot=bot))


def unload(bot):
    bot.remove_plugin("SuperUser")
