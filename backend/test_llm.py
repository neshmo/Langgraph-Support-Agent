import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

model = os.getenv("OPENROUTER_MODEL")
print(f"Testing model: {model}")

try:
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": "Hello, are you working?"}],
        stream=False 
    )
    print("Response received:")
    print(response.choices[0].message.content)
except Exception as e:
    print(f"Error: {e}")
