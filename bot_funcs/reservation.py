from datetime import date, datetime, timedelta
from pathlib import Path
import json
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def reservation(bot, message):
    """
    Запуск бронирования
    Выбор недели бронирования
    """

    def week_borders(plus=0):
        """
        Определение границ недели через n недель
        """
        first_day_0_week = date.today() - timedelta(days=date.today().isoweekday() % 7)
        first_day_need_week = first_day_0_week + timedelta(days=plus * 7 + 1)
        last_day_need_week = first_day_need_week + timedelta(days=6)
        return first_day_need_week, last_day_need_week

    with Path("data/tech.json").open("r", encoding="utf8") as tech_file:
        tech = json.load(tech_file)
    # Количество недель для отрисовки
    n_weeks_show = tech["n_weeks_show"]
    weeks_markup = InlineKeyboardMarkup()
    for i in range(n_weeks_show):
        start, finish = week_borders(i)
        if i == 0:
            pre = "Эта неделя"
        elif i == 1:
            pre = "Следующая неделя"
        else:
            pre = f"Неделя через {i} недели"

        button = InlineKeyboardButton(
            text=pre + f" ({start} - {finish})",
            callback_data=f"week_{start.strftime('%Y-%m-%d')}",
        )
        weeks_markup.row(button)
    bot.send_message(message.chat.id, "Выберите неделю:", reply_markup=weeks_markup)


def generate_reservation_message(day, user_id):
    """
    Генерация инлайн клавиатуры для бронирования
    """
    markup = InlineKeyboardMarkup()
    with Path("data/tech.json").open("r", encoding="utf8") as tech_file:
        tech = json.load(tech_file)
    with Path("data/reserv.json").open("r", encoding="utf8") as reserv_file:
        reserv = json.load(reserv_file)
    with Path("data/user.json").open("r", encoding="utf8") as user_file:
        user = json.load(user_file)[user_id]
    # Для каждого часа создем кнопку
    for hour in tech["standart_schedule"][day]:
        # Проверка на бронирование
        try:
            reserv_id = reserv[user["choose_week"]][day][hour]["user_reserv"]
        except KeyError:
            reserv_id = False
        # Генерация кнопки в зависимости от присутствия бронирования
        if not tech["standart_schedule"][day][hour]["free"] or reserv_id:
            if reserv_id == user_id:
                button_text = f"🟢{hour}"
                button_callback = f"your_{user_id}"
            else:
                button_text = f"🔴{hour}"
                button_callback = f"other_{reserv_id}"
        else:
            button_text = f"🆓{hour}"
            button_callback = "empty_"
        n_days = list(tech["standart_schedule"].keys()).index(day)
        day_date = (
            datetime.strptime(user["choose_week"], "%Y-%m-%d") + timedelta(n_days)
        ).strftime("%Y-%m-%d")
        finish_hour = hour.split("-")[1]
        finish_time = datetime.strptime(
            (day_date + " " + finish_hour), "%Y-%m-%d %H:%M"
        )
        if (
            "🔴" in button_text or "🆓" in button_text
        ) and datetime.now() > finish_time:
            button_text = f"🔘{hour}"
            button_callback = "passed_"

        button = InlineKeyboardButton(
            text=button_text,
            callback_data=f"R_{button_callback}_{user['choose_week']}_{day}_{hour}",
        )
        markup.row(button)
    # Генерация кнопок для выбора дня
    day_buttons = []
    for day_name in list(tech["standart_schedule"].keys()):
        if day_name == day:
            button = InlineKeyboardButton(
                text=f"📍{day_name[:2]}",
                callback_data=f"I_{day_name}",
            )
        else:
            button = InlineKeyboardButton(
                text=day_name[:2],
                callback_data=f"D_{day_name}",
            )
        day_buttons.append(button)
    markup.row(*day_buttons)
    markup.add(InlineKeyboardButton(text="Закончить выбор", callback_data="FR_"))
    return markup


