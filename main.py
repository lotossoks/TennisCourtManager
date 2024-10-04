import config as config

import telebot

from bot_funcs.create_standart_shadule import create_standart_shadule
from bot_funcs.setting_standart_schedule import (
    setting_standart_schedule,
    setting_callback,
)
from bot_funcs.reservation import reservation, reservation_callback
bot = telebot.TeleBot(token=config.token)


@bot.message_handler(commands=["create_standart_schedule"])
def handle_create_standart_schedule(message):
    create_standart_shadule(bot, message)


@bot.message_handler(commands=["setting_standart_schedule"])
def handle_setting_standart_schedule(message):
    setting_standart_schedule(bot, message, set_exist=True)


@bot.message_handler(commands=["reservation"])
def handle_create_standard_schedule(message):
    reservation(bot, message)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    text = call.data
    if (
        text.startswith("RC_")
        or text.startswith("IC_")
        or text.startswith("DC_")
        or text.startswith("FC_")
    ):
        setting_callback(bot, call)
    elif (
            text.startswith("week_")
            or text.startswith("R_")
            or text.startswith("I_")
            or text.startswith("D_")
            or text.startswith("FR_")
            or text.startswith("CR_")
            or text.startswith("NCR_")
        ):
            reservation_callback(bot, call)


bot.infinity_polling()



"""
Планы на будущее
Чат -(ссылка)-> Бот -> Какие общие чаты у user и Бота -> Выбор чата для работы -> Start (показывает доступные функции) -> Все нужные действия
Решить, как человек сможет менять свой чат (команда, скорее всего)
Доступность функций только для админов
Архив всех регистраций
Просмотр всех броней (для админа) + возможность отмены
Просмотр всех броней + возможность отмены (для user)
Отмена брони (для user)
напоминание о брони
Админ - бронирование и отмена любого количества слотов
Экран start
Слова дней недели нигде не используются, только даты или индексы
Настройка количества регистраций в неделю
Указывать порядок дней недели (1- понедельник, 2 - вторник и т.д.)
Переписать при помощи db, а не json 
Переписать на asinc, а не telebot
"""