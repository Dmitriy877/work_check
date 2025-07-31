import requests
from environs import env


def main():
    env.read_env()
    token = env.str('TOKEN')

    headers = {
        "Authorization": token,
    }

    url = 'https://dvmn.org/api/user_reviews/'

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    print(response.json())


if __name__ == '__main__':
    main()
