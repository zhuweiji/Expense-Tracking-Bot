import csv
import html
import io
import re

from src.utilities.data_utilities import safe_float


def escape_markdown_v2(text):
    """
    Escape special characters for Telegram's MarkdownV2 format.
    """
    # Characters that need to be escaped
    escape_chars = r'_*[]()~`>#+-=|{}.!'

    # Function to escape a single character
    def escape_char(match):
        return '\\' + match.group(0)

    # Escape special characters
    return re.sub(f'([{re.escape(escape_chars)}])', escape_char, text)


def chunk_html_for_telegram(html_content, char_limit=4096, footer_text=None):
    chunks = []
    current_chunk = ""
    lines = html_content.split('\n')

    for line in lines:
        if len(current_chunk) + len(line) + 1 > char_limit:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = ""

        current_chunk += line + '\n'

    if current_chunk:
        chunks.append(current_chunk.strip())

    # Ensure each chunk is valid HTML and add footer text if provided
    for i in range(len(chunks)):
        if not chunks[i].startswith('<pre>'):
            chunks[i] = '<pre>\n' + chunks[i]
        # Add footer text to the last chunk
        if footer_text and i == len(chunks) - 1:
            chunks[i] = chunks[i].rstrip('</pre>') + f'\n\n{footer_text}</pre>'
        elif not chunks[i].endswith('</pre>'):
            chunks[i] = chunks[i] + '\n</pre>'

    return chunks


def split_markdown_messages(markdown_text, max_length=4096):
    messages = []
    current_message = ""
    lines = markdown_text.split('\n')

    # Add the header separately to ensure it's included in each message
    header = '\n'.join(lines[:3])  # Assuming the first 3 lines are the header
    current_message = header + '\n'

    for line in lines[3:]:  # Start from the 4th line (index 3)
        if len(current_message) + len(line) + 1 > max_length:
            # If adding this line would exceed the max length, start a new message
            messages.append(current_message.strip())
            current_message = header + '\n' + line + '\n'
        else:
            current_message += line + '\n'

    # Add the last message if it's not empty
    if current_message.strip():
        messages.append(current_message.strip())

    return messages


def snake_to_title(snake_str):
    """
    Convert a snake_case string to Title Case.

    Args:
    snake_str (str): A string in snake_case format

    Returns:
    str: The input string converted to Title Case
    """
    # Split the string by underscores
    words = snake_str.split('_')
    # Capitalize each word and join them with spaces
    return ' '.join(word.capitalize() for word in words)


def format_nested_dict(results, indent=0):
    output = []
    for key, value in results.items():
        key_text = snake_to_title(key)
        if isinstance(value, dict):
            output.append('  ' * indent + f"{key_text}:")
            output.append(format_nested_dict(value, indent + 2))
            output.append('\n')
        elif isinstance(value, float):
            output.append('  ' * indent + f"{key_text}: ${value:.2f}")
        else:
            output.append('  ' * indent + f"{key_text}: {value}")
    return '\n'.join(output)


def sort_csv_by_price_to_telegram_html(csv_content):
    # Read CSV content
    csv_file = io.StringIO(csv_content)
    reader = csv.DictReader(csv_file)

    # Convert to list of dictionaries and sort by price
    data = list(reader)
    data.sort(key=lambda x: safe_float(x.get('price', 0) or 0), reverse=True)

    # Generate Telegram-compatible HTML
    html_output = '<pre>\n'

    # Add header row
    headers = list(data[0].keys())
    header_row = ' | '.join(
        f'<b>{html.escape(header)}</b>' for header in headers)
    html_output += f'{header_row}\n'
    html_output += '-' * \
        len(header_row.replace('<b>', '').replace('</b>', '')) + '\n'

    # Add data rows
    for row in data:
        row_values = [html.escape(str(row[header])) for header in headers]
        html_output += ' | '.join(row_values) + '\n'

    html_output += '</pre>'

    return html_output
