"""Message handlers for Yuki bot."""
import time
import asyncio
import re
from collections import defaultdict
from pyrogram import Client, filters
from database.db import get_groups_collection, init_db as _init_db
from utils.responses import get_local_reply
from ai import ask_ai


# ─── Limits ─────────────────────────────
USER_COOLDOWN = 6          # seconds per user
MAX_ACTIVE_REQUESTS = 5   # global limit

last_used = defaultdict(float)
api_semaphore = asyncio.Semaphore(MAX_ACTIVE_REQUESTS)


def register_handlers(app: Client):
    """Register all message handlers."""
    _init_db()
    groups = get_groups_collection()

    @app.on_message(filters.private & filters.text)
    async def baka_ai(_, message):
        """Handle private chat messages."""
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
        """Handle group chat messages."""
        if message.chat and message.chat.id:
            groups.update_one(
                {"chat_id": message.chat.id},
                {"$set": {"chat_id": message.chat.id, "title": message.chat.title}},
                upsert=True,
            )
        text = message.text or ""

        bot = await app.get_me()
        
        # Create mention patterns (case-insensitive)
        text_lower = text.lower()
        bot_username_lower = bot.username.lower() if bot.username else ""
        mention_pattern = f"@{bot_username_lower}"

        # Check conditions
        mentioned = bot.username and mention_pattern in text_lower
        replied = (
            message.reply_to_message
            and message.reply_to_message.from_user
            and message.reply_to_message.from_user.is_bot
            and message.reply_to_message.from_user.id == bot.id
        )

        
        # Clean text by removing bot mention (case-insensitive)
        clean_text = text
        if mentioned and bot.username:
            # Remove mention from text (case-insensitive) while keeping original casing
            clean_text = re.sub(re.escape(f"@{bot.username}"), "", text, flags=re.IGNORECASE).strip()
        
        # If user only mentioned the bot, guide them to start
        if mentioned and not clean_text:
            return await message.reply_text(f"Hmph. Yes, I’m here. Now say something more than just calling me 😤")

        # Check for keywords
        local_reply = get_local_reply(clean_text)

        # Respond if any condition is met
        should_respond = mentioned or replied or (local_reply is not None)
        
        if not should_respond:
            return

        # If we have a keyword response, use it
        if local_reply:
            return await message.reply_text(local_reply)

        # If mentioned or replied but no keyword match, use AI
        if mentioned or replied:
            async with api_semaphore:
                try:
                    reply = ask_ai(clean_text)
                    await message.reply_text(reply)
                except Exception as e:
                    await message.reply_text("Hmph… too noisy here 😵‍💫")
