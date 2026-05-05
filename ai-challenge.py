
import os
from dotenv import load_dotenv
from openai import OpenAI
import pandas as pd 

load_dotenv()


ai_client = OpenAI(
    base_url = os.getenv("LLM_DEFAULT_BASE_URL"),
    api_key = os.getenv("LLM_DEFAULT_APIKEY")
)

completions = ai_client.chat.completions.create(
    model = os.getenv("LLM_DEFAULT_MODEL"),
    messages = [
        {
            'role': 'system',
            'content': os.getenv("LLM_DEFAULT_SYSTEM")
        },
        {
            'role': 'user',
            'content': 'What\'s Generative AI? '
        },
    ],
    temperature=1,
)

print(completions.choices[0].message.content)
