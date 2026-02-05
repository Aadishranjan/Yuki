"""Economy + RPG commands for Yuki bot."""
from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

from pyrogram import Client, filters

from database.db import get_users_collection, init_db as _init_db

SHOP_ITEMS = {
    "dagger": {"name": "Dagger", "price": 500, "type": "weapon", "power": 10},
    "katana": {"name": "Katana", "price": 2500, "type": "weapon", "power": 25},
    "blaster": {"name": "Blaster", "price": 7000, "type": "weapon", "power": 45},
    "leather_armor": {"name": "Leather Armor", "price": 800, "type": "armor", "power": 8},
    "chainmail": {"name": "Chainmail", "price": 3500, "type": "armor", "power": 20},
    "titan_armor": {"name": "Titan Armor", "price": 12000, "type": "armor", "power": 40},
    "medkit": {"name": "Medkit", "price": 300, "type": "item", "power": 0},
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
        args = message.text.split()
        if len(args) >= 3 and args[1].lower() == "buy":
            item_key = args[2].lower()
            item = SHOP_ITEMS.get(item_key)
            if not item:
                return await message.reply_text("Item not found. Use /shop to see items.")
            user = message.from_user
            if not user:
                return
            row = _get_user(users, user.id)
            _update_username(users, user.id, user.username)
            if row.get("coins", 0) < item["price"]:
                return await message.reply_text("Not enough coins.")
            users.update_one(
                {"user_id": user.id},
                {"$inc": {"coins": -item["price"]}},
            )
            inv = _load_inventory(row)
            inv[item_key] = inv.get(item_key, 0) + 1
            _save_inventory(users, user.id, inv)
            return await message.reply_text(
                f"Purchased {item['name']} for {item['price']} coins."
            )

        items_list = "\n".join(
            f"- {v['name']} ({v['type']}) — {v['price']} coins"
            for v in SHOP_ITEMS.values()
        )
        await message.reply_text(
            "Shop items:\n"
            f"{items_list}\n\n"
            "To buy: /shop buy <item_key>\n"
            "Example: /shop buy katana"
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
