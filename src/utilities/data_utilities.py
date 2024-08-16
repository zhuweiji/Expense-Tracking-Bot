import csv
import io
import os
import re

import pandas as pd

from src.config.project_paths import data_dir


def safe_float(value):
    try:
        return float(value or 0)
    except ValueError:
        return float(0)


def sum_prices_from_csv(csv_content):
    csv_file = io.StringIO(csv_content)
    reader = csv.DictReader(csv_file)
    total_price = sum(float(row.get('price', 0) or 0) for row in reader)
    return total_price


def list_transaction_csvs(folder_path=data_dir):
    files = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.csv'):
            files.append(filename)

    return files


def read_transaction_csvs(folder_path=data_dir, latest_only=False):
    # List to store DataFrames for each CSV file
    dfs = []

    # Get all CSV files in the folder
    csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

    # If latest_only is True, select only the latest file
    if latest_only and csv_files:
        csv_files = [max(csv_files, key=lambda f: f.split('_')[-1])]

    # Iterate through the selected files
    for filename in csv_files:
        file_path = os.path.join(folder_path, filename)

        # Read the CSV file
        df = pd.read_csv(file_path)

        # Ensure the required columns are present
        required_columns = ['date', 'name', 'price', 'category']
        if not all(col in df.columns for col in required_columns):
            print(f"Skipping {filename}: Missing required columns")
            continue

        # Convert date string to datetime object
        df['date'] = pd.to_datetime(df['date'], format='%d %b %Y')

        # Convert price to float
        df['price'] = df['price'].astype(float)

        # Add the DataFrame to our list
        dfs.append(df)

    # Combine all DataFrames into a single DataFrame
    if dfs:
        combined_df = pd.concat(dfs, ignore_index=True)

        # Sort the combined DataFrame by date
        combined_df = combined_df.sort_values('date')

        return combined_df
    else:
        print("No valid CSV files found in the specified folder.")
        return None


def remove_text_after_transaction_end(text: str):
    """
    Split a string using the regex pattern for "end of transaction details".

    :param text: The input string to split
    :return: A list of substrings split by the pattern
    """
    pattern = r'\-+ end of transaction details \-+'

    # re.IGNORECASE flag makes the regex case-insensitive
    # re.split() splits the string based on the pattern
    parts = re.split(pattern, text, flags=re.IGNORECASE)
    return parts[0]


def remove_uob_disclaimer(text: str) -> str:
    disclaimer_en = r"""Please note that you are bound by a duty under the rules governing the operation of this account, to check the entries in the above statement. If you do not notify us in writing of any errors,
omissions or unauthorised debits within fourteen \(14\) days of this statement, the entries above shall be deemed valid, correct, accurate and conclusively binding upon you, and you shall have no
claim against the bank in relation thereto."""

    disclaimer_zh = r"""请注意，在此户口的管理条规下，您必须核对此结单所列项目，并在十四（1 4 ）天内，以书面通知本行任何错误、遗漏或未经授权支账，否则上述项目当被视为有效、适当和准确并受其约束，您不得向本行索取赔偿\."""

    footer = r"""United Overseas Bank Limited   •   80 Raffles Place UOB Plaza Singapore 048624  •  Co\. Reg\. No\. 193500026Z  •  GST Reg\. No\. MR-8500194-3  •   www\.uob\.com\.sg"""

    # Combine all parts into one pattern
    pattern = f"{disclaimer_en}|{disclaimer_zh}|{footer}"

    # Remove the pattern, ignoring whitespace and capitalization
    cleaned_text = re.sub(
        pattern, '', text, flags=re.IGNORECASE | re.DOTALL | re.MULTILINE)

    return cleaned_text
