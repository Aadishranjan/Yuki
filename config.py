from dotenv import load_dotenv
import os

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGO_DB", "yuki")

GROQ_KEYS = [
    os.getenv("GROQ_API_KEY_1"),
    os.getenv("GROQ_API_KEY_2"),
    os.getenv("GROQ_API_KEY_3"),
    os.getenv("GROQ_API_KEY_4"),
    os.getenv("GROQ_API_KEY_5"),
    # os.getenv("GROQ_API_KEY_6"),
    # os.getenv("GROQ_API_KEY_7"),
    # os.getenv("GROQ_API_KEY_8"),
    # os.getenv("GROQ_API_KEY_9"),
    # os.getenv("GROQ_API_KEY_10"),
]

REPLY_CHANCE = 0.15
SIMILARITY_THRESHOLD = 0.45
MAX_CONTEXT = 8
TEMPLATE_CHANCE = 0.6
MARKOV_CHANCE = 0.15
