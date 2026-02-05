"""Command handlers for Yuki bot."""
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import os
from dotenv import load_dotenv

load_dotenv()

ADMIN_IDS = {8223925872}  # replace with YOUR Telegram ID


def register_commands(app: Client):
    """Register all command handlers."""

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
                    InlineKeyboardButton("ᴏᴡɴᴇʀ", user_id=7525763142),
                    InlineKeyboardButton("📣 ᴄʜᴀɴɴᴇʟ", url="https://t.me/Bot_X_Galaxy"),
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

    @app.on_callback_query(filters.regex("^help_ai$"))
    async def help_ai_cb(app: Client, callback_query):
        await callback_query.answer()
        keyboard = InlineKeyboardMarkup(
            [[
                InlineKeyboardButton("Back", callback_data="help_menu_from_start"),
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
                InlineKeyboardButton("Back", callback_data="help_menu_from_start"),
            ]]
        )
        await callback_query.message.edit_caption(
            "💰 Economy Commands:\n"
            "/bal — Check wallet, rank, status, kills, gear.\n"
            "/shop — View shop items.\n"
            "/shop buy <item_key> — Buy weapon/armor.\n"
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
