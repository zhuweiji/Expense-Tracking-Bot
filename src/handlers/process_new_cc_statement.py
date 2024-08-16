import logging
import os
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Optional

from anthropic import APIError
from telegram import Message, Update
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
from src.llm import llm_client
from src.utilities.image_utilities import pdf_to_images, pdf_to_text

log = logging.getLogger(__name__)


async def handle_document(update: Update, context):
    assert update.message, 'update.message is None'
    assert update.message.document, 'update.message.document is None'
    assert update.message.document.file_name, 'update.message.document.file_name is None'

    # Get the file
    file = await context.bot.get_file(update.message.document.file_id)

    pdf_path = cc_statement_dir / f'{update.message.document.file_name}'
    await file.download_to_drive(pdf_path)

    await update.message.reply_text('PDF received and saved. Analyzing...')

    current_year = datetime.now().strftime("%Y")

    cleaned_text = pdf_to_text(pdf_path)

    # Send to Claude API
    prompt = """
Help me categorize each transaction in this credit card statement into a csv table.
Use the columns date, name, price, category.
For BUS/MRT transactions, truncate the id at the end of the transaction name.
Make sure that the result is a valid csv with a transaction on each row.
Here's the credit card statement:

{statement}

Please provide the categorized transactions in CSV format.
"""

    prompt += f'Format the date as %d %b %Y. If the year is missing, use {current_year}.'
    prompt += f"Don't start the response with a message like 'This was generated by AI'. Only output the csv and nothing else. "

    log.info('Querying Claude')

    try:
        message = llm_client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=4000,
            messages=[
                {
                    "role": "user",
                    "content": prompt.format(statement=cleaned_text)
                }
            ]
        )

        # Save Claude's response to a CSV file
        csv_path = data_dir / \
            f'{os.path.splitext(update.message.document.file_name)[0]}.csv'

        with open(csv_path, 'w', newline='') as csv_file:
            csv_file.write(message.content[0].text)  # type: ignore

        if message.stop_reason == 'max_tokens':
            max_token_exceeded_message = 'Warning: CC statement was too large, CSV data was truncated.'
            log.warning(max_token_exceeded_message)
            await update.message.reply_text(max_token_exceeded_message)

        await update.message.reply_text('Analysis complete. CSV file saved.')

    except APIError as e:
        log.error(f"API error occurred: {e}")
        await update.message.reply_text(f"API error occurred: {e}")

    except Exception as e:
        log.error(f"An unexpected error occurred: {e}")
        await update.message.reply_text(f"An unexpected error occurred: {e}")


async def handle_document__images(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raise NotImplementedError

    assert update.message, 'update.message was None'
    assert update.message.document, 'update.message.document was None'

    file = await context.bot.get_file(update.message.document.file_id)

    pdf_path = cc_statement_dir / f'{update.message.document.file_name}'
    await file.download_to_drive(pdf_path)

    await update.message.reply_text('PDF received. Converting to images...')

    # Convert PDF to images
    image_files = pdf_to_images(pdf_path)

    if not image_files:
        await update.message.reply_text('Error converting PDF to images. Please try again with a different PDF.')
        return

    await update.message.reply_text('Analyzing images...')

    # Prepare the message content
    content = [
        {
            "type": "text",
            "text": """Help me categorize each transaction in this credit card statement into a csv table.
Use the columns date, name, price, category. For BUS/MRT transactions, truncate the id at the end of the transaction name.
Make sure that the result is a valid csv with a transaction on each row. Remove any reference numbers (Ref No).
The statement is provided in the following image(s):"""
        }
    ]

    # Add each image to the content
    for i, image_file in enumerate(image_files):
        content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/png",
                "data": base64.b64encode(image_file.getvalue()).decode()
            }
        })

    log.info('Querying Claude')

    message = llm_client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=2000,
        messages=[
            {
                "role": "user",
                "content": content
            }
        ]
    )

    # Save Claude's response to a CSV file
    csv_path = data_dir / \
        f'{os.path.splitext(update.message.document.file_name)[0]}.csv'
    with open(csv_path, 'w', newline='') as csv_file:
        csv_file.write(message.content[0].text)

    await update.message.reply_text('Analysis complete. CSV file saved.')
