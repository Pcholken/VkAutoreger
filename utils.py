# ---------------------------
# Program by Pcholken
#
#
# Date        Info
# 2020   File wtih methods
#
# ---------------------------
from random import sample, choice
import logging
from os import system, walk
from string import ascii_lowercase, digits
from base64 import b64encode
from time import sleep

from twocaptcha import TwoCaptcha
import requests
import vk_api

from config import to_subscribe, to_subscribe_communities, rucaptcha_token, captcha_type, log_type, sms_token


def generate_password():
    letters = ascii_lowercase + digits
    return 'pcholkenLolzteam' + ''.join(sample(letters, 10))


def vk_auth(proxy, login=None, password=None):
    vk_session = vk_api.VkApi(login=login, password=password)
    vk_session.http.proxies = {
        "http": f"http://{proxy}",
        "https": f"http://{proxy}"
    }
    if login and password is not None:
        vk_session.auth()
        system("rm vk_config.v2.json")
    return vk_session.get_api()


def get_token(login, password, proxy):
    vk_session = vk_api.VkApi(login=login, password=password)
    vk_session.http.proxies = {
        "http": f"http://{proxy}",
        "https": f"http://{proxy}"
    }

    vk_session.auth(token_only=True)

    print(vk_session.token)

    return vk_session.token['access_token'], vk_session.token['user_id']


def subscribe(vk):
    for user_id in to_subscribe:
        print(f"Подписка на {user_id}")
        try:
            vk.friends.add(user_id=user_id)
        except Exception as captcha:
            captcha_solver(captcha)
        sleep(2)

    for user_id in to_subscribe_communities:
        print(f"Подписка на {user_id}")
        vk.groups.join(group_id=user_id)
        sleep(1)


def upload_photo(vk):

    upload_url = vk.photos.getOwnerPhotoUploadServer()['upload_url']

    for _, _, files in walk("photos"):
        photos = files

    if photos != []:
        request = requests.post(upload_url, files={'photo': open(f"photos/{choice(photos)}", "rb")})

        params = {'server': request.json()['server'],
                  'photo': request.json()['photo'],
                  'hash': request.json()['hash']}

        vk.photos.saveOwnerPhoto(**params)


def captcha_solver(captcha):
    try:
        if not captcha_type:  # Ручной ввод
            print(captcha.get_url())
            captcha.try_again(input("Код с картинки => "))
            logging.info("Каптча решена успешно")
        else:
            solver = TwoCaptcha(rucaptcha_token)
            code = solver.normal(b64encode(captcha.get_image()).decode("utf-8"))
            captcha.try_again(code['code'])
            logging.info("Каптча решена успешно")
    except:
        logging.warning("Каптча не решена")


def get_proxy():
    proxyes = open("proxyes.txt").read().strip().split('\n')
    return proxyes


def write_log(login, password, proxy):
    print("Запись лога")

    if log_type == 0:
        with open("goods.txt", "a") as file:
            file.write(f"{login}:{password}\n")
        return

    try:
        token, user_id = get_token(login, password, proxy)
    except vk_api.Captcha as captcha:
        captcha_solver(captcha)
        token, user_id = get_token(login, password, proxy)

    except (requests.exceptions.ProxyError, requests.exceptions.ConnectionError) as error:
        logging.error(error)
        for _ in range(15):
            try:
                token, user_id = get_token(login, password, proxy)
                break
            except (requests.exceptions.ProxyError, requests.exceptions.ConnectionError):
                print(f"Bad proxy {proxy}, reconnect")
                sleep(20)
    except Exception as error:
        logging.error(error)
        print("Ошибка, невозможно получить токен.")
        logging.error("Невозможно получить токен.")

        with open("goods.txt", "a") as file:
            file.write(f"{login}:{password}\n")
        return

    if log_type == 1:
        with open("goods.txt", "a") as file:
            file.write(f"{login}:{password}:{token}\n")

    elif log_type == 2:
        with open("goods.txt", "a") as file:
            file.write(f"{login}:{password}:{user_id}\n")

    elif log_type == 3:
        with open("goods.txt", "a") as file:
            file.write(f"{login}:{password}:{token}:{user_id}\n")

    else:
        with open("goods.txt", "a") as file:
            file.write(f"{login}:{password}\n")


def wait_code(activation_id):
    for i in range(12):
        sleep(5)
        respone = requests.get(
            url=f"https://smshub.org/stubs/handler_api.php?api_key={sms_token}&action=getStatus&id={activation_id}").text
        print(respone)
        if respone == "STATUS_WAIT_CODE":
            if i == 11:
                requests.get(
                    url=f"https://smshub.org/stubs/handler_api.php?api_key={sms_token}&action=setStatus&status=8&id={activation_id}")
                print("Смс не пришло")
                logging.warning("Смс не пришло")
                return "resign"
            continue
        print("Найдено смс")
        return respone


def answer_from_sms_service(respone):
    if respone == ['NO_NUMBERS']:
        print("Номеров нет в наличии\nПопробуйте позже")
        logging.warning("Номеров нет в наличии")

    elif respone == ['NO_BALANCE']:
        print("Не достаточно баланса на сервисе")
        logging.warning("Не достаточно баланса на сервисе")

    elif respone == ['Ошибка покупки']:
        print("Ошибка покупки,попробуйте снова")
        logging.error("Ошибка покупки,попробуйте снова")

    elif respone == ['BAD_KEY']:
        print("Неверный апи ключ от смс сервиса")
        logging.warning("Неверный апи ключ от смс сервиса")

    elif respone[0] == 'BANNED':
        print(f"Вы были забаннены до {respone[1]}:{respone[2]}:{respone[3]}")
        logging.error("Бан на смс сервисе")

    elif respone == ['']:
        pass

    else:
        return True
