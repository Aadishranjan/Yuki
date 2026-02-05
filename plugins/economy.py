"""Economy + RPG commands for Yuki bot."""
from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from database.db import get_users_collection, init_db as _init_db

SHOP_ITEMS = {
    "stick": {
        "name": "Stick",
        "title": "🪵 Stick",
        "price": 500,
        "type": "weapon",
        "power": 1,
        "rarity": "⚪️ Common",
        "buff_text": "+1% Kill Loot",
        "life_text": "⏳ 24 Hours",
        "description": "A deadly weapon. Increases your kill rewards by +1%.",
    },
    "brick": {
        "name": "Brick",
        "title": "🧱 Brick",
        "price": 1000,
        "type": "weapon",
        "power": 2,
        "rarity": "⚪️ Common",
        "buff_text": "+2% Kill Loot",
        "life_text": "⏳ 24 Hours",
        "description": "A deadly weapon. Increases your kill rewards by +2%.",
    },
    "slingshot": {
        "name": "Slingshot",
        "title": "🪃 Slingshot",
        "price": 2000,
        "type": "weapon",
        "power": 3,
        "rarity": "⚪️ Common",
        "buff_text": "+3% Kill Loot",
        "life_text": "⏳ 24 Hours",
        "description": "A deadly weapon. Increases your kill rewards by +3%.",
    },
    "knife": {
        "name": "Knife",
        "title": "🔪 Knife",
        "price": 3500,
        "type": "weapon",
        "power": 5,
        "rarity": "⚪️ Common",
        "buff_text": "+5% Kill Loot",
        "life_text": "⏳ 24 Hours",
        "description": "A deadly weapon. Increases your kill rewards by +5%.",
    },
    "bat": {
        "name": "Bat",
        "title": "🏏 Bat",
        "price": 5000,
        "type": "weapon",
        "power": 8,
        "rarity": "🟢 Uncommon",
        "buff_text": "+8% Kill Loot",
        "life_text": "⏳ 24 Hours",
        "description": "A deadly weapon. Increases your kill rewards by +8%.",
    },
    "axe": {
        "name": "Axe",
        "title": "🪓 Axe",
        "price": 7500,
        "type": "weapon",
        "power": 10,
        "rarity": "🟢 Uncommon",
        "buff_text": "+10% Kill Loot",
        "life_text": "⏳ 24 Hours",
        "description": "A deadly weapon. Increases your kill rewards by +10%.",
    },
    "hammer": {
        "name": "Hammer",
        "title": "🔨 Hammer",
        "price": 10000,
        "type": "weapon",
        "power": 12,
        "rarity": "🟢 Uncommon",
        "buff_text": "+12% Kill Loot",
        "life_text": "⏳ 24 Hours",
        "description": "A deadly weapon. Increases your kill rewards by +12%.",
    },
    "chainsaw": {
        "name": "Chainsaw",
        "title": "🪚 Chainsaw",
        "price": 15000,
        "type": "weapon",
        "power": 15,
        "rarity": "🟢 Uncommon",
        "buff_text": "+15% Kill Loot",
        "life_text": "⏳ 24 Hours",
        "description": "A deadly weapon. Increases your kill rewards by +15%.",
    },
    "pistol": {
        "name": "Pistol",
        "title": "🔫 Pistol",
        "price": 25000,
        "type": "weapon",
        "power": 20,
        "rarity": "🔵 Rare",
        "buff_text": "+20% Kill Loot",
        "life_text": "⏳ 24 Hours",
        "description": "A deadly weapon. Increases your kill rewards by +20%.",
    },
    "shotgun": {
        "name": "Shotgun",
        "title": "🧨 Shotgun",
        "price": 40000,
        "type": "weapon",
        "power": 25,
        "rarity": "🔵 Rare",
        "buff_text": "+25% Kill Loot",
        "life_text": "⏳ 24 Hours",
        "description": "A deadly weapon. Increases your kill rewards by +25%.",
    },
    "uzi": {
        "name": "Uzi",
        "title": "🔫 Uzi",
        "price": 55000,
        "type": "weapon",
        "power": 30,
        "rarity": "🔵 Rare",
        "buff_text": "+30% Kill Loot",
        "life_text": "⏳ 24 Hours",
        "description": "A deadly weapon. Increases your kill rewards by +30%.",
    },
    "katana": {
        "name": "Katana",
        "title": "⚔️ Katana",
        "price": 75000,
        "type": "weapon",
        "power": 35,
        "rarity": "🔵 Rare",
        "buff_text": "+35% Kill Loot",
        "life_text": "⏳ 24 Hours",
        "description": "A deadly weapon. Increases your kill rewards by +35%.",
    },
    "ak_47": {
        "name": "AK-47",
        "title": "💥 AK-47",
        "price": 100000,
        "type": "weapon",
        "power": 40,
        "rarity": "🟣 Epic",
        "buff_text": "+40% Kill Loot",
        "life_text": "⏳ 24 Hours",
        "description": "A deadly weapon. Increases your kill rewards by +40%.",
    },
    "minigun": {
        "name": "Minigun",
        "title": "🔥 Minigun",
        "price": 150000,
        "type": "weapon",
        "power": 45,
        "rarity": "🟣 Epic",
        "buff_text": "+45% Kill Loot",
        "life_text": "⏳ 24 Hours",
        "description": "A deadly weapon. Increases your kill rewards by +45%.",
    },
    "sniper": {
        "name": "Sniper",
        "title": "🎯 Sniper",
        "price": 200000,
        "type": "weapon",
        "power": 50,
        "rarity": "🟣 Epic",
        "buff_text": "+50% Kill Loot",
        "life_text": "⏳ 24 Hours",
        "description": "A deadly weapon. Increases your kill rewards by +50%.",
    },
    "rpg": {
        "name": "RPG",
        "title": "🚀 RPG",
        "price": 300000,
        "type": "weapon",
        "power": 55,
        "rarity": "🟣 Epic",
        "buff_text": "+55% Kill Loot",
        "life_text": "⏳ 24 Hours",
        "description": "A deadly weapon. Increases your kill rewards by +55%.",
    },
    "tank": {
        "name": "Tank",
        "title": "🚜 Tank",
        "price": 500000,
        "type": "weapon",
        "power": 57,
        "rarity": "🟣 Epic",
        "buff_text": "+57% Kill Loot",
        "life_text": "⏳ 24 Hours",
        "description": "A deadly weapon. Increases your kill rewards by +57%.",
    },
    "laser": {
        "name": "Laser",
        "title": "⚡ Laser",
        "price": 800000,
        "type": "weapon",
        "power": 59,
        "rarity": "🟣 Epic",
        "buff_text": "+59% Kill Loot",
        "life_text": "⏳ 24 Hours",
        "description": "A deadly weapon. Increases your kill rewards by +59%.",
    },
    "death_note": {
        "name": "Death Note",
        "title": "📓 Death Note",
        "price": 5000000,
        "type": "weapon",
        "power": 60,
        "rarity": "🟡 Legendary",
        "buff_text": "+60% Kill Loot",
        "life_text": "⏳ 24 Hours",
        "description": "Writes names. Deletes people. 60% Kill Buff.",
    },
    "cloth": {
        "name": "Cloth",
        "title": "👕 Cloth",
        "price": 2500,
        "type": "armor",
        "power": 5,
        "rarity": "⚪️ Common",
        "defense_text": "5% Block Chance",
        "life_text": "⏳ 24 Hours",
        "description": "Protective gear. Gives a 5% chance to block any robbery attempt.",
    },
    "leather": {
        "name": "Leather",
        "title": "🧥 Leather",
        "price": 8000,
        "type": "armor",
        "power": 8,
        "rarity": "🟢 Uncommon",
        "defense_text": "8% Block Chance",
        "life_text": "⏳ 24 Hours",
        "description": "Protective gear. Gives a 8% chance to block any robbery attempt.",
    },
    "chain": {
        "name": "Chain",
        "title": "⛓️ Chain",
        "price": 20000,
        "type": "armor",
        "power": 10,
        "rarity": "🔵 Rare",
        "defense_text": "10% Block Chance",
        "life_text": "⏳ 24 Hours",
        "description": "Protective gear. Gives a 10% chance to block any robbery attempt.",
    },
    "riot_shield": {
        "name": "Riot Shield",
        "title": "🛡️ Riot Shield",
        "price": 40000,
        "type": "armor",
        "power": 15,
        "rarity": "🔵 Rare",
        "defense_text": "15% Block Chance",
        "life_text": "⏳ 24 Hours",
        "description": "Protective gear. Gives a 15% chance to block any robbery attempt.",
    },
    "diamond": {
        "name": "Diamond",
        "title": "💎 Diamond",
        "price": 200000,
        "type": "armor",
        "power": 30,
        "rarity": "🟣 Epic",
        "defense_text": "30% Block Chance",
        "life_text": "⏳ 24 Hours",
        "description": "Protective gear. Gives a 30% chance to block any robbery attempt.",
    },
    "obsidian": {
        "name": "Obsidian",
        "title": "⚫️ Obsidian",
        "price": 400000,
        "type": "armor",
        "power": 35,
        "rarity": "🟣 Epic",
        "defense_text": "35% Block Chance",
        "life_text": "⏳ 24 Hours",
        "description": "Protective gear. Gives a 35% chance to block any robbery attempt.",
    },
    "nano_suit": {
        "name": "Nano Suit",
        "title": "🧬 Nano Suit",
        "price": 700000,
        "type": "armor",
        "power": 40,
        "rarity": "🟣 Epic",
        "defense_text": "40% Block Chance",
        "life_text": "⏳ 24 Hours",
        "description": "Protective gear. Gives a 40% chance to block any robbery attempt.",
    },
    "vibranium": {
        "name": "Vibranium",
        "title": "🛡️ Vibranium",
        "price": 1500000,
        "type": "armor",
        "power": 50,
        "rarity": "🟡 Legendary",
        "defense_text": "50% Block Chance",
        "life_text": "⏳ 24 Hours",
        "description": "Protective gear. Gives a 50% chance to block any robbery attempt.",
    },
    "forcefield": {
        "name": "Forcefield",
        "title": "🔮 Forcefield",
        "price": 3000000,
        "type": "armor",
        "power": 55,
        "rarity": "🟡 Legendary",
        "defense_text": "55% Block Chance",
        "life_text": "⏳ 24 Hours",
        "description": "Protective gear. Gives a 55% chance to block any robbery attempt.",
    },
    "plot_armor": {
        "name": "Plot Armor",
        "title": "🎬 Plot Armor",
        "price": 10000000,
        "type": "armor",
        "power": 60,
        "rarity": "🔴 GODLY",
        "defense_text": "60% Block Chance",
        "life_text": "⏳ 24 Hours",
        "description": "Literal Plot Armor. You cannot die. 60% Block.",
    },
}

