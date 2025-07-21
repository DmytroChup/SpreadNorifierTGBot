import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.client.default import DefaultBotProperties

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

@dp.message(CommandStart())
async def send_welcome(message: types.Message):
    subscribers.add(message.chat.id)
    await save_subscribers(subscribers)
    await message.reply("Ты подписан на спред-алерты")

@dp.message()
async def help_msg(message: types.Message):
    await message.answer("Напиши /start, чтобы подписаться на алерты.")

async def main():
    global subscribers
    subscribers = await load_subscribers()

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    tasks = [check_spread(bot, ClientClassMap),
             dp.start_polling(bot)]

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
