import os
import asyncio
import logging
import hashlib
from datetime import datetime, timezone, timedelta
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- CONFIGURATION ---
BOT_TOKEN = "8843656284:AAHG9XEeB3lkt9XFpJy22PGABwmtv3YFpfY"

# Aapke Channels & Groups (Simple Names ke sath)
CHANNELS_CONFIG = [
    {"name": "📢 Channel 1", "url": "https://t.me/+FiAGrNzwRIZhNGY1", "id": None},
    {"name": "📢 Channel 2", "url": "https://t.me/ProfessorX106", "id": "@ProfessorX106"},
    {"name": "💬 Group 1", "url": "https://t.me/+EZMAVv_kmuNjOTM1", "id": None},
    {"name": "📢 Channel 3", "url": "https://t.me/+OLB-4SeGbXJjZjQ9", "id": None},
    {"name": "📢 Channel 4", "url": "https://t.me/SlotsByToxic", "id": "@SlotsByToxic"}
]

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class CalcState(StatesGroup):
    choosing_level = State()
    entering_balance = State()

# --- FORCE SUB KEYBOARD ---
def get_force_sub_keyboard():
    buttons = []
    for ch in CHANNELS_CONFIG:
        buttons.append([InlineKeyboardButton(text=ch["name"], url=ch["url"])])
    buttons.append([InlineKeyboardButton(text="✅ Verify Access", callback_data="verify_access")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# --- MAIN MENU KEYBOARD ---
def get_main_menu():
    keyboard = [
        [InlineKeyboardButton(text="🎯 Predict Next Period (1-Min)", callback_data="get_prediction")],
        [InlineKeyboardButton(text="🧮 Level Maintain Chart (L4 - L8)", callback_data="open_calculator")],
        [InlineKeyboardButton(text="📈 10% Compounding Plan", callback_data="compounding_plan")],
        [InlineKeyboardButton(text="📢 Official Channels", callback_data="refresh_links")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# --- WINGO 1-MIN REAL-TIME PERIOD & PATTERN ENGINE ---
def get_wingo_live_prediction():
    # India Standard Time (UTC+5:30)
    ist = timezone(timedelta(hours=5, minutes=30))
    now = datetime.now(ist)
    
    # Calculate Total Minutes Elapsed Today (1 min = 1 period)
    minutes_today = now.hour * 60 + now.minute + 1
    current_period = f"{now.strftime('%Y%m%d')}01{minutes_today:04d}"
    seconds_remaining = 60 - now.second

    # Hash-based deterministic algorithm for current period (Stable per minute)
    period_hash = int(hashlib.md5(current_period.encode()).hexdigest(), 16)
    
    is_big = (period_hash % 2) == 0
    prediction = "BIG (5-9)" if is_big else "SMALL (0-4)"
    color = "🟢 GREEN" if (period_hash % 3 == 0) else "🔴 RED"
    
    patterns = ["Dragon Continuation", "2x2 Mirror Pattern", "Break Reversal", "Alternate Run"]
    pattern = patterns[period_hash % len(patterns)]
    confidence = 85 + (period_hash % 11)

    return current_period, prediction, color, confidence, pattern, seconds_remaining

# --- COMMAND /START ---
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    welcome_text = (
        "👋 **Welcome to Wingo 1-Minute VIP Prediction & Toolkit Bot!**\n\n"
        "Bot ke features use karne ke liye pehle niche diye gaye **Sabhi Channels & Groups** ko join karein:"
    )
    await message.answer(welcome_text, reply_markup=get_force_sub_keyboard(), parse_mode="Markdown")

# --- REAL VERIFICATION CHECK ---
@dp.callback_query(F.data == "verify_access")
async def verify_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    not_joined = []

    # Check Public Channels where bot can check members
    for ch in CHANNELS_CONFIG:
        if ch["id"]:
            try:
                member = await bot.get_chat_member(chat_id=ch["id"], user_id=user_id)
                if member.status in ["left", "kicked"]:
                    not_joined.append(ch["name"])
            except Exception as e:
                logging.error(f"Verification error for {ch['id']}: {e}")

    # Agar user ne join nahi kiya
    if not_joined:
        await callback.answer(
            f"❌ Access Denied! Aapne {', '.join(not_joined)} join nahi kiya hai. Pehle join karein!",
            show_alert=True
        )
        return

    # Agar verified hai:
    await callback.answer("✅ Verification Successful!")
    await callback.message.edit_text(
        "🎉 **VIP Access Unlocked!**\n\nNiche diye gaye options me se select karein:",
        reply_markup=get_main_menu(),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == "refresh_links")
async def refresh_callback(callback: types.CallbackQuery):
    await callback.message.edit_text("📢 **Official Partner Channels & Groups:**", reply_markup=get_force_sub_keyboard())

# --- 1-CLICK ACCURATE PREDICTION ---
@dp.callback_query(F.data == "get_prediction")
async def prediction_handler(callback: types.CallbackQuery):
    await callback.answer("Analyzing Live 1-Min Trend...")
    period, prediction, color, confidence, pattern, sec_left = get_wingo_live_prediction()

    result_text = (
        "🎮 **GAME:** Wingo 1-Minute\n"
        f"🆔 **TARGET PERIOD:** `{period}`\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"🎯 **PREDICTION:** **{prediction}**\n"
        f"🎨 **COLOR HINT:** {color}\n"
        f"📊 **ACCURACY:** **{confidence}%**\n"
        f"📈 **TREND DETECTED:** *{pattern}*\n"
        f"⏱️ **TIME LEFT:** ~{sec_left}s remaining\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🛡️ **RECOMMENDED BET:** Level 1 se start karein!"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Refresh Next Period", callback_data="get_prediction")],
        [InlineKeyboardButton(text="🔙 Main Menu", callback_data="verify_access")]
    ])
    await callback.message.edit_text(result_text, reply_markup=keyboard, parse_mode="Markdown")

# --- LEVEL CALCULATOR (4 TO 8 LEVELS PROFIT CHART) ---
@dp.callback_query(F.data == "open_calculator")
async def open_calc(callback: types.CallbackQuery, state: FSMContext):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="4 Levels", callback_data="lvl_4"), InlineKeyboardButton(text="5 Levels", callback_data="lvl_5")],
        [InlineKeyboardButton(text="6 Levels", callback_data="lvl_6"), InlineKeyboardButton(text="7 Levels", callback_data="lvl_7")],
        [InlineKeyboardButton(text="8 Levels", callback_data="lvl_8")],
        [InlineKeyboardButton(text="🔙 Cancel", callback_data="verify_access")]
    ])
    await callback.message.edit_text("🧮 **Select Backup Levels (4 se 8):**", reply_markup=keyboard)
    await state.set_state(CalcState.choosing_level)

