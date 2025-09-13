import requests
import time
import logging

from requests.exceptions import ReadTimeout, ConnectionError
from environs import env
from bot import telegram_send_message
import telegram


def get_response(url: str, devman_token, timestamp: float) -> dict:
    headers = {
        "Authorization": devman_token,
    }
    payload = {
        'timestamp': timestamp,
    }
    response = requests.get(url, headers=headers, params=payload)
    response.raise_for_status()
    return response.json()


def check_lesson(
        url: str,
        devman_token,
        tg_bot,
        chat_id,
        logger,
        timestamp: float = None,
):
    while True:
        try:
            response_raw = get_response(url, devman_token, timestamp)
            if response_raw['status'] == 'timeout':
                timestamp = response_raw['timestamp_to_request']
            if response_raw['status'] == 'found':
                new_attempts = response_raw['new_attempts'][0]
                telegram_send_message(
                    tg_bot,
                    chat_id,
                    is_negative=new_attempts['is_negative'],
                    lesson_url=new_attempts['lesson_url'],
                    lesson_title=new_attempts['lesson_title']
                )
            time.sleep(60)
        except ReadTimeout as e:
            logger.error('Бот упал с ошибкой:')
            logger.error(e)
            continue
        except ConnectionError as e:
            logger.error('Бот упал с ошибкой:')
            logger.error(e)
            time.sleep(60)
            continue


def main():
    env.read_env()

    telegram_token = env.str('TELEGRAMM_API_KEY')
    chat_id = env.str('TELEGRAMM_CHAT_ID')
    devman_token = env.str('DEVMAN_TOKEN')
    url = "https://dvmn.org/api/long_polling/"
    tg_bot = telegram.Bot(token=telegram_token)

    class TelegramLogsHandler(logging.Handler):

        def __init__(self, tg_bot, chat_id):
            super().__init__()
            self.chat_id = chat_id
            self.tg_bot = tg_bot

        def emit(self, record):
            log_entry = self.format(record)
            self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)

    logger = logging.getLogger("Logger")
    logger.setLevel(logging.INFO)
    logger.addHandler(TelegramLogsHandler(tg_bot, chat_id))
    while True:
        try:
            logger.info('Бот работает')
            check_lesson(url, devman_token, tg_bot, chat_id, logger)
            time.sleep(60)
        except Exception as e:
            logger.error('Бот упал с ошибкой:')
            logger.error(e)


if __name__ == '__main__':
    main()
