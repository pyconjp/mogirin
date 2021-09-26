from os import getenv
from traceback import TracebackException

import discord
from discord.ext import commands

from mogirin import (
    TicketAlreadyCollected,
    TicketCollector,
    TicketNumberNotFound,
    find_ticket_number,
)

MOGIRI_CHANNEL_ID = int(getenv("MOGIRI_CHANNEL_ID"))
ATTENDEE_ROLE_ID = int(getenv("ATTENDEE_ROLE_ID"))

bot = commands.Bot(command_prefix="/")
collector = TicketCollector(getenv("SPREADSHEET_ID"))


class NeedToNotifyMonitors(Exception):
    def __init__(self, message):
        self.message = message


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


async def notify(
    message,
    channel_id=int(getenv("LOGGING_CHANNEL_ID")),
    guild_id=int(getenv("GUILD_ID")),
    role_id=int(getenv("STAFF_ROLE_ID")),
):
    channel = bot.get_channel(channel_id)
    guild = bot.get_guild(guild_id)
    staff_role = guild.get_role(role_id)
    await channel.send(f"{staff_role.mention} {message}")


@bot.event
async def on_ready():
    await greet()


@bot.command()
async def ping(ctx):
    await ctx.send("pong")


async def collect_ticket(
    ticket_number: str, member: discord.Member, role: discord.Role
) -> str:
    try:
        await collector.collect(ticket_number, member, role)
    except TicketNumberNotFound:
        return (
            f"LookupError: Couldn't find your number {ticket_number!r}.\n"
            "If the number is correct, try again in a few hours "
            "(Sorry, there is a lag in synchronizing participant information)."
        )
    except TicketAlreadyCollected:
        message = (
            f"RuntimeError: the ticket {ticket_number!r} is already used.\n"
            "If the number is correct, please contact staff "
            "with `@2021-staff` mention."
        )
        raise NeedToNotifyMonitors(message)
    else:
        return "Accepted! Welcome to PyCon JP 2021 venue!"


@bot.event
async def on_message(message):
    if message.channel.id != MOGIRI_CHANNEL_ID:
        # もぎり用テキストチャンネル以外のmessageには反応しない
        return

    if message.author.bot:
        # botからのmessageには反応しない (Issue #8)
        return

    if bot.user not in message.mentions:
        # @mogirin メンションがないmessageには反応しない
        return

    attendee_role = message.guild.get_role(ATTENDEE_ROLE_ID)
    if attendee_role in message.author.roles:
        # すでにattendeeロールが付いているユーザからのmessageには反応しない
        return

    ticket_number = find_ticket_number(message.clean_content)
    needs_to_notify = False
    if ticket_number is None:
        reply_message = (
            f"ValueError: ticket number is not included in your message.\n"
            "Please input numeric ticket number like `@mogirin 1234567`."
        )
    else:
        try:
            reply_message = await collect_ticket(
                ticket_number, message.author, attendee_role
            )
        except NeedToNotifyMonitors as ex:
            needs_to_notify = True
            reply_message = ex.message

    await message.channel.send(f"{message.author.mention} {reply_message}")

    if needs_to_notify:
        monitor_message = (
            f"「{message.author.display_name}」氏のもぎりに以下のエラーを送出しました\n"
            f"{reply_message}"
        )
        await notify(monitor_message)


token = getenv("DISCORD_BOT_TOKEN")
bot.run(token)
