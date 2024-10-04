from pathlib import Path
import json
import re
from bot_funcs.setting_standart_schedule import setting_standart_schedule


def create_standart_shadule(bot, message):
    """
    Запуск создания стандартного расписания
    Создание сообщения с выбором количества недель
    """
    # Создание файла data/proc_tech.json
    Path("data/proc_tech.json").touch(exist_ok=True)
    # Заполнение его пустым словарем
    with Path("data/proc_tech.json").open("w", encoding="utf8") as proc_tech_file:
        json.dump({}, proc_tech_file, ensure_ascii=False)
    # Сообщение пользователю о выборе недель
    msg = bot.send_message(
        message.chat.id,
        "Введите количество недель на которые будет доступно бронирование:",
    )
    # Обработчик сообщения на количество недель
    bot.register_next_step_handler(msg, lambda msg: process_week_input(bot, msg))


def process_week_input(bot, message):
    """
    Проверка корректности ввода количества недель
    Создание вообщения с вводом расписания на неделю
    """
    # Проверка: неделя - int
    try:
        n_weeks_show = int(message.text)
        # Проверка - кол-во неделб больше 0
        if n_weeks_show < 0:
            raise ValueError("Количество недель должно быть" + "положительным числом.")
        # Запись количества недель в data/proc_tech.json
        with Path("data/proc_tech.json").open("r", encoding="utf8") as proc_tech_file:
            proc_tech = json.load(proc_tech_file)
        proc_tech["n_weeks_show"] = n_weeks_show
        with Path("data/proc_tech.json").open("w", encoding="utf8") as proc_tech_file:
            json.dump(proc_tech, proc_tech_file, ensure_ascii=False)
        # Сообщение пользователю о вводе расписания
        msg = bot.send_message(
            message.chat.id,
            "Введите расписание на неделю в формате:\n"
            + "'День недели - Старт брони (чч:мм) - Финиш брони (чч:мм)'"
            + "\nПример: Понедельник - 09:00 - 12:00\n\n"
            + "Каждый слот с новой строки.\n "
            + "Слоты не должны перекрываться по времени.",
        )
        bot.register_next_step_handler(msg, lambda msg: process_days_schedule(bot, msg))

    except ValueError as e:
        # При ошибке формата недели повторный ввод
        bot.send_message(message.chat.id, f"Ошибка: {str(e)}. Попробуйте снова.")
        create_standart_shadule(bot, message)


def process_days_schedule(bot, message):
    """
    Ввод, проверка и сохранение расписания
    """
    # Проверка корректности ввода расписания
    error_lines = add_days_to_schedule(message.text)
    # Если существуют неправильно обработанные строки
    if error_lines:
        # Повторный ввод исправленых строк
        bot.send_message(
            message.chat.id,
            f"Ошибки в этих строках:\n{'\n'.join(error_lines)}\nПопробуйте снова.",
        )
        msg = bot.send_message(
            message.chat.id,
            "Пожалуйста, введите исправленные строки:",
        )
        bot.register_next_step_handler(msg, lambda msg: process_days_schedule(bot, msg))
    else:
        bot.send_message(message.chat.id, "Расписание успешно добавлено!")
        setting_standart_schedule(bot, message, set_exist=False)


def add_days_to_schedule(input_data):
    """
    Проверка корректности ввода расписания
    """

    def is_valid_time_slot(time_string):
        """
        Проверка совпадение формата времени в строке расписания
        """
        return re.match(r"^\d{2}:\d{2}$", time_string) is not None

    # Разделение строки на элементы
    lines = [line.split("-") for line in input_data.split("\n")]
    error_lines = []
    for i, line in enumerate(lines):
        # Для каждой введенной строки
        try:
            # Проверка на количество элементов
            if len(line) != 3:
                raise ValueError("Неверное количество элементов в строке.")
            day, start, end = [x.strip() for x in line]
            # Проверка корректности введенного времени
            if not is_valid_time_slot(start) or not is_valid_time_slot(end):
                raise ValueError("Неверный формат времени. Используйте чч:мм.")
            # Обновление расписания в data/proc_tech.json
            with Path("data/proc_tech.json").open(
                "r", encoding="utf8"
            ) as proc_tech_file:
                proc_tech = json.load(proc_tech_file)
            if "standart_schedule" not in proc_tech:
                proc_tech["standart_schedule"] = {}
            if day not in proc_tech["standart_schedule"]:
                proc_tech["standart_schedule"][day] = {}
            proc_tech["standart_schedule"][day][f"{start}-{end}"] = {"free": True}
            with Path("data/proc_tech.json").open(
                "w", encoding="utf8"
            ) as proc_tech_file:
                json.dump(proc_tech, proc_tech_file, ensure_ascii=False)
        except ValueError as e:
            # Для неправильных строк созранение в error_lines
            error_lines.append(f"{input_data.split('\n')[i]}: {str(e)}")

    return error_lines
