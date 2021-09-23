from os import getenv
from traceback import TracebackException

from discord.ext import commands

from mogirin import TicketCollector

MOGIRI_CHANNEL_ID = int(getenv("MOGIRI_CHANNEL_ID"))

bot = commands.Bot(command_prefix="/")
collector = TicketCollector(getenv("SPREADSHEET_ID"))


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
    return collector.collect(ticket_number)


@bot.event
async def on_message(message):
    if message.channel.id != MOGIRI_CHANNEL_ID:
        # もぎり用テキストチャンネル以外のmessageには反応しない
        return

    if bot.user not in message.mentions:
        return

    # TODO: 正規表現で最初に見つけた数字にするとより簡潔に書けそう
    ticket_number = message.content.split()[1]
    if not ticket_number.isnumeric():
        reply_message = (
            f"ValueError: invalid ticket number {ticket_number!r}\n"
            "Please input numeric ticket number instead."
        )
    else:
        reply_message = collect_ticket(ticket_number)

    await message.channel.send(f"{message.author.mention} {reply_message}")


token = getenv("DISCORD_BOT_TOKEN")
bot.run(token)