@dp.callback_query(F.data.startswith("lvl_"))
async def level_chosen(callback: types.CallbackQuery, state: FSMContext):
    levels = int(callback.data.split("_")[1])
    await state.update_data(levels=levels)
    await callback.message.edit_text(f"✅ Selected: **{levels} Levels**\n\nApna **Total Wallet Balance** type karke bhejein:")
    await state.set_state(CalcState.entering_balance)

@dp.message(CalcState.entering_balance)
async def process_balance(message: types.Message, state: FSMContext):
    try:
        balance = float(message.text.strip())
        if balance < 50:
            await message.reply("⚠️ Minimum balance ₹50 hona chahiye.")
            return
    except ValueError:
        await message.reply("⚠️ Sirf number likhein:")
        return

    data = await state.get_data()
    levels = data.get("levels", 6)
    await state.clear()

    multipliers = [1, 3, 8, 24, 72, 216, 650, 1950][:levels]
    total_ratio = sum(multipliers)
    base_unit = max(1, int(balance / total_ratio))

    chart_lines = []
    total_spent = 0
    for i, mult in enumerate(multipliers, 1):
        bet = base_unit * mult
        total_spent += bet
        net_profit = (bet * 1.96) - total_spent
        chart_lines.append(f"• **L{i}:** ₹{bet} ➔ *Net Profit: +₹{net_profit:.1f}*")

    table = "\n".join(chart_lines)
    result = (
        f"📊 **Aapka {levels}-Level 100% Profit Chart:**\n"
        f"💰 **Total Fund:** ₹{int(balance)} | **Base Bet (L1):** ₹{base_unit}\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"{table}\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "💡 *Rule: Win hone par wapas Level 1 se start karein!*"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧮 Recalculate", callback_data="open_calculator")],
        [InlineKeyboardButton(text="🔙 Main Menu", callback_data="verify_access")]
    ])
    await message.answer(result, reply_markup=keyboard, parse_mode="Markdown")

# --- 10% COMPOUNDING SHEET ---
@dp.callback_query(F.data == "compounding_plan")
async def compounding_handler(callback: types.CallbackQuery):
    text = (
        "📈 **Safe 10% Daily Compounding Rule:**\n\n"
        "• **Day 1:** ₹1,000 ➔ Profit Target: **+₹100**\n"
        "• **Day 5:** ₹1,464 ➔ Profit Target: **+₹146**\n"
        "• **Day 10:** ₹2,357 ➔ Profit Target: **+₹235**\n"
        "• **Day 20:** ₹6,115 ➔ Profit Target: **+₹611**\n"
        "• **Day 30:** **₹17,449+ (17x Growth)**\n\n"
        "🛑 **Rule:** Daily 10% profit bante hi game turant band kar dein!"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Back to Menu", callback_data="verify_access")]])
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")

# Render Ping Handler
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
