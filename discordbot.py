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


def collect_ticket(ticket_number: str):
    return "Hello"


@bot.event
async def on_message(message):
    # TODO: もぎり用チャンネルでなければ早期リターンする（もぎり用チャンネルはまだない）

    if bot.user not in message.mentions:
        return

    # TODO: 正規表現で最初に見つけた数字にするとより簡潔に書けそう
    ticket_number = message.content.split()[1]
    if not ticket_number.isnumeric():
        reply_message = (
            f"{message.author.mention} ValueError: "
            f"invalid ticket number {ticket_number!r}\n"
            "Please input numeric ticket number instead."
        )
    else:
        reply_message = collect_ticket(ticket_number)

    await message.channel.send(reply_message)


token = getenv("DISCORD_BOT_TOKEN")
bot.run(token)
