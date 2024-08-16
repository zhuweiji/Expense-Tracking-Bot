# Expense Tracker Bot

This repository contains a Telegram bot that helps you track and analyze your expenses. 

You might have several credit cards and debit accounts spread across various banks. Each will provide different monthly credit card statements, which makes it a little hard to track your overall expenditure. This project allows you to spin up a telegram bot to interact with your expense data, helping you to get a comprehensive view over your expenditure. 

Of course, since this is very personal financial data that you wouldn't want a third-party handling, this allows you to maintain complete control over all your data.

The bot is designed to run as a Docker container and uses python-telegram-bot.

## Features

- Process PDF credit card statements and extract transaction data
- Automatically tag transactions using an LLM (e.g., shopping, dining, travel)
- Store processed transaction data locally
- Provide analysis and insights on your spending habits

## Prerequisites

- Docker
- [Telegram Bot Token](https://core.telegram.org/bots/tutorial)
- [Anthropic API Key](https://docs.anthropic.com/en/api/getting-started)

## Setup

1. Clone this repository:

   ```
   git clone https://github.com/yourusername/expense-tracker-bot.git
   cd expense-tracker-bot
   ```

2. Create a `.env` file in the root directory with the following content:

   ```
    TELEGRAM_BOT_TOKEN=
    ANTHROPIC_API_KEY=
    DEVELOPER_CHAT_ID=

   ```

3. Build the Docker image:

   ```
   docker build -t expense-tracker-bot .
   ```

4. Run the Docker container:
   ```
   docker run -d --name expense-tracker-bot \
    -v ./docker_volume/data:/app/data \
    -v ./docker_volume/cc_statements:/app/cc_statements \
    expense-tracker-bot

   ```

## Usage

Once the bot is running, you can interact with it on Telegram using the following commands:

- `/start` - Begin interacting with the bot
- `/help` - Display available commands and instructions
- `/last_month_stats` - Show an analysis of last month's expenses and an overview of transactions by month
- `/last_statement_stats` - Show an analysis of the last credit card statement's expenses
- `/data` - List the months for which expense data is available and processed
- `/list` - Display a detailed list of transactions from the last month

To add new expense data:

1. Upload a PDF of your credit card statement to the bot
2. The bot will automatically convert the PDF to CSV and store the data

## Development

To modify or extend the bot's functionality:

1. Make changes to the Python code in the `src` directory
2. Rebuild the Docker image:
   ```
   docker build -t expense-tracker-bot .
   ```
3. Stop and remove the existing container:
   ```
   docker stop expense-tracker-bot
   docker rm expense-tracker-bot
   ```
4. Run the new container with the updated image

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
