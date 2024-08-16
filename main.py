import logging

import pymupdf
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackContext,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from src.config.project_paths import cc_statement_dir, data_dir
from src.config.project_secrets import ANTHROPIC_API_KEY, TELEGRAM_BOT_TOKEN
from src.handlers import help
from src.handlers.exception_handler import error_handler
from src.handlers.list_transactions import (
    list_transaction_data_months,
    list_transactions_last_month,
)
from src.handlers.process_new_cc_statement import handle_document
from src.handlers.stats import view_last_month_stats, view_last_statement_stats

logging.basicConfig(
    format='%(name)s-%(levelname)s|%(lineno)d:  %(message)s', level=logging.INFO)

log = logging.getLogger(__name__)


cc_statement_dir.mkdir(parents=True, exist_ok=True)
data_dir.mkdir(parents=True, exist_ok=True)


def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", help.help_command))
    application.add_handler(CommandHandler("help", help.help_command))

    application.add_handler(CommandHandler(
        "last_month_stats", view_last_month_stats))

    application.add_handler(CommandHandler(
        "last_statement_stats", view_last_statement_stats))

    application.add_handler(CommandHandler(
        "data", list_transaction_data_months))

    application.add_handler(CommandHandler(
        "list", list_transactions_last_month))

    application.add_handler(MessageHandler(
        filters.Document.PDF, handle_document))

    # application.add_handler(MessageHandler(
    #     filters.Document.PDF, handle_document__images))

    application.add_error_handler(error_handler)

    log.info('bot started.')

    application.run_polling()


if __name__ == '__main__':
    main()
