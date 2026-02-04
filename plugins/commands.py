"""Command handlers for Yuki bot."""
from pyrogram import Client, filters
import os
from dotenv import load_dotenv

load_dotenv()

ADMIN_IDS = {8223925872}  # replace with YOUR Telegram ID


def register_commands(app: Client):
    """Register all command handlers."""

    @app.on_message(filters.command("start"))
    async def start_cmd(_, message):
        await message.reply_text(
            "Tch… I'm not here to entertain you 😤\nType something already."
        )

    @app.on_message(filters.command("help"))
    async def help_cmd(_, message):
        await message.reply_text(
            "Don't be dumb 😆\nJust talk normally. I'll reply."
        )

    @app.on_message(filters.command("ping"))
    async def ping_cmd(_, message):
        await message.reply_text("Pong 😤")

    @app.on_message(filters.command("reload"))
    async def reload_json(_, message):
        if message.from_user.id not in ADMIN_IDS:
            return await message.reply_text("Oi—who allowed you to do that? 😤")

        # Reload utils module
        import importlib
        import utils.responses
        importlib.reload(utils.responses)
        await message.reply_text("JSON reloaded. Hmph… don't break it 😆")
