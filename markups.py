from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

###
mainMenu = InlineKeyboardMarkup(row_width=2)
btnFind = InlineKeyboardButton(text='Найти товар', callback_data='btnFind')
btnAdd = InlineKeyboardButton(text='Добавить товар', callback_data='btnAdd')

mainMenu.insert(btnFind)
mainMenu.insert(btnAdd)
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

###
# productActions = InlineKeyboardMarkup(row_width=1)
# btnAddProduct = InlineKeyboardButton(text='Добавить к мониторингу', callback_data=f'btnAddProduct_{product}')
# btnDeleteProduct = InlineKeyboardButton(text='Удалить из мониторинга', callback_data=f'btnDeleteProduct_{product}')

# productActions.insert(btnAddProduct)
# productActions.insert(btnDeleteProduct)
###