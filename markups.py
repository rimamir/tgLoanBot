from telebot import types

category_markups = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
category_markups_6 = types.KeyboardButton('6%')
category_markups_8 = types.KeyboardButton('8%')
category_markups_10 = types.KeyboardButton('10%')
category_markups_12 = types.KeyboardButton('12%')

category_markups.row(category_markups_6, category_markups_8)
category_markups.row(category_markups_10, category_markups_12)


cash_markups = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
cash_markups_1000 = types.KeyboardButton('5000')
cash_markups_5000 = types.KeyboardButton('10000')
cash_markups_10000 = types.KeyboardButton('25000')
cash_markups_30000 = types.KeyboardButton('50000')
cash_markups.row(cash_markups_1000, cash_markups_5000)
cash_markups.row(cash_markups_10000, cash_markups_30000)

day_markups = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
day_markups_3 = types.KeyboardButton('3')
day_markups_7 = types.KeyboardButton('7')
day_markups_14 = types.KeyboardButton('14')
day_markups_30 = types.KeyboardButton('30')
day_markups.row(day_markups_3, day_markups_7)
day_markups.row(day_markups_14, day_markups_30)
