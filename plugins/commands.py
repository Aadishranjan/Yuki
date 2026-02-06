"""Command handlers for Yuki bot."""
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import os
import sys
import time
import psutil
from dotenv import load_dotenv
from config import OWNER_ID, UPDATE_CHANNEL
from database.db import get_sudoers_collection, get_users_collection, get_groups_collection, init_db as _init_db

load_dotenv()

ADMIN_IDS = {8223925872}  # replace with YOUR Telegram ID


def register_commands(app: Client):
    """Register all command handlers."""
    start_time = time.monotonic()
    _init_db()
    sudoers = get_sudoers_collection()
    users = get_users_collection()
    groups = get_groups_collection()

    def _is_owner(user_id: int) -> bool:
        return OWNER_ID and user_id == OWNER_ID

    def _is_sudo(user_id: int) -> bool:
        return _is_owner(user_id) or sudoers.find_one({"user_id": user_id}) is not None

    async def _resolve_user(app: Client, message, args: list[str]):
        if message.reply_to_message and message.reply_to_message.from_user:
            return message.reply_to_message.from_user
        if len(args) < 2:
            return None
        target = args[1]
        try:
            return await app.get_users(target)
        except Exception:
            return None

    async def _help_main_markup(app: Client):
        me = await app.get_me()
        bot_username = me.username or ""
        return InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "ᴀᴅᴅ ᴍᴇ ʙᴀʙʏ 🖤",
                        url=f"https://t.me/{bot_username}?startgroup=true" if bot_username else "https://t.me/",
                    ),
                ],
                [
                    InlineKeyboardButton("ᴏᴡɴᴇʀ", user_id=OWNER_ID),
                    InlineKeyboardButton("📣 ᴄʜᴀɴɴᴇʟ", url=f"https://t.me/{UPDATE_CHANNEL}"),
                ],
                [
                    InlineKeyboardButton("ꜰᴜɴᴄᴛɪᴏɴꜱ + ᴄᴏᴍᴍᴀɴᴅꜱ", callback_data="help_menu_from_start"),
                ],
            ]
        )

    def _help_main_text(mention: str) -> str:
        return (
            f"👋 Kon'nichiwa {mention} (⁠≧⁠▽⁠≦⁠)\n\n"
            "『 🫧 yυĸι ×͜࿐ 』\n"
            "The Aesthetic AI-Powered RPG Bot! 🌸\n\n"
            "🎮 𝐅𝐞𝐚𝐭𝐮𝐫𝐞𝐬:\n"
            "‣ RPG: Kill, Rob (100%), Protect\n"
            "‣ Social: Marry, Couple\n"
            "‣ Economy: Claim, Give\n"
            "‣ AI: Sassy Chatbot\n\n"
            "💭 𝐍𝐞𝐞𝐝 𝐇𝐞𝐥𝐩?\n"
            "Click the buttons below!"
        )

    def _help_menu_text() -> str:
        return "Help Menu:\nChoose a category below."

    def _help_menu_markup(show_back: bool) -> InlineKeyboardMarkup:
        rows = [
            [
                InlineKeyboardButton("ᴇᴄᴏɴᴏᴍʏ", callback_data="help_economy"),
                InlineKeyboardButton("ᴀɪ", callback_data="help_ai"),
            ],
            [
                InlineKeyboardButton("ʙʀᴏᴀᴅᴄᴀꜱᴛ", callback_data="help_admin"),
            ],
            [
                InlineKeyboardButton("ᴏᴡɴᴇʀ", user_id=7525763142),
            ],
        ]
        if show_back:
            rows.append([InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="help_back_to_start")])
        return InlineKeyboardMarkup(rows)

    @app.on_message(filters.command("start"))
    async def start_cmd(app: Client, message):
        user = message.from_user
        mention = user.mention if user else "there"
        keyboard = await _help_main_markup(app)
        await message.reply_photo(
            photo="https://files.catbox.moe/yn3pk2.jpg",
            caption=_help_main_text(mention),
            reply_markup=keyboard,
        )

    @app.on_message(filters.command("help"))
    async def help_cmd(app: Client, message):
        keyboard = _help_menu_markup(show_back=False)
        await message.reply_photo(
            photo="https://files.catbox.moe/yn3pk2.jpg",
            caption=_help_menu_text(),
            reply_markup=keyboard,
        )

    @app.on_message(filters.command("ping"))
    async def ping_cmd(app: Client, message):
        me = await app.get_me()
        mentionbot = me.mention if me else "Bot"

        uptime_seconds = int(time.monotonic() - start_time)
        hours = uptime_seconds // 3600
        minutes = (uptime_seconds % 3600) // 60
        seconds = uptime_seconds % 60
        uptime_text = f"{hours}ʜ:{minutes}ᴍ:{seconds}s"

        ram = psutil.virtual_memory().percent
        cpu = psutil.cpu_percent(interval=0.2)
        disk = psutil.disk_usage("/").percent

        caption = (
            f"{mentionbot} ꜱʏꜱᴛᴇᴍ ꜱᴛᴀᴛꜱ :\n\n"
            f"↬ ᴜᴘᴛɪᴍᴇ : {uptime_text}\n"
            f"↬ ʀᴀᴍ : {ram:.1f}%\n"
            f"↬ ᴄᴘᴜ : {cpu:.1f}%\n"
            f"↬ ᴅɪꜱᴋ : {disk:.1f}%"
        )

        await message.reply_photo(
            photo="https://files.catbox.moe/yn3pk2.jpg",
            caption=caption,
        )

    @app.on_message(filters.command("reload"))
    async def reload_json(_, message):
        if message.from_user.id not in ADMIN_IDS:
            return await message.reply_text("Oi—who allowed you to do that? 😤")

        # Reload utils module
        import importlib
        import utils.responses
        importlib.reload(utils.responses)
        await message.reply_text("JSON reloaded. Hmph… don't break it 😆")

    @app.on_message(filters.command("restart"))
    async def restart_cmd(_, message):
        if not message.from_user or not _is_sudo(message.from_user.id):
            return await message.reply_text("You are not allowed to use this.")
        await message.reply_text("Restarting...")
        os.execv(sys.executable, [sys.executable] + sys.argv)

    @app.on_message(filters.command("stats"))
    async def stats_cmd(_, message):
        if not message.from_user or not _is_sudo(message.from_user.id):
            return await message.reply_text("You are not allowed to use this.")
        total_users = users.count_documents({})
        total_groups = groups.count_documents({})
        await message.reply_text(
            "📊 Stats\n"
            f"👤 Users: {total_users}\n"
            f"👥 Groups: {total_groups}"
        )

    @app.on_message(filters.command("addsudo"))
    async def addsudo_cmd(app: Client, message):
        if not message.from_user or not _is_owner(message.from_user.id):
            return await message.reply_text("Only owner can use this.")
        target = await _resolve_user(app, message, message.text.split())
        if not target or not target.id:
            return await message.reply_text("Usage: /addsudo <user_id or @username> or reply")
        sudoers.update_one(
            {"user_id": target.id},
            {"$set": {"user_id": target.id, "username": target.username}},
            upsert=True,
        )
        await message.reply_text(f"Added sudo: {target.first_name}")

    @app.on_message(filters.command("removesudo"))
    async def removesudo_cmd(app: Client, message):
        if not message.from_user or not _is_owner(message.from_user.id):
            return await message.reply_text("Only owner can use this.")
        target = await _resolve_user(app, message, message.text.split())
        if not target or not target.id:
            return await message.reply_text("Usage: /removesudo <user_id or @username> or reply")
        sudoers.delete_one({"user_id": target.id})
        await message.reply_text(f"Removed sudo: {target.first_name}")

    @app.on_message(filters.command("sudolist"))
    async def sudolist_cmd(_, message):
        if not message.from_user or not _is_sudo(message.from_user.id):
            return await message.reply_text("You are not allowed to use this.")
        rows = list(sudoers.find({}, {"user_id": 1, "username": 1}))
        if not rows:
            return await message.reply_text("No sudo users found.")
        lines = []
        for idx, row in enumerate(rows, 1):
            uname = row.get("username")
            label = f"@{uname}" if uname else str(row.get("user_id"))
            lines.append(f"{idx}. {label}")
        await message.reply_text("Sudo Users:\n" + "\n".join(lines))

    @app.on_callback_query(filters.regex("^help_ai$"))
    async def help_ai_cb(app: Client, callback_query):
        await callback_query.answer()
        keyboard = InlineKeyboardMarkup(
            [[
                InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="help_menu_from_start"),
            ]]
        )
        await callback_query.message.edit_caption(
            "AI:\nhello world",
            reply_markup=keyboard,
        )

    @app.on_callback_query(filters.regex("^help_economy$"))
    async def help_economy_cb(app: Client, callback_query):
        await callback_query.answer()
        keyboard = InlineKeyboardMarkup(
            [[
                InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="help_menu_from_start"),
            ]]
        )
        await callback_query.message.edit_caption(
            "💰 Economy Commands:\n"
            "/bal — Check wallet, rank, status, kills, gear.\n"
            "/shop — View shop items.\n"
            "/give <amount> <user or reply> — Send coins (10% tax).\n"
            "/claim — Group bonus +2000 (24h cooldown).\n"
            "/daily — Daily reward +150 (24h cooldown).\n"
            "/ranking — Global leaderboard.\n"
            "\n"
            "⚔️ RPG Commands:\n"
            "/kill <user or reply> — Kill for 12h and earn 100–170 coins.\n"
            "/rob <amount> <user or reply> — Steal coins if your gear power is higher.\n"
            "/protect — Shield for 1 day.\n"
            "/revive — Revive for 500 coins.\n"
            "\n"
            "Notes:\n"
            "• Stronger gear blocks kill/rob.\n"
            "• Use /shop to see item keys.",
            reply_markup=keyboard,
        )

    @app.on_callback_query(filters.regex("^help_admin$"))
    async def help_admin_cb(app: Client, callback_query):
        await callback_query.answer()
        keyboard = InlineKeyboardMarkup(
            [[
                InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="help_menu_from_start"),
            ]]
        )
        await callback_query.message.edit_caption(
            "🛠️ Admin / Sudo Commands:\n"
            "/restart — Restart the bot (owner + sudo only).\n"
            "/ping — Show system stats.\n"
            "/stats — Total users + groups (owner + sudo only).\n"
            "/addsudo <user_id/@username or reply> — Add sudo (owner only).\n"
            "/removesudo <user_id/@username or reply> — Remove sudo (owner only).\n"
            "/sudolist — List sudo users (owner + sudo only).",
            reply_markup=keyboard,
        )

    @app.on_callback_query(filters.regex("^help_menu_from_start$"))
    async def help_menu_from_start_cb(app: Client, callback_query):
        await callback_query.answer()
        keyboard = _help_menu_markup(show_back=True)
        await callback_query.message.edit_caption(
            _help_menu_text(),
            reply_markup=keyboard,
        )

    @app.on_callback_query(filters.regex("^help_back_to_start$"))
    async def help_back_to_start_cb(app: Client, callback_query):
        await callback_query.answer()
        user = callback_query.from_user
        mention = user.mention if user else "there"
        keyboard = await _help_main_markup(app)
        await callback_query.message.edit_caption(
            _help_main_text(mention),
            reply_markup=keyboard,
        )
