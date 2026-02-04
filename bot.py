"""Main entry point for Yuki bot."""
from pyrogram import Client, idle
from plugins.commands import register_commands
from plugins.handlers import register_handlers
from config import BOT_TOKEN, API_ID, API_HASH

app = Client(
    "baka",
    bot_token = BOT_TOKEN,
    api_id = API_ID,
    api_hash = API_HASH
)

# ─── REGISTER PLUGINS ─────────────────────
register_commands(app)
register_handlers(app)

# ─── RUN BOT ──────────────────────────────
if __name__ == "__main__":
    app.start()
    me = app.get_me()
    print(f"@{me.username} is now start")
    idle()
    app.stop()
