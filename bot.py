import os
import json
import random
import time
import asyncio
from collections import defaultdict
from pyrogram import Client, filters
from dotenv import load_dotenv
from ai import ask_ai

load_dotenv()

ADMIN_IDS = {8223925872}  # replace with YOUR Telegram ID

app = Client(
    "baka",
    bot_token=os.getenv("BOT_TOKEN"),
    api_id=int(os.getenv("API_ID")),
    api_hash=os.getenv("API_HASH")
)

# ─── LOCAL RESPONSES ─────────────────────
def load_responses():
    with open("responses.json", "r", encoding="utf-8") as f:
        return json.load(f)

LOCAL_REPLIES = load_responses()


def get_local_reply(text: str):
    text = text.lower()

    for category in LOCAL_REPLIES.values():
        for keyword in category["keywords"]:
            if keyword in text:
                return random.choice(category["replies"])

    return None



# ─── Limits ─────────────────────────────
USER_COOLDOWN = 6          # seconds per user
MAX_ACTIVE_REQUESTS = 5   # global limit

last_used = defaultdict(float)
api_semaphore = asyncio.Semaphore(MAX_ACTIVE_REQUESTS)

# ─── COMMANDS (NO AI CALLS) ──────────────

@app.on_message(filters.command("start"))
async def start_cmd(_, message):
    await message.reply_text(
        "Tch… I’m not here to entertain you 😤\nType something already."
    )

@app.on_message(filters.command("help"))
async def help_cmd(_, message):
    await message.reply_text(
        "Don’t be dumb 😆\nJust talk normally. I’ll reply."
    )

@app.on_message(filters.command("ping"))
async def ping_cmd(_, message):
    await message.reply_text("Pong 😤")

@app.on_message(filters.command("reload"))
async def reload_json(_, message):
    if message.from_user.id not in ADMIN_IDS:
        return await message.reply_text("Oi—who allowed you to do that? 😤")

    global LOCAL_REPLIES
    try:
        LOCAL_REPLIES = load_responses()
        await message.reply_text("JSON reloaded. Hmph… don’t break it 😆")
    except Exception as e:
        await message.reply_text(f"Reload failed 😵‍💫\n{e}")


# ─── AI CHAT (HYBRID PART) ───────────────

@app.on_message(filters.private & filters.text)
async def baka_ai(_, message):

    if message.text.startswith("/"):
        return  # commands handled elsewhere

    user_id = message.from_user.id
    now = time.time()
    text = message.text

    # 🔹 1. JSON reply FIRST (no API)
    local_reply = get_local_reply(text)
    if local_reply:
        return await message.reply_text(local_reply)

    # ⛔ Per-user cooldown
    if now - last_used[user_id] < USER_COOLDOWN:
        return await message.reply_text("Tch—stop spamming 😤")

    last_used[user_id] = now

    # 🔹 2. AI fallback (limited)
    async with api_semaphore:
        try:
            reply = ask_ai(text)
            await message.reply_text(reply)
        except Exception:
            await message.reply_text("Hmph… my head hurts 😵‍💫")


@app.on_message(filters.group & filters.text)
async def group_chat(_, message):
    text = message.text or ""

    bot = await app.get_me()

    # reply only if mentioned or replied to
    mentioned = bot.username and f"@{bot.username}" in text
    replied = (
        message.reply_to_message
        and message.reply_to_message.from_user
        and message.reply_to_message.from_user.is_bot
    )

    if not (mentioned or replied):
        return

    # clean mention
    clean_text = text.replace(f"@{bot.username}", "").strip()

    # JSON reply first
    local = get_local_reply(clean_text)
    if local:
        return await message.reply_text(local)

    # AI fallback (API safe)
    async with api_semaphore:
        try:
            reply = ask_ai(clean_text)
            await message.reply_text(reply)
        except Exception:
            await message.reply_text("Hmph… too noisy here 😵‍💫")


app.run()
