import html
import json
import logging
import traceback
from functools import wraps

from telegram import Update
from telegram.constants import ParseMode
from telegram.error import BadRequest, NetworkError, TelegramError, TimedOut
from telegram.ext import ContextTypes

from src.config.project_secrets import DEVELOPER_CHAT_ID

log = logging.getLogger(__name__)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    log.error("Exception while handling an update:", exc_info=context.error)

    if isinstance(context.error, BadRequest):
        log.error(f"BadRequest error: {context.error}")
        return
    elif isinstance(context.error, TimedOut):
        log.error(f"TimedOut error: {context.error}")
        return
    elif isinstance(context.error, NetworkError):
        log.error(f"NetworkError error: {context.error}")
        return
    # elif isinstance(context.error, TelegramError):
    #     log.error(f"TelegramError: {context.error}")
    #     return

    # For any other exception, prepare a message to send to the developer
    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)
    log.error(tb_string)

    # Build the message with some markup and additional information about what happened.
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        f"An exception was raised while handling an update\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    )

    if DEVELOPER_CHAT_ID:
        await context.bot.send_message(
            chat_id=DEVELOPER_CHAT_ID, text=message, parse_mode=ParseMode.HTML
        )
