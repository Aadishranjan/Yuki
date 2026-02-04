import os
import requests
from itertools import cycle
from config import GROQ_KEYS



# remove empty keys
GROQ_KEYS = [k for k in GROQ_KEYS if k]
if not GROQ_KEYS:
    raise RuntimeError("No GROQ API keys found")

API_POOL = cycle(GROQ_KEYS)

# ─── AI CONFIG ──────────────────────────────────────
SYSTEM_PROMPT = """
You are a yuki chatbot.
Replies must be VERY SHORT (1–2 sentences).
Playful, sarcastic, slightly rude, use can also use abusing words.
Use emojis 😤😆
"""

# Playful, sarcastic, slightly rude but not abusive.

MODELS = [
    "llama-3.1-8b-instant",
    "llama-3.1-70b-versatile"
]

API_URL = "https://api.groq.com/openai/v1/chat/completions"

# ─── INTERNAL CALL ───────────────────────────────────
def call_groq(api_key: str, model: str, user_text: str) -> str:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text}
        ],
        "temperature": 0.9,
        "max_tokens": 80
    }

    r = requests.post(API_URL, json=payload, headers=headers, timeout=15)
    data = r.json()

    if "choices" not in data:
        raise Exception(data)

    return data["choices"][0]["message"]["content"].split("\n")[0]

# ─── PUBLIC FUNCTION ─────────────────────────────────
def ask_ai(user_text: str) -> str:
    last_error = None

    # try each API key once per request (round-robin)
    for _ in range(len(GROQ_KEYS)):
        api_key = next(API_POOL)

        for model in MODELS:
            try:
                return call_groq(api_key, model, user_text)
            except Exception as e:
                last_error = e
                continue

    raise Exception(f"All AI providers failed: {last_error}")