PROTECT_COST = 1000
REVIVE_COST = 500
CLAIM_BONUS = 2000
DAILY_REWARD = 150


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _get_user(users, user_id: int) -> Dict:
    row = users.find_one({"user_id": user_id})
    if row is None:
        row = {
            "user_id": user_id,
            "username": None,
            "coins": 0,
            "streak": 0,
            "kills": 0,
            "last_daily": None,
            "last_claim": None,
            "shield_until": None,
            "dead_until": None,
            "inventory": {},
        }
        users.insert_one(row)
    return row


def _update_username(users, user_id: int, username: Optional[str]) -> None:
    if username:
        users.update_one({"user_id": user_id}, {"$set": {"username": username}})


def _load_inventory(row: Dict) -> Dict[str, int]:
    inv = row.get("inventory")
    return inv if isinstance(inv, dict) else {}


def _save_inventory(users, user_id: int, inv: Dict[str, int]) -> None:
    users.update_one({"user_id": user_id}, {"$set": {"inventory": inv}})


def _best_gear(inv: Dict[str, int]) -> tuple[Optional[Dict], Optional[Dict]]:
    weapon = None
    armor = None
    for key, data in SHOP_ITEMS.items():
        if inv.get(key, 0) <= 0:
            continue
        if data["type"] == "weapon":
            if not weapon or data["price"] > weapon["price"]:
                weapon = {"key": key, **data}
        if data["type"] == "armor":
            if not armor or data["price"] > armor["price"]:
                armor = {"key": key, **data}
    return weapon, armor


