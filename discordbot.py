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


async def greet(channel_id=int(getenv("LOGGING_CHANNEL_ID"))):
    channel = bot.get_channel(channel_id)
    await channel.send("[INFO] もぎりん、起動しました")


@bot.event
async def on_ready():
    await greet()


@bot.command()
async def ping(ctx):
    await ctx.send("pong")


token = getenv("DISCORD_BOT_TOKEN")
bot.run(token)
