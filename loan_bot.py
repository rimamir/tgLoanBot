from datetime import datetime, timedelta
import time
from threading import Thread
import logging

import telebot
from telebot import types
import schedule

import config
import markups as m
from orm import BorrowerDB, get_recent_borrowers, get_today_borrowers, \
    get_all_borrowers, get_weekly_borrowers
from utils import loan_calculate, borrower_info, is_digit, set_loan, name_validate, change_borrower_status

bot = telebot.TeleBot(config.TOKEN)

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

current_borrower = dict()


def auth(func):
    def wrapper(message):
        chat_id = message.chat.id

        msg = message.text
        user_id = message.from_user.id
        logger.info(f'{user_id} - {msg}')

        if message.from_user.id in config.allowed_id:
            return func(message)

        msg = '<b>Доступ запрещен❗️</b>\nДля получения - @amir_abubakirov'
        bot.send_message(chat_id, msg, parse_mode='HTML')

    return wrapper


@bot.message_handler(commands=['start', 'go'])
@auth
def start_handler(message):
    chat_id = message.chat.id
    msg = config.start_msg
    bot.send_message(chat_id, msg, parse_mode='HTML', reply_markup=types.ReplyKeyboardRemove(selective=False))


@bot.message_handler(commands=['help'])
@auth
def help_handler(message):
    chat_id = message.chat.id
    msg = config.help_msg
    bot.send_message(chat_id, msg, parse_mode='HTML')


@bot.message_handler(commands=['add'])
@auth
def add_handler(message):
    chat_id = message.chat.id

    # Clear data in temp dict
    global current_borrower
    current_borrower = dict()

    if not config.adding_process:
        msg = bot.send_message(chat_id, '<i>Введите имя:</i>', parse_mode="HTML")
        bot.register_next_step_handler(msg, borrower_name_handler)
        config.adding_process = True


@auth
def borrower_name_handler(message):
    chat_id = message.chat.id
    try:
        name = message.text.lower()
    except AttributeError:
        except_msg = bot.send_message(chat_id, 'Неверный формат имени❗')
        bot.register_next_step_handler(except_msg, borrower_name_handler)
    else:
        validity, validator_msg = name_validate(name)

        if not validity:
            msg = bot.send_message(chat_id, validator_msg, parse_mode='HTML')
            bot.register_next_step_handler(msg, borrower_name_handler)
            return

        current_borrower['name'] = name

        choice_msg = bot.send_message(chat_id, validator_msg, reply_markup=m.category_markups, parse_mode='HTML')
        bot.register_next_step_handler(choice_msg, rate_handler)


@auth
def rate_handler(message):
    chat_id = message.chat.id
    try:
        category_msg = message.text.lower()
    except AttributeError:
        except_msg = bot.send_message(chat_id, 'Неверный формат❗')
        bot.register_next_step_handler(except_msg, rate_handler)
    else:
        digit_flag = False

        # Check if category_msg the num
        if is_digit(category_msg):
            category_msg = category_msg.replace(',', '.')
            rate = float(category_msg)
            if rate < 0:
                attention = bot.send_message(chat_id, 'Процентая ставка не может быть меньше нуля❗️ Введите заново:')
                bot.register_next_step_handler(attention, rate_handler)
                return
            if rate >= 100000000:
                attention = bot.send_message(chat_id,
                                             'Процентая ставка не может быть больше 100000000❗️ Введите заново:')
                bot.register_next_step_handler(attention, rate_handler)
                return

            digit_flag = True

        elif category_msg not in config.rate_categories:
            attention = bot.send_message(message.chat.id, 'Такой категории не существует❗️',
                                         reply_markup=m.category_markups)
            bot.register_next_step_handler(attention, rate_handler)
            return

        if digit_flag:
            current_borrower['rate'] = float(category_msg)
        else:
            current_borrower['rate'] = config.rate_categories[category_msg]

        choice_msg = bot.send_message(message.chat.id, '<i>Введите сумму:</i>',
                                      reply_markup=m.cash_markups, parse_mode='HTML')
        bot.register_next_step_handler(choice_msg, cash_handler)


@auth
def cash_handler(message):
    chat_id = message.chat.id
    try:
        cash = message.text.lower()
    except AttributeError:
        except_msg = bot.send_message(chat_id, 'Неверный формат❗')
        bot.register_next_step_handler(except_msg, cash_handler)
    else:
        if not is_digit(cash):
            attention = bot.send_message(chat_id, 'Сумма должна быть целым числом❗️', reply_markup=m.cash_markups)
            bot.register_next_step_handler(attention, cash_handler)
            return
        else:
            cash = message.text.replace(',', '.')
            if int(float(cash)) < 0:
                attention = bot.send_message(chat_id, 'Сумма не может быть меньше 0❗️', reply_markup=m.cash_markups)
                bot.register_next_step_handler(attention, cash_handler)
                return
            if int(float(cash)) > 100000000:
                attention = bot.send_message(chat_id, 'Сумма не может быть больше 100000000❗️',
                                             reply_markup=m.cash_markups)
                bot.register_next_step_handler(attention, cash_handler)
                return

        current_borrower['cash'] = int(float(cash))
        choice_msg = bot.send_message(message.chat.id, '<i>На сколько дней?</i>',
                                      reply_markup=m.day_markups, parse_mode='HTML')
        bot.register_next_step_handler(choice_msg, date_handler)


