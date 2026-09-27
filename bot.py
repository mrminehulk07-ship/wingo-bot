import os
import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile

# ==================== CONFIGURATION ====================
BOT_TOKEN = "8772775679:AAFNhAS8fAflvpa6qk0hQQ0GHXmGAfNkr6E"

DEFAULT_PHOTO_URL = "https://images.unsplash.com/photo-1518609878373-06d740f60d8b?w=800"

# --- STEP 1: TOP 4 CHANNELS (2x2 Grid) ---
TOP_4_CHANNELS = [
    {"name": "📢 Join 1 ↗️", "url": "https://t.me/+miAnzdPVlNA5M2U1", "id": -1004447397342},
    {"name": "📢 Join 2 ↗️", "url": "https://t.me/+cSAjB1XCsN40MzY1", "id": -1003759197616},
    {"name": "📢 Join 3 ↗️", "url": "https://t.me/+XMExpGdJ06hjMmZl", "id": -1003965694341},
    {"name": "📢 Join 4 ↗️", "url": "https://t.me/+t7dCpQb5p0U2MWJl", "id": -1002107968004}
]

# --- STEP 2: REMAINING CHANNELS (5, 6, 7) ---
REMAINING_CHANNELS = [
    {"name": "📢 Channel 5 ↗️", "url": "https://t.me/SaahoTricks", "id": -1002907609430},
    {"name": "📢 Channel 6 ↗️", "url": "https://t.me/code91areas", "id": -1002072638055},
    {"name": "📢 Channel 7 ↗️", "url": "https://t.me/+evlayNwyI_EzOWM1", "id": -1002175836786}
]

# --- FINAL 8TH LINK (Destination Voucher Request Link) ---
FINAL_8TH_LINK = "https://t.me/+_hlE6fwQ0nJiZjdl"

# =======================================================

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Pending Join Requests ko track karne ke liye
user_requests = {}

# --- JOIN REQUEST LISTENER ---
@dp.chat_join_request()
async def handle_join_request(event: types.ChatJoinRequest):
    user_id = event.from_user.id
    chat_id = event.chat.id
    if user_id not in user_requests:
        user_requests[user_id] = set()
    user_requests[user_id].add(chat_id)
    logging.info(f"Join Request Detected: User {user_id} in Chat {chat_id}")

# --- STRICT VERIFICATION FUNCTION ---
async def check_user_joined(user_id: int, chat_id: int) -> bool:
    if not chat_id:
        return True

    # 1. Check karo agar Join Request bheji hui hai
    if user_id in user_requests and chat_id in user_requests[user_id]:
        return True

    # 2. Check karo agar already Member / Admin hai
    try:
        member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
        if member.status in ["member", "administrator", "creator", "restricted"]:
            return True
    except Exception as e:
        logging.error(f"Error checking {chat_id}: {e}")

    return False

# --- 2x2 GRID KEYBOARDS ---

def get_step1_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(text=TOP_4_CHANNELS[0]["name"], url=TOP_4_CHANNELS[0]["url"]),
            InlineKeyboardButton(text=TOP_4_CHANNELS[1]["name"], url=TOP_4_CHANNELS[1]["url"])
        ],
        [
            InlineKeyboardButton(text=TOP_4_CHANNELS[2]["name"], url=TOP_4_CHANNELS[2]["url"]),
            InlineKeyboardButton(text=TOP_4_CHANNELS[3]["name"], url=TOP_4_CHANNELS[3]["url"])
        ],
        [
            InlineKeyboardButton(text="🔓 Continue To Step 2 🔓", callback_data="goto_step2")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_step2_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(text=REMAINING_CHANNELS[0]["name"], url=REMAINING_CHANNELS[0]["url"]),
            InlineKeyboardButton(text=REMAINING_CHANNELS[1]["name"], url=REMAINING_CHANNELS[1]["url"])
        ],
        [
            InlineKeyboardButton(text=REMAINING_CHANNELS[2]["name"], url=REMAINING_CHANNELS[2]["url"])
        ],
        [
            InlineKeyboardButton(text="🎁 Get Voucher & Promo Code 🎁", callback_data="claim_voucher")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# --- PHOTO SENDER HELPER ---
async def send_welcome_photo(chat_id, caption, reply_markup):
    if os.path.exists("banner.jpg"):
        photo = FSInputFile("banner.jpg")
    else:
        photo = DEFAULT_PHOTO_URL

    try:
        await bot.send_photo(
            chat_id=chat_id,
            photo=photo,
            caption=caption,
            reply_markup=reply_markup,
            parse_mode="Markdown"
