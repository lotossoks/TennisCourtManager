# from pathlib import Path
# import json
# import re


# def create_standart_shadule(bot, message):
#     """
#     Запуск создания стандартного расписания
#     Создание сообщения с выбором количества недель
#     """
#     # Создание файла data/proc_tech.json
#     Path("data/proc_tech.json").touch(exist_ok=True)
#     # Заполнение его пустым словарем
#     with Path("data/proc_tech.json").open("w", encoding="utf8") as proc_tech_file:
#         json.dump({}, proc_tech_file, ensure_ascii=False)
#     # Сообщение пользователю о выборе недель
#     msg = bot.send_message(
#         message.chat.id,
#         "Введите количество недель на которые будет доступно бронирование:",
#     )
#     # Обработчик сообщения на количество недель
#     bot.register_next_step_handler(msg, lambda msg: process_week_input(bot, msg))


# def process_week_input(bot, message):
#     """
#     Проверка корректности ввода количества недель
#     Создание вообщения с вводом расписания на неделю
#     """
#     # Проверка: неделя - int
#     if check_corr_int(message.text):
#         n_weeks_show = int(message.text)
#         # Запись количества недель в data/proc_tech.json
#         with Path("data/proc_tech.json").open("r", encoding="utf8") as proc_tech_file:
#             proc_tech = json.load(proc_tech_file)
#         proc_tech["n_weeks_show"] = n_weeks_show
#         with Path("data/proc_tech.json").open("w", encoding="utf8") as proc_tech_file:
#             json.dump(proc_tech, proc_tech_file, ensure_ascii=False)
#         # Сообщение пользователю о вводе расписания
#         msg = bot.send_message(
#             message.chat.id,
#             "&??????????????????????????????"
#         )
#         bot.register_next_step_handler(msg, lambda msg: process_days_schedule(bot, msg))
#     else:
#         # При ошибке формата недели повторный ввод
#         bot.send_message(message.chat.id, f"Количество недель введено не корректно.")
#         create_standart_shadule(bot, message)


# def check_corr_int(string):
#     return string.isdigit() and int(string) > 0