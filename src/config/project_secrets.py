import os

from dotenv import load_dotenv

from src.config.project_paths import project_root

env_file = project_root / '.env'
load_dotenv(env_file)


TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
ANTHROPIC_API_KEY = os.environ['ANTHROPIC_API_KEY']
DEVELOPER_CHAT_ID = os.environ.get('DEVELOPER_CHAT_ID', None)
