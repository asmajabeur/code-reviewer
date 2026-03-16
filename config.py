import os
from dotenv import load_dotenv

load_dotenv()

# We use the deepseek model (llama-3.3-70b-versatile or similar) via Groq API
groq_api_key = os.environ.get("GROQ_API_KEY", "")

from openai import AsyncOpenAI
import agents.models._openai_shared as shared

# Force openai-agents to use our custom OpenAI client pointing to Groq
groq_client = AsyncOpenAI(
    api_key=groq_api_key,
    base_url="https://api.groq.com/openai/v1"
)
shared.set_default_openai_client(groq_client)

groq_model = "llama-3.3-70b-versatile"

