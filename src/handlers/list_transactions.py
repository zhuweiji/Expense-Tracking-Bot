import os

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

from src.config.project_paths import data_dir
from src.utilities.data_utilities import list_transaction_csvs, sum_prices_from_csv
from src.utilities.text_message_utilities import (
    chunk_html_for_telegram,
    sort_csv_by_price_to_telegram_html,
)


async def list_transactions_last_month(update: Update,  context: CallbackContext):
    assert update.message, 'update.message was None'

    # Get all CSV files in the folder
    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]

    if csv_files:
        csv_files = [max(csv_files, key=lambda f: f.split('_')[-1])]

        data = (data_dir / csv_files[0]).read_text()
        html_txt = sort_csv_by_price_to_telegram_html(data)

        total = sum_prices_from_csv(data)

        for i in chunk_html_for_telegram(html_txt):
            await update.message.reply_text(i, parse_mode=ParseMode.HTML)
        await update.message.reply_text(f'Total: {total}')
    else:
        await update.message.reply_text('no files')


async def list_transaction_data_months(update: Update, context):
    assert update.message, 'update.message was None'

    txt = '\n'.join([i.split('_')[0] for i in list_transaction_csvs()])
    await update.message.reply_text(txt)
