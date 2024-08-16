import anthropic
from anthropic import Anthropic, APIError

from src.config.project_secrets import ANTHROPIC_API_KEY


def get_llm_client():
    return anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
