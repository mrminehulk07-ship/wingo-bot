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

DEFAULT_PHOTO_URL = "https://i.postimg.cc/cLGk97Zw/YONO-LOOT-640x360.png"

# --- STEP 1: TOP 4 CHANNELS (With Exact IDs) ---
TOP_4_CHANNELS = [
    {"name": "📢 Join 1 ↗️", "url": "https://t.me/+miAnzdPVlNA5M2U1", "id": -1004447397342},
    {"name": "📢 Join 2 ↗️", "url": "https://t.me/+cSAjB1XCsN40MzY1", "id": -1003759197616},
    {"name": "📢 Join 3 ↗️", "url": "https://t.me/+XMExpGdJ06hjMmZl", "id": -1003965694341},
    {"name": "📢 Join 4 ↗️", "url": "https://t.me/+t7dCpQb5p0U2MWJl", "id": -1002107968004}
]

# --- STEP 2: REMAINING CHANNELS (With Exact IDs) ---
REMAINING_CHANNELS = [
    {"name": "📢 Channel 5 ↗️", "url": "https://t.me/SaahoTricks", "id": -1002907609430},
    {"name": "📢 Channel 6 ↗️", "url": "https://t.me/code91areas", "id": -1002072638055},
    {"name": "📢 Channel 7 ↗️", "url": "https://t.me/+evlayNwyI_EzOWM1", "id": -1002175836786}
]

# --- FINAL 8TH LINK (Destination Voucher Link) ---
FINAL_8TH_LINK = "https://t.me/+_hlE6fwQ0nJiZjdl"

# =======================================================

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Pending Join Requests ko track karne ke liye
user_requests = {}

# --- JOIN REQUEST LISTENER (Agar banda request dale toh detect kare) ---
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
        )
    except Exception as e:
        logging.error(f"Photo send error: {e}")
        await bot.send_message(
            chat_id=chat_id,
            text=caption,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

# --- COMMAND /START ---
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    caption = (
        "🎉 **Welcome To Official Promo Codes & Voucher Center..!!!**\n\n"
        "🚀 **Click The Buttons Below To Claim Your Voucher**\n\n"
        "🤑 **Per Account ( ₹100 - ₹500 Free )**\n"
        "🎰 **Game:** All Yono & Slots Official Vouchers\n"
        "⚡ **Status:** Active & Verified ✅\n\n"
        "👇 *Step 1: Niche diye gaye 4 Channels me join/request daalein:*"
    )
    await send_welcome_photo(message.chat.id, caption, get_step1_keyboard())

# --- STEP 2 HANDLER (STRICT VERIFICATION FOR TOP 4) ---
@dp.callback_query(F.data == "goto_step2")
async def process_step2(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    not_joined = []

    for ch in TOP_4_CHANNELS:
        is_joined = await check_user_joined(user_id, ch["id"])
        if not is_joined:
            not_joined.append(ch["name"])

    # Agar banda join/request nahi kiya:
    if not_joined:
        await callback.answer(
            f"❌ Access Denied!\nAapne {len(not_joined)} channels join/request nahi kiye.\nPehle upar ke 4 channels join karein!",
            show_alert=True
        )
        return

    await callback.answer("✅ Step 1 Verified!")
    
    step2_caption = (
        "🔥 **STEP 1 COMPLETED (4/4 CHANNELS JOINED)!**\n\n"
        "⏳ **Aapka Voucher 90% Unlock Ho Chuka Hai.**\n\n"
        "Sirf aakhri 3 channels bache hain! Niche join/request daal kar turant apna **Voucher & Promo Code** claim karein:\n\n"
        "👇 *Niche diye gaye channels join karein:*"
    )

    try:
        await callback.message.edit_caption(
            caption=step2_caption,
            reply_markup=get_step2_keyboard(),
            parse_mode="Markdown"
        )
    except Exception:
        await callback.message.edit_text(
            step2_caption,
            reply_markup=get_step2_keyboard(),
            parse_mode="Markdown"
        )

# --- FINAL CLAIM HANDLER (STRICT VERIFICATION FOR 5, 6, 7) ---
@dp.callback_query(F.data == "claim_voucher")
async def process_claim(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    not_joined = []

    for ch in REMAINING_CHANNELS:
        is_joined = await check_user_joined(user_id, ch["id"])
        if not is_joined:
            not_joined.append(ch["name"])

    if not_joined:
        await callback.answer(
            f"❌ Access Denied!\nPehle Step 2 ke baki channels join/request karein!",
            show_alert=True
        )
        return

    await callback.answer("🎉 Verification Successful!")

    # Purana lamba message delete
    try:
        await callback.message.delete()
    except Exception:
        pass

    # Naya fresh message with intense FOMO
    reward_text = (
        "🎁 **HERE IS YOUR VOUCHER & PROMO CODE!** 🎁\n\n"
        "⚡ **Official VIP Promo Code & Free Cash Voucher agle 10 MINUTES me niche diye gaye VIP Channel me drop hone wala hai!**\n\n"
        "⚠️ **Fast Join:** Ye code sirf **First 500 Active Users** ke liye valid hoga. Jaldi se niche click karke Join Request daalein taaki code aate hi aap claim kar sakein!\n\n"
        "👇 **Click Below & Send Join Request Now:**"
    )

    final_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🚀 FAST JOIN VIP CHANNEL (CODE IN 10M) 🚀", url=FINAL_8TH_LINK)
        ]
    ])

    await callback.message.answer(
        text=reward_text,
        reply_markup=final_keyboard,
        parse_mode="Markdown"
    )

# Render Keep-Alive Server
async def handle_ping(request):
    return web.Response(text="Yono Diwa Voucher Bot is Running!")

async def main():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print("Bot is starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
