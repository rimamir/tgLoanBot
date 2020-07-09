TOKEN = 'token'

allowed_id = [257498767, 343555468]
# 791925253 - Raf
# 343555468 - Nail

rate_categories = {'6%': 6 / 30,
                   '8%': 8 / 30,
                   '10%': 10 / 30,
                   '12%': 12 / 30,
                   }
commands = ['/add', '/recent', '/today', '/week', '/all', '/categories', '/help', '/del']

start_msg = 'ЗаймБот\n' \
            '____________________________________\n' \
            '/add - <i>добавить</i>\n\n' \
            '<b>Просмотр:</b>\n' \
            '/today - <i>сегодняшние</i>\n' \
            '/week - <i>недельные</i>\n' \
            '/all - <i>все</i>\n' \
            '/recent - <i>недавно добавленные</i>\n\n' \
            '/categories - <i>категории - проценты</i>\n\n' \
            '/help - <i>помощь</i>'

help_msg = 'Доступные команды:\n' \
           '/add - <i>добавить</i>\n\n' \
           '<b>Просмотр:</b>\n' \
           '/today - <i>сегодняшние</i>\n' \
           '/week - <i>недельные</i>\n' \
           '/all - <i>все</i>\n' \
           '/recent - <i>недавно добавленные</i>\n\n' \
           '/categories - <i>категории - проценты</i>\n\n'

thread_active = dict()
adding_process = False
