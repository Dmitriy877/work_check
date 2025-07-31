import telegram


def telegram_send_message(
    token: str,
    chat_id: str,
    is_negative: bool,
    lesson_url: str,
    lesson_title: str
):
    if is_negative:
        text = f"""
            У вас проверили работу "{lesson_title}"
            К сожалению в работе нашлись ошибки
            Ссылка на работу {lesson_url}
        """
    else:
        text = f"""
            У вас проверили работу "{lesson_title}"
            Преподавателю все понравилось, можно приступать к следующему уроку!
            Ссылка на работу {lesson_url}
        """
    bot = telegram.Bot(token=token)
    bot.send_message(text=text, chat_id=chat_id)
