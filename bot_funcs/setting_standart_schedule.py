import json
from pathlib import Path
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from telebot.apihelper import ApiTelegramException


def setting_standart_schedule(bot, message, set_exist):
    """
    Обновление существующего расписания и/или
    До настройка создающегося расписания
    """
    bot.send_message(
        message.chat.id,
        "Для изменения стандартных настроек нажмите на слот."
        + "После окончания выбора нажите на кнопку 'Готово'",
        reply_markup=generate_reservation_message_change(set_exist=set_exist),
    )


def generate_reservation_message_change(set_exist, day=None):
    """
    Клавиатура для изменения расписания
    """
    # Настройка существующего расписания
    if set_exist:
        # Копирование расписания в proc_tech.json
        with Path("data/tech.json").open("r", encoding="utf8") as tech_file:
            tech = json.load(tech_file)
        Path("data/proc_tech.json").touch(exist_ok=True)
        with Path("data/proc_tech.json").open("w", encoding="utf8") as proc_tech_file:
            json.dump(tech, proc_tech_file, ensure_ascii=False)
    # Данные из настраемого расписания
    with Path("data/proc_tech.json").open("r", encoding="utf8") as proc_tech_file:
        proc_tech = json.load(proc_tech_file)
    # Если не указана day, устанавлиявается первый
    if not day:
        day = list(proc_tech["standart_schedule"].keys())[0]
    markup = InlineKeyboardMarkup()

    for hour in proc_tech["standart_schedule"][day]:
        # Добавлие кнопок в зависимости от состояния
        if not proc_tech["standart_schedule"][day][hour]["free"]:
            button_text = f"🔴{hour}"
        else:
            button_text = f"🆓{hour}"
        button = InlineKeyboardButton(
            text=button_text, callback_data=f"RC_{day}_{hour}"
        )
        markup.row(button)
    # Добавление кнопок с переходами на другие дни
    day_buttons = []
    for day_name in list(proc_tech["standart_schedule"].keys()):
        if day_name == day:
            button = InlineKeyboardButton(
                text=f"📍{day_name[:2]}",
                callback_data=f"IC_{day_name}",
            )
        else:
            button = InlineKeyboardButton(
                text=day_name[:2],
                callback_data=f"DC_{day_name}",
            )
        day_buttons.append(button)
    markup.row(*day_buttons)
    markup.add(InlineKeyboardButton(text="Закончить настройку", callback_data="FC_"))
    return markup


def setting_callback(bot, call):
    """
    Обработчих callback от generate_reservation_message_change
    """
    text = call.data
    message_updated = False
    if text.startswith("RC_"):
        with Path("data/proc_tech.json").open("r", encoding="utf8") as proc_tech_file:
            proc_tech = json.load(proc_tech_file)
        _, day, hour = text.split("_")
        proc_tech["standart_schedule"][day][hour]["free"] = not (
            proc_tech["standart_schedule"][day][hour]["free"]
        )
        with Path("data/proc_tech.json").open("w", encoding="utf8") as proc_tech_file:
            json.dump(proc_tech, proc_tech_file)
        message_updated = True
    elif text.startswith("IC_"):
        day = text.split("_")[1]
        bot.answer_callback_query(
            call.id,
            f"Сейчас вы выбираете из слотов на {day}.",
        )
    elif text.startswith("DC_"):
        day = text.split("_")[1]
        message_updated = True
    elif text.startswith("FC_"):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        with Path("data/tech.json").open("r", encoding="utf8") as tech_file:
            tech = json.load(tech_file)
        with Path("data/proc_tech.json").open("r", encoding="utf8") as proc_tech_file:
            proc_tech = json.load(proc_tech_file)
        tech["standart_schedule"] = proc_tech["standart_schedule"]
        tech["n_weeks_show"] = proc_tech["n_weeks_show"]
        with Path("data/tech.json").open("w", encoding="utf8") as tech_file:
            json.dump(tech, tech_file)
        Path("data/proc_tech.json").unlink()
        bot.send_message(
            call.message.chat.id,
            "Стандартные настройки успешно обновлены.",
        )
    if message_updated:
        try:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=generate_reservation_message_change(
                    set_exist=False, day=day
                ),
                text=f"Выберите слот на {day}",
            )
        except ApiTelegramException as e:
            if "message is not modified" not in str(e):
                print(f"Ошибка при обновлении сообщения: {e}")
