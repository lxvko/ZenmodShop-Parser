from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

###
mainMenu = InlineKeyboardMarkup(row_width=2)
btnFind = InlineKeyboardButton(text='Поиск по товарам', callback_data='btnFind')
btnShowAdded = InlineKeyboardButton(text='Отслеживаемые товары', callback_data='btnShowAdded')

mainMenu.insert(btnFind)
mainMenu.insert(btnShowAdded)
###

###
comebackToMenu = InlineKeyboardMarkup(row_width=1)
btnComeback = InlineKeyboardButton(text='Вернуться в главное меню', callback_data='btnComeback')

comebackToMenu.insert(btnComeback)
###

###
failedSearch = InlineKeyboardMarkup(row_width=2)

failedSearch.insert(btnFind)
failedSearch.insert(btnComeback)
###
