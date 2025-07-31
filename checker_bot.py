import requests
import time
from requests.exceptions import ReadTimeout, ConnectionError
from environs import env
from bot import telegram_send_message


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
        telegram_token,
        chat_id,
        timestamp: float = None
) -> dict:
    while True:
        try:
            response_raw = get_response(url, devman_token, timestamp)
            if response_raw['status'] == 'timeout':
                timestamp = response_raw['timestamp_to_request']
            if response_raw['status'] == 'found':
                new_attempts = response_raw['new_attempts'][0]
                telegram_send_message(
                    telegram_token,
                    chat_id,
                    is_negative=new_attempts['is_negative'],
                    lesson_url=new_attempts['lesson_url'],
                    lesson_title=new_attempts['lesson_title']
                )
        except ReadTimeout:
            continue
        except ConnectionError:
            print(
                "Потреяно соедиение, будет выполнена попытка переподключения"
            )
            time.sleep(60)
            continue


def main():
    env.read_env()
    telegram_token = env.str('TELEGRAMM_API_KEY')
    chat_id = env.str('TELEGRAMM_CHAT_ID')
    devman_token = env.str('DEVMAN_TOKEN')
    url = "https://dvmn.org/api/long_polling/"
    check_lesson(url, devman_token, telegram_token, chat_id)


if __name__ == '__main__':
    main()