def _gear_power(inv: Dict[str, int]) -> int:
    weapon, armor = _best_gear(inv)
    return (weapon["power"] if weapon else 0) + (armor["power"] if armor else 0)


def _rank_for(coins: int) -> str:
    if coins >= 50000:
        return "Legend"
    if coins >= 20000:
        return "Elite"
    if coins >= 5000:
        return "Warrior"
    if coins >= 1000:
        return "Fighter"
    return "Rookie"


def _parse_iso(dt_str: Optional[str]) -> Optional[datetime]:
    if not dt_str:
        return None
    try:
        return datetime.fromisoformat(dt_str)
    except ValueError:
        return None


def _is_active(dt_str: Optional[str]) -> bool:
    dt = _parse_iso(dt_str)
    return bool(dt and dt > _utcnow())


async def _resolve_target(app: Client, message, args: list[str]):
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user
    if not args:
        return None
    target = args[-1]
    try:
        return await app.get_users(target)
    except Exception:
        return None


def register_economy(app: Client) -> None:
    _init_db()
    users = get_users_collection()

    ARMOR_KEYS = [
        "cloth",
        "leather",
        "chain",
        "riot_shield",
        "diamond",
        "obsidian",
        "nano_suit",
        "vibranium",
        "forcefield",
        "plot_armor",
    ]
    WEAPON_KEYS = [
        "stick",
        "brick",
        "slingshot",
        "knife",
        "bat",
        "axe",
        "hammer",
        "chainsaw",
        "pistol",
        "shotgun",
        "uzi",
        "katana",
        "ak_47",
        "minigun",
        "sniper",
        "rpg",
        "tank",
        "laser",
        "death_note",
    ]

    def _shop_main_text(user_name: str, coins: int) -> str:
        return (
            "🛒 𝐌𝐚𝐫𝐢𝐞 𝐌𝐚𝐫𝐤𝐞𝐭𝐩𝐥𝐚𝐜𝐞\n\n"
            f"👤 Customer: {user_name}\n"
            f"👛 Wallet: ${coins}\n\n"
            "Select a category to browse our goods!"
        )

    def _shop_main_markup() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🛡️ Amor", callback_data="shop_cat_armor"),
                    InlineKeyboardButton("⚔️ Weapon", callback_data="shop_cat_weapon"),
                ]
            ]
        )

    def _armor_list_text(coins: int, page: int, total_pages: int) -> str:
        return (
            "🛡️ 𝐃𝐞𝐟𝐞𝐧𝐬𝐞 𝐒𝐲𝐬𝐭𝐞𝐦𝐬\n"
            "Protection against thieves.\n\n"
            f"💰 Balance: ${coins}\n"
            f"📄 Page: {page + 1}/{total_pages}"
        )

    def _weapon_list_text(coins: int, page: int, total_pages: int) -> str:
        return (
            "⚔️ 𝐖𝐞𝐚𝐩𝐨𝐧 𝐒𝐲𝐬𝐭𝐞𝐦𝐬\n"
            "Choose your weapon.\n\n"
            f"💰 Balance: ${coins}\n"
            f"📄 Page: {page + 1}/{total_pages}"
        )

    def _weapon_item_text(item_key: str, coins: int, note: Optional[str] = None) -> str:
        item = SHOP_ITEMS[item_key]
        note_text = f"\n\n{note}" if note else ""
        title = item.get("title") or f"🛍️ {item['name']}"
        return (
            f"{title}\n"
            "━━━━━━━━━━━━━━━━━━\n"
            f"📖 {item['description']}\n"
            "━━━━━━━━━━━━━━━━━━\n"
            f"💰 Price: ${item['price']:,}\n"
            f"🌟 Rarity: {item['rarity']}\n"
            f"💥 Buff: {item['buff_text']}\n"
            f"⏱️ Life: {item['life_text']}\n\n"
            f"👛 Your Wallet: ${coins}"
            f"{note_text}"
        )

    def _weapon_item_markup(item_key: str, can_buy: bool) -> InlineKeyboardMarkup:
        rows = []
        if can_buy:
            rows.append([InlineKeyboardButton("✅ Buy", callback_data=f"shop_buy_{item_key}")])
        else:
            rows.append([InlineKeyboardButton("❌ Can't Afford", callback_data="shop_weapon_noop")])
        rows.append([InlineKeyboardButton("🔙 Back", callback_data="shop_cat_weapon")])
        return InlineKeyboardMarkup(rows)

    def _armor_list_markup(page: int) -> InlineKeyboardMarkup:
        page_size = 4
        total_pages = max(1, (len(ARMOR_KEYS) + page_size - 1) // page_size)
        page = max(0, min(page, total_pages - 1))

        start = page * page_size
        end = start + page_size
        page_keys = ARMOR_KEYS[start:end]

        rows = []
        row = []
        for key in page_keys:
            item = SHOP_ITEMS[key]
            row.append(InlineKeyboardButton(item["title"], callback_data=f"shop_armor_{key}"))
            if len(row) == 2:
                rows.append(row)
                row = []
        if row:
            rows.append(row)
        left_cb = f"shop_armor_page_{page - 1}" if page > 0 else "shop_armor_noop"
        right_cb = f"shop_armor_page_{page + 1}" if page < total_pages - 1 else "shop_armor_noop"
        rows.append(
            [
                InlineKeyboardButton("⬅️", callback_data=left_cb),
                InlineKeyboardButton("🔙 Back", callback_data="shop_back_main"),
                InlineKeyboardButton("➡️", callback_data=right_cb),
            ]
        )
        return InlineKeyboardMarkup(rows)

    def _weapon_list_markup(page: int) -> InlineKeyboardMarkup:
        page_size = 4
        total_pages = max(1, (len(WEAPON_KEYS) + page_size - 1) // page_size)
        page = max(0, min(page, total_pages - 1))

        start = page * page_size
        end = start + page_size
        page_keys = WEAPON_KEYS[start:end]

        rows = []
        row = []
        for key in page_keys:
            item = SHOP_ITEMS[key]
            label = item.get("title") or item["name"]
            row.append(InlineKeyboardButton(label, callback_data=f"shop_weapon_{key}"))
            if len(row) == 2:
                rows.append(row)
                row = []
        if row:
            rows.append(row)

        left_cb = f"shop_weapon_page_{page - 1}" if page > 0 else "shop_weapon_noop"
        right_cb = f"shop_weapon_page_{page + 1}" if page < total_pages - 1 else "shop_weapon_noop"
        rows.append(
            [
                InlineKeyboardButton("⬅️", callback_data=left_cb),
                InlineKeyboardButton("🔙 Back", callback_data="shop_back_main"),
                InlineKeyboardButton("➡️", callback_data=right_cb),
            ]
        )
        return InlineKeyboardMarkup(rows)

    def _armor_item_text(item_key: str, coins: int, note: Optional[str] = None) -> str:
        item = SHOP_ITEMS[item_key]
        note_text = f"\n\n{note}" if note else ""
        title = item.get("title") or f"🛍️ {item['name']}"
        return (
            f"{title}\n"
            "━━━━━━━━━━━━━━━━━━\n"
            f"📖 {item['description']}\n"
            "━━━━━━━━━━━━━━━━━━\n"
            f"💰 Price: ${item['price']:,}\n"
            f"🌟 Rarity: {item['rarity']}\n"
            f"🛡️ Defense: {item['defense_text']}\n"
            f"⏱️ Life: {item['life_text']}\n\n"
            f"👛 Your Wallet: ${coins}"
            f"{note_text}"
        )

    def _armor_item_markup(item_key: str, can_buy: bool) -> InlineKeyboardMarkup:
        rows = []
        if can_buy:
            rows.append([InlineKeyboardButton("✅ Buy", callback_data=f"shop_buy_{item_key}")])
        else:
            rows.append([InlineKeyboardButton("❌ Can't Afford", callback_data="shop_armor_noop")])
        rows.append([InlineKeyboardButton("🔙 Back", callback_data="shop_cat_armor")])
        return InlineKeyboardMarkup(rows)

    @app.on_message(filters.command("bal"))
    async def bal_cmd(_, message):
        target_user = message.from_user
        if message.reply_to_message and message.reply_to_message.from_user:
            target_user = message.reply_to_message.from_user
        if not target_user:
            return
        row = _get_user(users, target_user.id)
        _update_username(users, target_user.id, target_user.username)
        coins = row.get("coins", 0)
        inv = _load_inventory(row)
        kills = row.get("kills", 0)
        status = "💖 Alive"
        if _is_active(row.get("dead_until")):
            status = "💀 Dead"

        higher = users.count_documents({"coins": {"$gt": coins}})
        rank_num = higher + 1

        weapon, armor = _best_gear(inv)

        weapon_text = "None"
        if weapon:
            weapon_text = f"💥 {weapon['name']} (+40%)"
        armor_text = "None"
        if armor:
            armor_text = f"💎 {armor['name']} (30% Block)"

        await message.reply_text(
            "👤 User: {name}\n"
            "👛 Balance: ${coins}\n"
            "🏆 Rank: #{rank}\n"
            "❤️ Status: {status}\n"
            "⚔️ Kills: {kills}\n\n"
            "🎒 𝐀𝐜𝐭𝐢𝐯𝐞 𝐆𝐞𝐚𝐫:\n"
            "🗡️ Weapon: {weapon}\n"
            "🛡️ Armor: {armor}".format(
                name=(target_user.first_name or "User"),
                coins=coins,
                rank=rank_num,
                status=status,
                kills=kills,
                weapon=weapon_text,
                armor=armor_text,
            )
        )

    @app.on_message(filters.command("shop"))
    async def shop_cmd(_, message):
        user = message.from_user
        if not user:
            return
        row = _get_user(users, user.id)
        _update_username(users, user.id, user.username)
        coins = row.get("coins", 0)
        await message.reply_text(
            _shop_main_text(user.first_name or "𝐘ᴜᴛᴀ", coins),
            reply_markup=_shop_main_markup(),
        )

    @app.on_callback_query(filters.regex("^shop_back_main$"))
    async def shop_back_main_cb(_, callback_query):
        await callback_query.answer()
        user = callback_query.from_user
        if not user:
            return
        row = _get_user(users, user.id)
        _update_username(users, user.id, user.username)
        coins = row.get("coins", 0)
        await callback_query.message.edit_text(
            _shop_main_text(user.first_name or "𝐘ᴜᴛᴀ", coins),
            reply_markup=_shop_main_markup(),
        )

    @app.on_callback_query(filters.regex("^shop_cat_armor$"))
    async def shop_cat_armor_cb(_, callback_query):
        await callback_query.answer()
        user = callback_query.from_user
        if not user:
            return
        row = _get_user(users, user.id)
        _update_username(users, user.id, user.username)
        coins = row.get("coins", 0)
        total_pages = max(1, (len(ARMOR_KEYS) + 4 - 1) // 4)
        await callback_query.message.edit_text(
            _armor_list_text(coins, 0, total_pages),
            reply_markup=_armor_list_markup(0),
        )

    @app.on_callback_query(filters.regex("^shop_armor_page_(\\d+)$"))
    async def shop_armor_page_cb(_, callback_query):
        await callback_query.answer()
        user = callback_query.from_user
        if not user:
            return
        page = int(callback_query.data.split("_")[-1])
        row = _get_user(users, user.id)
        _update_username(users, user.id, user.username)
        coins = row.get("coins", 0)
        total_pages = max(1, (len(ARMOR_KEYS) + 4 - 1) // 4)
        await callback_query.message.edit_text(
            _armor_list_text(coins, page, total_pages),
            reply_markup=_armor_list_markup(page),
        )

    @app.on_callback_query(filters.regex("^shop_armor_noop$"))
    async def shop_armor_noop_cb(_, callback_query):
        await callback_query.answer()

    @app.on_callback_query(filters.regex("^shop_cat_weapon$"))
    async def shop_cat_weapon_cb(_, callback_query):
        await callback_query.answer()
        user = callback_query.from_user
        if not user:
            return
        row = _get_user(users, user.id)
        _update_username(users, user.id, user.username)
        coins = row.get("coins", 0)
        total_pages = max(1, (len(WEAPON_KEYS) + 4 - 1) // 4)
        await callback_query.message.edit_text(
            _weapon_list_text(coins, 0, total_pages),
            reply_markup=_weapon_list_markup(0),
        )

    @app.on_callback_query(filters.regex("^shop_weapon_page_(\\d+)$"))
    async def shop_weapon_page_cb(_, callback_query):
        await callback_query.answer()
        user = callback_query.from_user
        if not user:
            return
        page = int(callback_query.data.split("_")[-1])
        row = _get_user(users, user.id)
        _update_username(users, user.id, user.username)
        coins = row.get("coins", 0)
        total_pages = max(1, (len(WEAPON_KEYS) + 4 - 1) // 4)
        await callback_query.message.edit_text(
            _weapon_list_text(coins, page, total_pages),
            reply_markup=_weapon_list_markup(page),
        )

    @app.on_callback_query(filters.regex("^shop_weapon_noop$"))
    async def shop_weapon_noop_cb(_, callback_query):
        await callback_query.answer()

    @app.on_callback_query(filters.regex("^shop_weapon_(.+)$"))
    async def shop_weapon_item_cb(_, callback_query):
        await callback_query.answer()
        user = callback_query.from_user
        if not user:
            return
        match = callback_query.data.split("shop_weapon_", 1)[-1]
        if match not in SHOP_ITEMS or SHOP_ITEMS[match].get("type") != "weapon":
            return await callback_query.answer("Item not found.")
        row = _get_user(users, user.id)
        _update_username(users, user.id, user.username)
        coins = row.get("coins", 0)
        can_buy = coins >= SHOP_ITEMS[match]["price"]
        await callback_query.message.edit_text(
            _weapon_item_text(match, coins),
            reply_markup=_weapon_item_markup(match, can_buy),
        )

    @app.on_callback_query(filters.regex("^shop_armor_(.+)$"))
    async def shop_armor_item_cb(_, callback_query):
        await callback_query.answer()
        user = callback_query.from_user
        if not user:
            return
        match = callback_query.data.split("shop_armor_", 1)[-1]
        if match not in SHOP_ITEMS or SHOP_ITEMS[match].get("type") != "armor":
            return await callback_query.answer("Item not found.")
        row = _get_user(users, user.id)
        _update_username(users, user.id, user.username)
        coins = row.get("coins", 0)
        can_buy = coins >= SHOP_ITEMS[match]["price"]
        await callback_query.message.edit_text(
            _armor_item_text(match, coins),
            reply_markup=_armor_item_markup(match, can_buy),
        )

    @app.on_callback_query(filters.regex("^shop_buy_(.+)$"))
    async def shop_buy_item_cb(_, callback_query):
        await callback_query.answer()
        user = callback_query.from_user
        if not user:
            return
        item_key = callback_query.data.split("shop_buy_", 1)[-1]
        item = SHOP_ITEMS.get(item_key)
        if not item or item.get("type") not in {"armor", "weapon"}:
            return await callback_query.answer("Item not found.")
        row = _get_user(users, user.id)
        _update_username(users, user.id, user.username)
        coins = row.get("coins", 0)
        if coins < item["price"]:
            if item["type"] == "armor":
                await callback_query.message.edit_text(
                    _armor_item_text(item_key, coins, note="❌ Not enough money."),
                    reply_markup=_armor_item_markup(item_key, False),
                )
            else:
                await callback_query.message.edit_text(
                    _weapon_item_text(item_key, coins, note="❌ Not enough money."),
                    reply_markup=_weapon_item_markup(item_key, False),
                )
            return

        users.update_one(
            {"user_id": user.id},
            {"$inc": {"coins": -item["price"]}},
        )
        inv = _load_inventory(row)
        inv[item_key] = inv.get(item_key, 0) + 1
        _save_inventory(users, user.id, inv)
        new_coins = coins - item["price"]
        if item["type"] == "armor":
            await callback_query.message.edit_text(
                _armor_item_text(item_key, new_coins, note="✅ Purchased."),
                reply_markup=_armor_item_markup(item_key, False),
            )
        else:
            await callback_query.message.edit_text(
                _weapon_item_text(item_key, new_coins, note="✅ Purchased."),
                reply_markup=_weapon_item_markup(item_key, False),
            )

    @app.on_message(filters.command("give"))
    async def give_cmd(app: Client, message):
        args = message.text.split()
        if len(args) < 2:
            return await message.reply_text("Usage: /give <amount> <user or reply>")
        try:
            amount = int(args[1])
        except ValueError:
            return await message.reply_text("Amount must be a number.")
        if amount <= 0:
            return await message.reply_text("Amount must be positive.")

        target = await _resolve_target(app, message, args)
        if not target or not target.id:
            return await message.reply_text("Could not find that user. Reply to them or use @username.")
        if target.id == message.from_user.id:
            return await message.reply_text("You can't give coins to yourself.")

        tax = int(amount * 0.10)
        receive_amount = amount - tax

        sender = _get_user(users, message.from_user.id)
        if sender.get("coins", 0) < amount:
            return await message.reply_text("Not enough coins.")
        _get_user(users, target.id)
        users.update_one(
            {"user_id": message.from_user.id},
            {"$inc": {"coins": -amount}},
        )
        users.update_one(
            {"user_id": target.id},
            {"$inc": {"coins": receive_amount}},
        )

        await message.reply_text(
            f"Sent {receive_amount} coins to {target.first_name}. (Tax: {tax})"
        )

    @app.on_message(filters.command("claim"))
    async def claim_cmd(_, message):
        user = message.from_user
        if not user:
            return
        now = _utcnow()
        row = _get_user(users, user.id)
        last_claim = _parse_iso(row.get("last_claim"))
        if last_claim and now - last_claim < timedelta(hours=24):
            remaining = timedelta(hours=24) - (now - last_claim)
            hours = int(remaining.total_seconds() // 3600)
            return await message.reply_text(f"Claim cooldown: {hours}h left.")
        users.update_one(
            {"user_id": user.id},
            {"$inc": {"coins": CLAIM_BONUS}, "$set": {"last_claim": now.isoformat()}},
        )
        await message.reply_text(f"Group bonus claimed! +{CLAIM_BONUS} coins.")

    @app.on_message(filters.command("daily"))
    async def daily_cmd(_, message):
        user = message.from_user
        if not user:
            return
        now = _utcnow()
        row = _get_user(users, user.id)
        last_daily = _parse_iso(row.get("last_daily"))
        if last_daily and now - last_daily < timedelta(hours=24):
            remaining = timedelta(hours=24) - (now - last_daily)
            hours = int(remaining.total_seconds() // 3600)
            return await message.reply_text(f"Daily cooldown: {hours}h left.")

        reward = DAILY_REWARD
        users.update_one(
            {"user_id": user.id},
            {
                "$inc": {"coins": reward},
                "$set": {"last_daily": now.isoformat()},
            },
        )
        await message.reply_text(
            f"Daily reward claimed! +{reward} coins."
        )

    @app.on_message(filters.command("ranking"))
    async def ranking_cmd(_, message):
        rows = list(users.find({}, {"user_id": 1, "username": 1, "coins": 1}).sort("coins", -1).limit(10))

        if not rows:
            return await message.reply_text("No rankings yet.")

        lines = []
        for idx, row in enumerate(rows, 1):
            name = row.get("username") or f"User {row.get('user_id')}"
            lines.append(f"{idx}. {name} — {row.get('coins', 0)} coins")

        await message.reply_text("Global Leaderboard:\n" + "\n".join(lines))

    @app.on_message(filters.command("protect"))
    async def protect_cmd(_, message):
        user = message.from_user
        if not user:
            return
        now = _utcnow()
        shield_until = (now + timedelta(days=1)).isoformat()

        partner = None
        if message.reply_to_message and message.reply_to_message.from_user:
            partner = message.reply_to_message.from_user

        row = _get_user(users, user.id)
        if row.get("coins", 0) < PROTECT_COST:
            return await message.reply_text("Not enough coins for protection.")
        users.update_one(
            {"user_id": user.id},
            {"$inc": {"coins": -PROTECT_COST}, "$set": {"shield_until": shield_until}},
        )
        if partner and partner.id != user.id:
            _get_user(users, partner.id)
            users.update_one(
                {"user_id": partner.id},
                {"$set": {"shield_until": shield_until}},
            )

        if partner:
            await message.reply_text(
                f"Shield active for you and {partner.first_name} for 1 day."
            )
        else:
            await message.reply_text("Shield active for 1 day.")

    @app.on_message(filters.command("revive"))
    async def revive_cmd(_, message):
        user = message.from_user
        if not user:
            return
        row = _get_user(users, user.id)
        if not _is_active(row.get("dead_until")):
            return await message.reply_text("You're already alive.")
        if row.get("coins", 0) < REVIVE_COST:
            return await message.reply_text("Not enough coins to revive.")
        users.update_one(
            {"user_id": user.id},
            {"$inc": {"coins": -REVIVE_COST}, "$set": {"dead_until": None}},
        )
        await message.reply_text("Revived instantly.")

    @app.on_message(filters.command("kill"))
    async def kill_cmd(app: Client, message):
        user = message.from_user
        if not user:
            return
        target = await _resolve_target(app, message, message.text.split())
        if not target:
            return await message.reply_text("Usage: /kill <user or reply>")
        if target.id == user.id:
            return await message.reply_text("Try someone else.")

        now = _utcnow()
        attacker = _get_user(users, user.id)
        if _is_active(attacker.get("dead_until")):
            return await message.reply_text("You're dead. Use /revive.")

        victim = _get_user(users, target.id)
        if _is_active(victim.get("shield_until")):
            return await message.reply_text("Target is protected by a shield.")
        if _is_active(victim.get("dead_until")):
            return await message.reply_text("💀 Victim is already dead!")
        attacker_power = _gear_power(_load_inventory(attacker))
        victim_power = _gear_power(_load_inventory(victim))
        if victim_power > attacker_power:
            return await message.reply_text("Target has stronger gear. You can't kill them.")

        users.update_one(
            {"user_id": target.id},
            {"$set": {"dead_until": (now + timedelta(hours=12)).isoformat()}},
        )

        kill_reward = random.randint(100, 170)
        users.update_one(
            {"user_id": user.id},
            {"$inc": {"coins": kill_reward, "kills": 1}},
        )

        await message.reply_text(
            f"👤 {user.first_name} killed {target.first_name}\n"
            f"💰 Earned: ${kill_reward}"
        )

    @app.on_message(filters.command("rob"))
    async def rob_cmd(app: Client, message):
        user = message.from_user
        if not user:
            return
        args = message.text.split()
        if len(args) < 2:
            return await message.reply_text("Usage: /rob <amount> <user or reply>")
        try:
            desired = int(args[1])
        except ValueError:
            return await message.reply_text("Amount must be a number.")
        if desired <= 0:
            return await message.reply_text("Amount must be positive.")

        target = await _resolve_target(app, message, args)
        if not target or target.id == user.id:
            return await message.reply_text("Pick a valid target.")

        attacker = _get_user(users, user.id)
        if _is_active(attacker.get("dead_until")):
            return await message.reply_text("You're dead. Use /revive.")

        victim = _get_user(users, target.id)
        if _is_active(victim.get("shield_until")):
            return await message.reply_text("Target is protected by a shield.")
        attacker_power = _gear_power(_load_inventory(attacker))
        victim_power = _gear_power(_load_inventory(victim))
        if victim_power > attacker_power:
            return await message.reply_text("Target has stronger gear. You can't rob them.")

        if victim.get("coins", 0) <= 0:
            return await message.reply_text("Target has no coins.")

        success = random.random() < 0.6
        if not success:
            return await message.reply_text("Rob failed. Better luck next time.")

        amount = min(desired, max(1, int(victim.get("coins", 0) * random.uniform(0.05, 0.15))))
        users.update_one(
            {"user_id": target.id},
            {"$inc": {"coins": -amount}},
        )
        users.update_one(
            {"user_id": user.id},
            {"$inc": {"coins": amount}},
        )

        await message.reply_text(
            f"Rob successful! Stole {amount} coins from {target.first_name}."
        )
