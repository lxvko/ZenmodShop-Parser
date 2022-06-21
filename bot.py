from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
import asyncio

token = '5556593938:AAHd1AYNfJCUrQ4kwIaxlLGfdf2VgrM9Vek'

bot = Bot(token=token, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)

async def parser():
    


@dp.message_handler(commands='start')
async def start(message: types.Message):
    await message.answer('hi')




def main():
    executor.start_polling(dp)


if __name__ == '__main__':
    main()
