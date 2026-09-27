import os
import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile

# ==================== CONFIGURATION ====================
BOT_TOKEN = "8772775679:AAFNhAS8fAflvpa6qk0hQQ0GHXmGAfNkr6E"
DEFAULT_PHOTO = "https://i.postimg.cc/cLGk97Zw/YONO-LOOT-640x360.png"

CHANNELS_S1 = [
    {"name": "📢 Join 1 ↗️", "url": "https://t.me/+miAnzdPVlNA5M2U1", "id": -1004447397342},
    {"name": "📢 Join 2 ↗️", "url": "https://t.me/+cSAjB1XCsN40MzY1", "id": -1003759197616},
    {"name": "📢 Join 3 ↗️", "url": "https://t.me/+XMExpGdJ06hjMmZl", "id": -1003965694341},
    {"name": "📢 Join 4 ↗️", "url": "https://t.me/+t7dCpQb5p0U2MWJl", "id": -1002107968004}
]

CHANNELS_S2 = [
    {"name": "📢 Channel 5 ↗️", "url": "https://t.me/SaahoTricks", "id": -1002907609430},
    {"name": "📢 Channel 6 ↗️", "url": "https://t.me/code91areas", "id": -1002072638055},
    {"name": "📢 Channel 7 ↗️", "url": "https://t.me/+evlayNwyI_EzOWM1", "id": -1002175836786}
]

FINAL_LINK = "https://t.me/+_hlE6fwQ0nJiZjdl"

# =======================================================

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
user_requests = {}

@dp.chat_join_request()
async def on_join_req(event: types.ChatJoinRequest):
    if event.from_user.id not in user_requests:
        user_requests[event.from_user.id] = set()
    user_requests[event.from_user.id].add(event.chat.id)

async def is_joined(user_id: int, chat_id: int) -> bool:
    if user_id in user_requests and chat_id in user_requests[user_id]:
        return True
    try:
        m = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
        if m.status in ["member", "administrator", "creator", "restricted"]:
            return True
    except Exception:
        pass
    return False

def kb_s1():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=CHANNELS_S1[0]["name"], url=CHANNELS_S1[0]["url"]), InlineKeyboardButton(text=CHANNELS_S1[1]["name"], url=CHANNELS_S1[1]["url"])],
        [InlineKeyboardButton(text=CHANNELS_S1[2]["name"], url=CHANNELS_S1[2]["url"]), InlineKeyboardButton(text=CHANNELS_S1[3]["name"], url=CHANNELS_S1[3]["url"])],
        [InlineKeyboardButton(text="🔓 Continue To Step 2 🔓", callback_data="step2")]
    ])

def kb_s2():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=CHANNELS_S2[0]["name"], url=CHANNELS_S2[0]["url"]), InlineKeyboardButton(text=CHANNELS_S2[1]["name"], url=CHANNELS_S2[1]["url"])],
        [InlineKeyboardButton(text=CHANNELS_S2[2]["name"], url=CHANNELS_S2[2]["url"])],
        [InlineKeyboardButton(text="🎁 Get Voucher & Promo Code 🎁", callback_data="claim")]
    ])

@dp.message(CommandStart())
async def start(msg: types.Message):
    caption = (
        "🎉 **Welcome To Official Promo Codes & Voucher Center..!!!**\n\n"
        "🚀 **Click The Buttons Below To Claim Your Voucher**\n\n"
        "🤑 **Per Account ( ₹100 - ₹500 Free )**\n"
        "🎰 **Game:** All Yono & Slots Official Vouchers\n"
        "⚡ **Status:** Active & Verified ✅\n\n"
        "👇 *Step 1: Niche diye gaye 4 Channels me join/request daalein:*"
    )
    photo = FSInputFile("banner.jpg") if os.path.exists("banner.jpg") else DEFAULT_PHOTO
    try:
        await msg.answer_photo(photo=photo, caption=caption, reply_markup=kb_s1(), parse_mode="Markdown")
    except Exception:
        await msg.answer(caption, reply_markup=kb_s1(), parse_mode="Markdown")

@dp.callback_query(F.data == "step2")
async def step2_handler(cb: types.CallbackQuery):
    uid = cb.from_user.id
    for ch in CHANNELS_S1:
        if not await is_joined(uid, ch["id"]):
            await cb.answer("❌ Access Denied!\nPehle upar ke 4 channels join karein!", show_alert=True)
            return
    await cb.answer("✅ Step 1 Verified!")
    text = (
        "🔥 **STEP 1 COMPLETED (4/4 CHANNELS JOINED)!**\n\n"
        "⏳ **Aapka Voucher 90% Unlock Ho Chuka Hai.**\n\n"
        "Sirf aakhri 3 channels bache hain! Niche join/request daal kar turant apna **Voucher & Promo Code** claim karein:\n\n"
        "👇 *Niche diye gaye channels join karein:*"
    )
    try:
        await cb.message.edit_caption(caption=text, reply_markup=kb_s2(), parse_mode="Markdown")
    except Exception:
        await cb.message.edit_text(text, reply_markup=kb_s2(), parse_mode="Markdown")

@dp.callback_query(F.data == "claim")
async def claim_handler(cb: types.CallbackQuery):
    uid = cb.from_user.id
    for ch in CHANNELS_S2:
        if not await is_joined(uid, ch["id"]):
            await cb.answer("❌ Access Denied!\nPehle Step 2 ke baki channels join/request karein!", show_alert=True)
            return
    await cb.answer("🎉 Verification Successful!")
    try:
        await cb.message.delete()
    except Exception:
        pass
    reward_text = (
        "🎁 **HERE IS YOUR VOUCHER & PROMO CODE!** 🎁\n\n"
        "⚡ **Official VIP Promo Code & Free Cash Voucher agle 10 MINUTES me niche diye gaye VIP Channel me drop hone wala hai!**\n\n"
        "⚠️ **Fast Join:** Ye code sirf **First 500 Active Users** ke liye valid hoga. Jaldi se niche click karke Join Request daalein taaki code aate hi aap claim kar sakein!\n\n"
        "👇 **Click Below & Send Join Request Now:**"
    )
    kb_final = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🚀 FAST JOIN VIP CHANNEL (CODE IN 10M) 🚀", url=FINAL_LINK)]])
    await cb.message.answer(reward_text, reply_markup=kb_final, parse_mode="Markdown")

async def handle_ping(request):
    return web.Response(text="Bot is running!")

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
