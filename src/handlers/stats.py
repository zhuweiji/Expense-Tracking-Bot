import logging
import os
from datetime import timedelta

import pandas as pd
from telegram import Update

from src.config.project_paths import data_dir
from src.utilities.data_utilities import read_transaction_csvs
from src.utilities.text_message_utilities import format_nested_dict

log = logging.getLogger(__name__)


async def view_last_statement_stats(update: Update, context):
    assert update.message, 'update.message is None'

    df = read_transaction_csvs(data_dir, latest_only=True)

    analysis = analyze_transactions(df)
    txt = format_nested_dict(analysis)
    await update.message.reply_text(txt)


async def view_last_month_stats(update: Update, context):
    assert update.message, 'update.message is None'

    df = read_transaction_csvs(data_dir)

    analysis = analyze_transactions(df)
    txt = format_nested_dict(analysis)
    await update.message.reply_text(txt)


def monthly_spending_overview(df):
    monthly_spending = df.groupby(df['date'].dt.to_period('M'))[
        'price'].sum().to_dict()
    return {str(k): float(v) for k, v in monthly_spending.items()}


def category_breakdown(df, start_date, end_date):
    mask = (df['date'] >= start_date) & (df['date'] <= end_date)
    category_totals = df.loc[mask].groupby('category')['price'].sum().to_dict()
    return {k: float(v) for k, v in category_totals.items()}


def top_merchants(df, start_date, end_date, top_n=10):
    mask = (df['date'] >= start_date) & (df['date'] <= end_date)
    merchant_totals = df.loc[mask].groupby(
        'name')['price'].sum().nlargest(top_n).to_dict()
    return {k: float(v) for k, v in merchant_totals.items()}


def recurring_expenses(df, start_date, end_date, threshold=2):
    mask = (df['date'] >= start_date) & (df['date'] <= end_date)
    recurring = df.loc[mask].groupby('name').agg({
        'price': 'mean',
        'date': 'count'
    })
    recurring = recurring[recurring['date'] >= threshold]
    return recurring['price'].to_dict()

# should be output by LLM analysis
# def unusual_spending_alerts(df, start_date, end_date, threshold=2):
#     mask = (df['date'] >= start_date) & (df['date'] <= end_date)
#     recent_spending = df.loc[mask].groupby('category')['price'].sum()

#     overall_avg = df.groupby('category')['price'].mean()
#     unusual = recent_spending[recent_spending > overall_avg * threshold]

#     return unusual.to_dict()


def discretionary_vs_essential_spending(df, start_date, end_date, essential_categories):
    mask = (df['date'] >= start_date) & (df['date'] <= end_date)
    spending = df.loc[mask]

    essential = spending[spending['category'].isin(
        essential_categories)]['price'].sum()
    discretionary = spending[~spending['category'].isin(
        essential_categories)]['price'].sum()

    return {
        'essential': float(essential),
        'discretionary': float(discretionary)
    }


def get_sum_of_top_x_transactions(df, x: int = 20, step: int = 5):
    result = {}

    for i in range(5, x, step):
        result[f'{i}'] = return_top_n_sum(df, i)

    return result


def return_top_n_sum(df, n=5):
    """
    Display the  combined price for the top-N items from the csv df.

    Parameters:
    df (pd.DataFrame): DataFrame with columns: date, name, price, category
    n (int): Number of top items to display (default is 5)

    Returns:
    None (prints the results)
    """
    # Ensure the price column is numeric
    df['price'] = pd.to_numeric(df['price'], errors='coerce')

    # Sort the DataFrame by price in descending order
    sorted_df = df.sort_values('price', ascending=False)

    # Get the top N items
    top_n = sorted_df.head(n)

    # Calculate the combined price
    combined_price = top_n['price'].sum()

    return combined_price


def analyze_transactions(df):
    last_date = df['date'].max()
    start_of_last_month = last_date.replace(day=1) - timedelta(days=1)
    start_of_last_month = start_of_last_month.replace(day=1)

    essential_categories = ['Groceries', 'Utilities',
                            'Rent', 'Transportation']  # Add more as needed

    return {
        'monthly_overview': monthly_spending_overview(df),
        'last_month': {
            'category_breakdown': category_breakdown(df, start_of_last_month, last_date),
            'top_merchants': top_merchants(df, start_of_last_month, last_date),
            'recurring_expenses': recurring_expenses(df, start_of_last_month, last_date),
            # 'unusual_spending': unusual_spending_alerts(df, start_of_last_month, last_date),
            'discretionary_vs_essential': discretionary_vs_essential_spending(df, start_of_last_month, last_date, essential_categories),
            'Combined_Value_of_top_N_transactions': get_sum_of_top_x_transactions(df),
        }
    }
