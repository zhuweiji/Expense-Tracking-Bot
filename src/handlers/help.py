from telegram import Update
from telegram.ext import (
    Application,
    CallbackContext,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)


async def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""

    assert update.message, 'update.message was None'

    HELP_TEXT = """
Expense Tracker Bot Help

This bot helps you track and analyze your expenses. Here are the available commands:

Commands:
- /start - Begin interacting with the bot
- /help - Display available commands and instructions
- /last_month_stats - Show an analysis of last month's expenses and an overview of transactions by month
- /last_statement_stats - Show an analysis of the last credit card statement's expenses
- /data - List the months for which expense data is available and processed
- /list - Display a detailed list of transactions from the last month

Uploading Statements:
To add new expense data:
1. Upload a PDF of your credit card statement to the bot.
2. The bot will automatically convert the PDF to CSV and store the data.
"""

    await update.message.reply_text(HELP_TEXT)
