import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.client.default import DefaultBotProperties
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import BOT_TOKEN
from exchanges.mexc import MEXCClient
from exchanges.bitget import BitgetClient
from exchanges.bingx import BingXClient
from exchanges.gate import GateClient
from checker import check_spread, load_subscribers, save_subscribers

dp = Dispatcher()
subscribers = set()

ClientClassMap = {
    "MEXC Futures": MEXCClient,
    "Bitget Futures": BitgetClient,
    "BingX Futures": BingXClient,
    "Gate Futures": GateClient
}

def get_main_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подписаться на алерты", callback_data="subscribe")],
        [InlineKeyboardButton(text="❌ Отписаться от алертов", callback_data="unsubscribe")]
    ])
    return keyboard

@dp.message(CommandStart())
async def send_welcome(message: types.Message):
    text = (
        "👋 Привет!\n\n"
        "Я спред-бот. Я могу присылать тебе алерты, если на биржах появляется спред.\n\n"
        "Нажми кнопку ниже, чтобы подписаться или отписаться."
    )
    await message.answer(text, reply_markup=get_main_keyboard())

@dp.callback_query(lambda c: c.data in ["subscribe", "unsubscribe"])
async def handle_subscription(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    if callback_query.data == "subscribe":
        subscribers.add(user_id)
        await callback_query.message.edit_text(
            "✅ Ты успешно подписан на алерты!",
            reply_markup=get_main_keyboard()
        )
    else:
        if user_id in subscribers:
            subscribers.remove(user_id)
            await callback_query.message.edit_text(
                "❌ Ты успешно отписан от алертов.",
                reply_markup=get_main_keyboard()
            )
        else:
            await callback_query.message.edit_text(
                "Ты и так не подписан",
                reply_markup=get_main_keyboard()
            )

    await save_subscribers(subscribers)

@dp.message()
async def fallback(message: types.Message):
    await message.answer(
        "Напиши /start или используй кнопки ниже ⬇️",
        reply_markup=get_main_keyboard()
    )

async def setup_bot_commands(bot: Bot):
    commands = [
        types.BotCommand(command="start", description="Запустить бота и меню"),
    ]
    await bot.set_my_commands(commands)

async def main():
    global subscribers
    subscribers = await load_subscribers()

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    await setup_bot_commands(bot)

    tasks = [check_spread(bot, ClientClassMap),
             dp.start_polling(bot)]

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
