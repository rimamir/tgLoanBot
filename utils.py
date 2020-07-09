from datetime import datetime, timedelta
from orm import change_status


def loan_calculate(cash: int, rate: float, days: int):
    annual_rate = rate * 365
    calculated_amount = ((cash * annual_rate * days) / (365 * 100))
    return int(cash + calculated_amount)


def set_loan(current_borrower, days: int):
    calculated_loan = loan_calculate(current_borrower['cash'], current_borrower['rate'], int(days))
    current_borrower['loan'] = calculated_loan


def borrower_info(current_borrower: dict):
    if isinstance(current_borrower['take_date'], str):
        current_borrower['take_date'] = str_to_datetime(current_borrower['take_date'])
    if isinstance(current_borrower['return_date'], str):
        current_borrower['return_date'] = str_to_datetime(current_borrower['return_date'])

    try:
        current_borrower['id']
    except KeyError:
        return f"{current_borrower['name'].title()} — <i>{current_borrower['cash']}р {toFixed(current_borrower['rate'], 2)}%</i> " \
               f"{formatted_date(current_borrower['take_date'])}\n" \
               f"<b>{current_borrower['loan']}р — " \
               f"{formatted_date(current_borrower['return_date'])}</b>"
    else:
        if current_borrower['return_date'] < datetime.now() - timedelta(days=1):
            return_date = f"❗{formatted_date(current_borrower['return_date'])}❗"
        else:
            return_date = f"{formatted_date(current_borrower['return_date'])}"

        return f"{current_borrower['name'].title()} — <i>{current_borrower['cash']}р {toFixed(current_borrower['rate'], 2)}%</i> " \
               f"{formatted_date(current_borrower['take_date'])}\n" \
               f"<b>{current_borrower['loan']}р — " \
               f"{return_date} /del{current_borrower['id']}</b>"


def formatted_date(date: datetime):
    months = {
        1: 'Января',
        2: 'Февраля',
        3: 'Марта',
        4: 'Апреля',
        5: 'Мая',
        6: 'Июня',
        7: 'Июля',
        8: 'Августа',
        9: 'Сентября',
        10: 'Октября',
        11: 'Ноября',
        12: 'Декабря'
    }
    return f"{date.day} {months[date.month]} {date.year}"


def is_digit(string: str):
    if string.isdigit():
        return True
    else:
        string = string.replace(',', '.')
        try:
            float(string)
            return True
        except ValueError:
            return False


def str_to_datetime(date):
    return datetime.strptime(date, '%Y-%m-%d')


def name_validate(name: str):
    """
    Return 2 params: validity, error
    """
    if name.startswith('/'):
        return False, 'Имя не может начинатся с / ❗️'
    elif len(name) < 4:
        return False, 'Слишком короткое имя❗️'
    elif len(name) > 50:
        return False, 'Слишком длинное имя❗'

    return True, '<i>Выберите категорию или введите процентную ставку (дневную):</i>'


def change_borrower_status(message, bot):
    chat_id = message.chat.id
    try:
        row_id = int(message.text[4:])
    except ValueError:
        bot.send_message(chat_id, '<i>Команда должна быть в формате:\n</i>/del(id)❗', parse_mode='HTML')
    else:
        if change_status(row_id):
            bot.send_message(chat_id, 'Удалил')
            return
        bot.send_message(chat_id, 'Такого пользователя не существует❗')


def toFixed(numobj, digits=0):
    return f"{numobj:.{digits}f}"