def reservation_callback(bot, call):
    """
    Обработчих callback от reservation
    """
    text = call.data
    user_id = str(call.from_user.id)
    message_updated = False
    if text.startswith("week_"):
        with Path("data/tech.json").open("r", encoding="utf8") as tech_file:
            tech = json.load(tech_file)
        day = list(tech["standart_schedule"].keys())[0]
        with Path("data/user.json").open("r", encoding="utf8") as user_file:
            user = json.load(user_file)
        if user_id in user.keys():
            user[str(user_id)]["choose_week"] = text.split("_")[1]
        else:
            user[str(user_id)] = {"choose_week": text.split("_")[1]}
        with Path("data/user.json").open("w", encoding="utf8") as user_file:
            json.dump(user, user_file)
        message_updated = True
    elif text.startswith("R_your"):
        _, _, user_id, week, day, hour = text.split("_")
        bot.send_message(
            user_id,
            f"Этот слот забронирован вами.\nХотите его отменить?",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Отменить",
                            callback_data=f"CR_{user_id}_{week}_{day}_{hour}",
                        ),
                    ],
                    [InlineKeyboardButton("Назад", callback_data="NCR_")],
                ]
            ),
        )
    elif text.startswith("R_other"):
        _, _, user_id, week, day, hour = text.split("_")
        user_link = f'<a href="tg://user?id={user_id}">Профиль пользователя</a>'
        bot.answer_callback_query(
            call.id,
            f"Этот слот забронирован другим пользователем. {user_link}",
            parse_mode="HTML",
        )
    elif text.startswith("R_empty"):
        _, _, _, week, day, hour = text.split("_")
        with Path("data/reserv.json").open("r", encoding="utf8") as reserv_file:
            reserv = json.load(reserv_file)
        c = 0
        max_flag = False
        for d in reserv[week].keys():
            for h in reserv[week][d].keys():
                if reserv[week][d][h]["user_reserv"] == user_id:
                    c += 1
                if c >= 2:
                    max_flag = True
                    break
            if max_flag:
                break
        if max_flag:
            bot.answer_callback_query(
                call.id,
                f"Лимит бронирований на неделю достигнут.",
            )
        else:
            reserv.setdefault(week, {}).setdefault(day, {}).setdefault(hour, {})[
                "user_reserv"
            ] = user_id
            with Path("data/reserv.json").open("w", encoding="utf8") as reserv_file:
                json.dump(reserv, reserv_file, ensure_ascii=False)
            message_updated = True
    elif text.startswith("I_"):
        day = text.split("_")[1]
        bot.answer_callback_query(
            call.id,
            f"Сейчас вы выбираете из слотов на {day}.",
        )
    elif text.startswith("D_"):
        day = text.split("_")[1]
        message_updated = True
    elif text.startswith("FR_"):
        day = text.split("_")[1]
        bot.delete_message(call.message.chat.id, call.message.message_id)
    elif text.startswith("NCR_"):
        bot.delete_message(call.message.chat.id, call.message.message_id)
    elif text.startswith("CR_"):
        with Path("data/reserv.json").open("r", encoding="utf8") as reserv_file:
            reserv = json.load(reserv_file)
        _, user_id, week, day, hour = text.split("_")
        n_days = list(tech["standart_schedule"].keys()).index(day)
        day_date = (
            datetime.strptime(user[str(user_id)]["choose_week"], "%Y-%m-%d")
            + timedelta(n_days)
        ).strftime("%Y-%m-%d")
        finish_hour = hour.split("-")[1]
        finish_time = datetime.strptime(
            (day_date + " " + finish_hour), "%Y-%m-%d %H:%M"
        )
        if datetime.now() <= finish_time:
            reserv[week][day][hour]["user_reserv"] = None
            with Path("data/reserv.json").open("w", encoding="utf8") as reserv_file:
                json.dump(reserv, reserv_file)
            message_updated = True
        else:
            bot.answer_callback_query(
                call.id,
                f"Время слота уже прошло. Вы не можете отменить бронирование.",
            )
    elif text.startswith("R_passed_"):
        bot.answer_callback_query(
            call.id,
            f"Время слота уже прошло. Вы не можете его забронировать",
        )
    if message_updated:
        with Path("data/user.json").open("r", encoding="utf8") as user_file:
            user = json.load(user_file)
        with Path("data/tech.json").open("r", encoding="utf8") as tech_file:
            tech = json.load(tech_file)
        n_days = list(tech["standart_schedule"].keys()).index(day)
        day_date = (
            datetime.strptime(user[str(user_id)]["choose_week"], "%Y-%m-%d")
            + timedelta(n_days + 1)
        ).strftime("%Y-%m-%d")
        text = f"Выберите слот на {day} ({day_date})"
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=generate_reservation_message(day, user_id),
            text=text,
        )
