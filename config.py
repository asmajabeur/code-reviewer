import os
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
load_dotenv(dotenv_path=env_path)

openai_api_key = os.environ.get("OPENAI_API_KEY", "")
groq_api_key = os.environ.get("GROQ_API_KEY", "")

from openai import AsyncOpenAI
from agents import set_default_openai_client, set_default_openai_api
from agents.tracing import set_tracing_disabled

if openai_api_key:
    client = AsyncOpenAI(api_key=openai_api_key)
    set_default_openai_client(client)
    groq_model = "gpt-4o-mini"

elif groq_api_key:
    client = AsyncOpenAI(
        api_key=groq_api_key,
        base_url="https://api.groq.com/openai/v1"
    )
    set_default_openai_client(client)
    set_default_openai_api("chat_completions")
    set_tracing_disabled(True)
    groq_model = "llama-3.1-8b-instant"

else:
    raise ValueError("Aucune clé API trouvée dans .env !")