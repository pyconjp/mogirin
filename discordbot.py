from os import getenv
from traceback import TracebackException

from discord.ext import commands

bot = commands.Bot(command_prefix="/")


@bot.event
async def on_command_error(ctx, error):
    original_error = getattr(error, "original", error)
    error_message = "".join(
        TracebackException.from_exception(original_error).format()
    )
    await ctx.send(error_message)


@bot.command()
async def ping(ctx):
    await ctx.send("pong")


token = getenv("DISCORD_BOT_TOKEN")
bot.run(token)
