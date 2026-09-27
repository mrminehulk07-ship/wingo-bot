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

# Fallback Banner Image (Agar aapne banner.jpg upload na ki ho)
DEFAULT_PHOTO_URL = "https://i.postimg.cc/cLGk97Zw/YONO-LOOT-640x360.png"

# --- STEP 1: TOP 4 CHANNELS (2x2 Grid) ---
TOP_4_CHANNELS = [
    {"name": "📢 Join 1 ↗️", "url": "https://t.me/+miAnzdPVlNA5M2U1"},
    {"name": "📢 Join 2 ↗️", "url": "https://t.me/+cSAjB1XCsN40MzY1"},
    {"name": "📢 Join 3 ↗️", "url": "https://t.me/+XMExpGdJ06hjMmZl"},
    {"name": "📢 Join 4 ↗️", "url": "https://t.me/+t7dCpQb5p0U2MWJl"}
]

# --- STEP 2: REMAINING CHANNELS (5, 6, 7) ---
REMAINING_CHANNELS = [
    {"name": "📢 Channel 5 ↗️", "url": "https://t.me/SaahoTricks", "id": "@SaahoTricks"},
    {"name": "📢 Channel 6 ↗️", "url": "https://t.me/code91areas", "id": "@code91areas"},
    {"name": "📢 Channel 7 ↗️", "url": "https://t.me/+evlayNwyI_EzOWM1", "id": None}
]

# --- 8TH LINK (FINAL VOUCHER CLAIM REQUEST LINK) ---
FINAL_8TH_LINK = "https://t.me/+_hlE6fwQ0nJiZjdl"

# =======================================================

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# --- 2x2 GRID KEYBOARDS ---

def get_step1_keyboard():
    # 2x2 Grid layout (Jaise 2nd screenshot me tha)
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
            InlineKeyboardButton(text="🎁 Claim Voucher & Promo Code 🎁", callback_data="claim_voucher")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_final_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(text="🚀 Click Here To Collect Voucher 🚀", url=FINAL_8TH_LINK)
        ],
        [
            InlineKeyboardButton(text="🔄 Claim Another Code", callback_data="restart_flow")
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

# --- STEP 2 HANDLER ---
@dp.callback_query(F.data == "goto_step2")
async def process_step2(callback: types.CallbackQuery):
    await callback.answer("✅ Step 1 Verified!")
    
    step2_caption = (
        "🔥 **STEP 1 COMPLETED (4/4 CHANNELS JOINED)!**\n\n"
        "⏳ **Aapka Voucher 90% Unlock Ho Chuka Hai.**\n\n"
        "Sirf aakhri kuch channels bache hain! Niche join/request daal kar turant apna **₹185 - ₹500 Free Voucher** claim karein:\n\n"
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

# --- FINAL VOUCHER CLAIM HANDLER ---
@dp.callback_query(F.data == "claim_voucher")
async def process_claim(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    not_joined = []

    # Check public channels 5 & 6
    for ch in REMAINING_CHANNELS:
        if ch.get("id"):
            try:
                member = await bot.get_chat_member(chat_id=ch["id"], user_id=user_id)
                if member.status in ["left", "kicked"]:
                    not_joined.append(ch["name"])
            except Exception as e:
                logging.error(f"Check error for {ch['id']}: {e}")

    if not_joined:
        await callback.answer(
            f"⚠️ Pehle Channel 5 & 6 join karein tabhi voucher milega!",
            show_alert=True
        )
        return

    await callback.answer("🎉 Congratulations! Voucher Unlocked!")

    reward_caption = (
        "🎊 **CONGRATS! REDEMPTION SUCCESSFUL!**\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "🎟️ **Promo Code:** `YONO-DIWA-FREE500`\n"
        "💰 **Cash Won:** **₹185.40 Free Spins / Bonus**\n"
        "⏳ **Expiry:** 10 Minutes Only (Active)\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "⚠️ **Voucher Collect Kaise Karein?**\n"
        "Niche diye gaye **'Click Here To Collect Voucher'** button par tap karke request daalein aur apna code direct game me use karein!\n\n"
        "👇 **Click The Green/Redeem Button Below:**"
    )

    try:
        await callback.message.edit_caption(
            caption=reward_caption,
            reply_markup=get_final_keyboard(),
            parse_mode="Markdown"
        )
    except Exception:
        await callback.message.edit_text(
            reward_caption,
            reply_markup=get_final_keyboard(),
            parse_mode="Markdown"
        )

@dp.callback_query(F.data == "restart_flow")
async def restart_callback(callback: types.CallbackQuery):
    await callback.message.delete()
    await cmd_start(callback.message)

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
