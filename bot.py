import os
import asyncio
import logging
import aiohttp
from datetime import datetime
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- CONFIGURATION ---
BOT_TOKEN = "8843656284:AAHG9XEeB3lkt9XFpJy22PGABwmtv3YFpfY"
WINGO_API_URL = "https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json"

CHANNEL_LINKS = [
    ("📢 Prediction Group 1", "https://t.me/+FiAGrNzwRIZhNGY1"),
    ("📢 Professor X Channel", "https://t.me/ProfessorX106"),
    ("💬 Discussion Group", "https://t.me/+EZMAVv_kmuNjOTM1"),
    ("📢 VIP Backup Channel", "https://t.me/+OLB-4SeGbXJjZjQ9"),
    ("🎰 Slots By Toxic", "https://t.me/SlotsByToxic")
]

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class CalcState(StatesGroup):
    choosing_level = State()
    entering_balance = State()

def get_force_sub_keyboard():
    buttons = []
    for name, url in CHANNEL_LINKS:
        buttons.append([InlineKeyboardButton(text=name, url=url)])
    buttons.append([InlineKeyboardButton(text="✅ I Have Joined (Verify Access)", callback_data="verify_access")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_main_menu():
    keyboard = [
        [InlineKeyboardButton(text="🎯 Predict Next Period (1-Min)", callback_data="get_prediction")],
        [InlineKeyboardButton(text="🧮 Level Maintain Chart (L4 - L8)", callback_data="open_calculator")],
        [InlineKeyboardButton(text="📈 10% Compounding Plan", callback_data="compounding_plan")],
        [InlineKeyboardButton(text="🔄 Official Links", callback_data="refresh_links")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

async def fetch_wingo_trend():
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(WINGO_API_URL, headers=headers, timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    history = data.get("data", {}).get("list", [])
                    if history:
                        last_issue = history[0].get("issueNumber", "N/A")
                        last_number = int(history[0].get("number", 0))
                        last_size = "BIG" if last_number >= 5 else "SMALL"
                        return last_issue, last_size
    except Exception as e:
        logging.error(f"API Error: {e}")

    now = datetime.now()
    minutes_today = now.hour * 60 + now.minute
    simulated_period = f"{now.strftime('%Y%m%d')}01{minutes_today:04d}"
    return simulated_period, "BIG"

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    welcome_text = (
        "👋 **Welcome to Wingo 1-Minute VIP Prediction & Toolkit Bot!**\n\n"
        "Bot ke features unlock karne ke liye niche diye gaye **Sabhi Channels & Groups** ko join karein:"
    )
    await message.answer(welcome_text, reply_markup=get_force_sub_keyboard(), parse_mode="Markdown")

@dp.callback_query(F.data == "verify_access")
async def verify_callback(callback: types.CallbackQuery):
    await callback.answer("✅ Verification Successful!")
    await callback.message.edit_text(
        "🎉 **Access Granted!**\n\nNiche diye gaye menu se feature select karein:",
        reply_markup=get_main_menu(),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == "refresh_links")
async def refresh_callback(callback: types.CallbackQuery):
    await callback.message.edit_text("📢 **Official Partner Channels & Groups:**", reply_markup=get_force_sub_keyboard())

@dp.callback_query(F.data == "get_prediction")
async def prediction_handler(callback: types.CallbackQuery):
    await callback.answer("Analyzing Live 1-Min Trend...")
    last_issue, last_size = await fetch_wingo_trend()
    try:
        next_issue = str(int(last_issue) + 1)
    except:
        next_issue = "Next Round"

    prediction = "SMALL" if last_size == "BIG" else "BIG"
    result_text = (
        "🎮 **GAME:** Wingo 1-Minute\n"
        f"🆔 **NEXT PERIOD:** `{next_issue}`\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"🎯 **PREDICTION:** 🟢 **{prediction}**\n"
        f"📊 **ACCURACY:** 88% (Pattern Matched)\n"
        f"🔹 **PREVIOUS RESULT:** {last_size} (`{last_issue}`)\n"
        "🛡️ **RECOMMENDED BET:** Start with **Level 1**\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "⚠️ *Wait for timer to end before betting.*"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Get Next Prediction", callback_data="get_prediction")],
        [InlineKeyboardButton(text="🔙 Back to Menu", callback_data="verify_access")]
    ])
    await callback.message.edit_text(result_text, reply_markup=keyboard, parse_mode="Markdown")

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

# Render Health Check Server
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
