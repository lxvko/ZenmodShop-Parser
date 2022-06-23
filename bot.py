from fetch_cigarettes import main as fetch_cigarettes
from fetch_liquids import main as fetch_liquids
from fetch_serviced import main as fetch_serviced

import json
import asyncio
import markups as nav
from datetime import datetime
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage


API_TOKEN = '5556593938:AAHd1AYNfJCUrQ4kwIaxlLGfdf2VgrM9Vek'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

products = {}
base = {}


class Form(StatesGroup):
    title = State()


@dp.message_handler(commands='start')
async def start_message(message: types.Message):
    text = f'👋 Привет, {message.from_user.first_name}! \n \nЭтот бот создан для мониторинга цен в магазине Zenmod.'
    await message.reply(text, reply=False, reply_markup=nav.mainMenu)
    
    with open('base.json', 'r', encoding='utf8') as file:
            base = json.load(file)
    if str(message.from_user.id) not in base:
        base[str(message.from_user.id)] = {
            'username': message.from_user.username,
            'preferences': list()
        }
    
    with open('base.json', 'w', encoding='utf8') as file:
            json.dump(base, file, indent=4, ensure_ascii=False)

@dp.callback_query_handler(state='*', text='btnComeback')
async def comeback_to_menu(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await bot.edit_message_text(
        text=f'👋 И снова привет! \n\nТы вернулся в главное меню.', 
        message_id=callback.message.message_id,
        chat_id=callback.message.chat.id,
        reply_markup=nav.mainMenu)

@dp.callback_query_handler(text='btnFind')
async def find_product(callback: types.CallbackQuery):
    await bot.edit_message_text(
        text='Поиск производится по названию. \nВведи часть или полное название искомого товара', 
        message_id=callback.message.message_id,
        chat_id=callback.message.chat.id,
        reply_markup=nav.comebackToMenu)
    await Form.title.set()

@dp.callback_query_handler(text='btnShowAdded')
async def add_product(callback: types.CallbackQuery):
    await bot.edit_message_text(
        text='Здесь ты можешь увидеть товары, которые отслеживаются для тебя.', 
        message_id=callback.message.message_id,
        chat_id=callback.message.chat.id,
        reply_markup=nav.comebackToMenu)

@dp.message_handler(state=Form.title)
async def process_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    data = await state.get_data()
    queue = data.get('title')

    await bot.send_message(message.chat.id, text=f'Ищу по запросу "{queue}"')
    await asyncio.sleep(1)
    await state.finish()
    products = find_product_by_name(queue)
    
    with open('base.json', 'r', encoding='utf8') as file:
            base = json.load(file)

    if products:
        for product in products:
            match products[product].get('destiny'):
                case 'atomizer':
                    text = f'[{products[product].get("title")}]({products[product].get("link")}) \nОписание: {products[product].get("description")} \nДиаметр посадки: {products[product].get("seat_diameter")} \nТип обдува: {products[product].get("blow_type")} \nТип затяжки: {products[product].get("tightening_type")} \nЦена: {products[product].get("price")}'
                case 'cigarette':
                    text = f'[{products[product].get("title")}]({products[product].get("link")}) \nОписание: {products[product].get("description")} \nЦена: {products[product].get("price")}'
                case 'liquid':
                    text = f'[{products[product].get("title")}]({products[product].get("link")}) \nОписание: {products[product].get("description")} \nВкус: {products[product].get("taste")} \nСоль: {products[product].get("is_salt")} \nЦена: {products[product].get("price")}'

            if products[product].get("title") in base[str(message.from_user.id)]['preferences']:
                await bot.send_photo(
                    message.chat.id,
                    photo=products[product].get('image'),
                    caption=text, 
                    parse_mode="Markdown", 
                    reply_markup=InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text='Удалить из мониторинга', callback_data=f'btnDeleteProduct_{product}')))
            else:
                await bot.send_photo(
                    message.chat.id,
                    photo=products[product].get('image'),
                    caption=text, 
                    parse_mode="Markdown", 
                    reply_markup=InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text='Добавить к мониторингу', callback_data=f'btnAddProduct_{product}')))
    else:
        await bot.delete_message(message.chat.id, message.message_id + 1)
        await bot.send_message(chat_id=message.chat.id, 
                               text='Ничего не удалось найти. \nПопробуй изменить запрос или можешь вернуться в главное меню', 
                               reply_markup=nav.failedSearch)


def find_product_by_name(name):
    global products
    products = {}

    with open('jsons/atomizers.json', 'r', encoding='utf8') as file:
            atomizers =  json.load(file)
    with open('jsons/cigarettes.json', 'r', encoding='utf8') as file:
            cigarettes =  json.load(file)
    with open('jsons/liquids.json', 'r', encoding='utf8') as file:
            liquids =  json.load(file)

    for element in atomizers:
        if name in atomizers[element].get('title'):
            products[element] = atomizers[element]
    for element in cigarettes:
        if name in cigarettes[element].get('title'):
            products[element] = cigarettes[element]
    for element in liquids:
        if name in liquids[element].get('title'):
            products[element] = liquids[element]
    return products
            
@dp.callback_query_handler(Text(startswith='btnAddProduct_'), state='*')
async def process_add_product(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    
    await callback.answer(f'Успешно добавлено')
    number = callback.data.rpartition('_')[2]
    
    with open('base.json', 'r', encoding='utf8') as file:
            base = json.load(file)
    
    base[str(callback.from_user.id)]['preferences'].append(products[number].get('title'))
    with open('base.json', 'w', encoding='utf8') as file:
            json.dump(base, file, indent=4, ensure_ascii=False)
    
    await bot.edit_message_reply_markup(message_id=callback.message.message_id,
                                  chat_id=callback.message.chat.id, 
                                  reply_markup=InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text='Удалить из мониторинга', callback_data=f'btnDeleteProduct_{number}')))

@dp.callback_query_handler(Text(startswith='btnDeleteProduct_'), state='*')
async def process_delete_product(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    
    await callback.answer(f'Успешно удалено')
    number = callback.data.rpartition('_')[2]
    
    with open('base.json', 'r', encoding='utf8') as file:
            base = json.load(file)

    base[str(callback.from_user.id)]['preferences'].remove(products[number].get('title'))
    with open('base.json', 'w', encoding='utf8') as file:
            json.dump(base, file, indent=4, ensure_ascii=False)
    
    await bot.edit_message_reply_markup(message_id=callback.message.message_id,
                                  chat_id=callback.message.chat.id, 
                                  reply_markup=InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text='Добавить к мониторингу', callback_data=f'btnAddProduct_{number}')))

async def periodic(sleep_for):
    while True:
        await asyncio.sleep(sleep_for)
        now = datetime.utcnow()
        print(f"{now}")
        # await bot.send_message(id, f"{now}", disable_notification=True)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(periodic(10))
    executor.start_polling(dp)