@auth
def date_handler(message):
    chat_id = message.chat.id
    try:
        days = message.text.lower()
    except AttributeError:
        except_msg = bot.send_message(chat_id, 'Неверный формат!')
        bot.register_next_step_handler(except_msg, date_handler)
    else:
        if not days.isdigit():
            attention = bot.send_message(chat_id, 'Количество дней должно быть целым числом❗️',
                                         reply_markup=m.day_markups)
            bot.register_next_step_handler(attention, date_handler)
            return

        if int(days) <= 0:
            attention = bot.send_message(chat_id, 'Количество дней не может быть меньше 0❗️',
                                         reply_markup=m.day_markups)
            bot.register_next_step_handler(attention, date_handler)
            return

        if int(days) >= 3650:
            attention = bot.send_message(chat_id, 'Количество дней не может быть больше 3650❗️',
                                         reply_markup=m.day_markups)
            bot.register_next_step_handler(attention, date_handler)
            return

        today_date = datetime.now().date()
        current_borrower['take_date'] = today_date
        current_borrower['return_date'] = today_date + timedelta(days=int(days))

        set_loan(current_borrower, days)

        bot.send_message(message.chat.id, borrower_info(current_borrower),
                         reply_markup=types.ReplyKeyboardRemove(selective=False), parse_mode="HTML")

        BorrowerDB.create(name=current_borrower['name'],
                          cash=current_borrower['cash'],
                          loan=current_borrower['loan'],
                          take_date=current_borrower['take_date'],
                          return_date=current_borrower['return_date'],
                          rate=current_borrower['rate'])

        config.adding_process = False


@bot.message_handler(commands=['today', 'week', 'all', 'recent'])
@auth
def get_borrowers(message):
    borrowers_get = {'/today': ['Сегодня:', get_today_borrowers],
                     '/week': ['На этой неделе:', get_weekly_borrowers],
                     '/all': ['Все:', get_all_borrowers],
                     '/recent': ['Недавно добавленные:', get_recent_borrowers]}
    chat_id = message.chat.id
    request_msg = message.text
    response_msg = borrowers_get[request_msg][0]
    borrowers = borrowers_get[request_msg][1]()

    if len(borrowers) == 0:
        response_msg = '<i>Никого нет</i>'
        bot.send_message(chat_id, response_msg, parse_mode='HTML')
        return

    for borrower in enumerate(borrowers):
        if len(response_msg) < 2400:
            response_msg += f"\n{borrower[0] + 1}. {borrower_info(borrower[1])}\n"
        else:
            bot.send_message(chat_id, response_msg, parse_mode='HTML')
            response_msg = ''

    try:
        bot.send_message(chat_id, response_msg, parse_mode='HTML')
    except Exception:
        pass


@bot.message_handler(commands=['categories'])
@auth
def categories_handler(message):
    chat_id = message.chat.id
    msg = 'Все категории:\n'
    for category in config.rate_categories.items():
        msg += f"{category[0]} - {category[1]}%\n"
    bot.send_message(chat_id, msg)


@bot.message_handler(content_types=['text'])
@auth
def text_handler(message):
    msg = message.text
    if msg.startswith('/del'):
        change_borrower_status(message, bot)
    else:
        if msg not in config.commands:
            bot.send_message(message.chat.id,
                             'Такой команды не существует❗\n/help — <i>посмотреть список всех команд</i>',
                             parse_mode='HTML')


def schedule_checker():
    logger.info('Thread start')
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except Exception as exc:
        logger.info(exc)


def function_to_run():
    response_msg = 'Сегодня:'
    borrowers = get_today_borrowers()

    if len(borrowers) == 0:
        response_msg = '<i>Никого нет</i>'
        bot.send_message(343555468, response_msg, parse_mode='HTML')
        return

    for borrower in enumerate(borrowers):
        if len(response_msg) < 2400:
            response_msg += f"\n{borrower[0] + 1}. {borrower_info(borrower[1])}\n"
        else:
            bot.send_message(343555468, response_msg, parse_mode='HTML')
            response_msg = ''

    try:
        bot.send_message(343555468, response_msg, parse_mode='HTML')
    except Exception as exc:
        logger.info(exc)


if __name__ == '__main__':
    Thread(target=schedule_checker).start()
    schedule.every().day.at("08:00").do(function_to_run)
    bot.polling()
