# ----------------------------------
# Program by @Pcholken
#
#
# Date        Info
# 2020    Autoreger vk.com
#
# ----------------------------------
import logging
import requests
from threading import Thread
from time import sleep
from random import choice, randint

import vk_api

from utils import vk_auth, answer_from_sms_service, captcha_solver, wait_code, generate_password, write_log,\
    upload_photo, subscribe, get_proxy
from config import sms_token, country, first_name, last_name, sex, delay

logging.basicConfig(filename='logs.log',
                    filemode='a',
                    format='%(asctime)s - %(message)s',
                    datefmt='%d %b %H:%M:%S',
                    level=logging.INFO
                    )


def signup(proxy):
    vk = vk_auth(proxy)

    args = requests.get(
        url=f"https://smshub.org/stubs/handler_api.php?api_key={sms_token}&action=getNumber&service=vk&operator=any&"
            f"country={country}").text.split(":")

    logging.info(args)

    if not answer_from_sms_service(args):
        sleep(5)
        signup(proxy)

    else:
        print("Получен номер")

        activation_id = args[1]
        phone = str(args[2])
        try:
            vk.auth.signup(client_id=2274003, client_secret="hHbZxrka2uZ6jB1inYsH", phone=phone,
                           first_name=choice(first_name),
                           last_name=choice(last_name), sex=sex,
                           birthday=f"{randint(1, 28)}.{randint(1, 12)}.{randint(1980, 2000)}")

            confirm_signup(proxy, vk, phone, activation_id)

        except vk_api.exceptions.ApiError as error:
            logging.error(str(error))

            if "1004" in str(error) or "Invalid phone number" in str(error) or \
                    "One of the parameters specified was missing or invalid: can't accept this phone" in str(error) or \
                    'Flood control: sms sent limit' in str(error):

                requests.get(url=f"https://smshub.org/stubs/handler_api.php?api_key={sms_token}\
                &action=setStatus&status=8&id={activation_id}")

                print("Номер не доступен для регистрации")
                signup(proxy)

            elif "User authorization failed: no access_token passed" in str(error):
                print("Аккаунт был забанен при регистрации.")
                logging.error("Аккаунт был забанен при регистрации.")

            else:
                print("Неизвестная ошибка, отправьте лог разработчику.")
                print(error)

                requests.get(url=f"https://smshub.org/stubs/handler_api.php?api_key={sms_token}\
                &action=setStatus&status=8&id={activation_id}")

        except (requests.exceptions.ProxyError, requests.exceptions.ConnectionError) as error:
            print(error)
            print(f"Bad proxy {proxy}")
            logging.error(f"Bad proxy {proxy}")

            del proxyes[0]

            requests.get(
                url=f"https://smshub.org/stubs/handler_api.php?api_key={sms_token}&"
                    f"action=setStatus&status=8&id={activation_id}")

        except vk_api.Captcha as captcha:
            captcha_solver(captcha)
            confirm_signup(proxy, vk, phone, activation_id)


def confirm_signup(proxy, vk, phone, activation_id):
    global count
    code = wait_code(activation_id)

    if code == "resign":
        signup(proxy)
        return

    password = generate_password()

    if code != ["STATUS_CANCEL"]:
        vk.auth.confirm(client_id=2274003, client_secret="hHbZxrka2uZ6jB1inYsH", phone=phone, code=code.split(":")[1],
                        password=password)

        requests.get(
            url=f"https://smshub.org/stubs/handler_api.php?api_key={sms_token}&action=setStatus&status=6&id={activation_id}")

        count += 1
        print(f"{count} аккаунт зареган")
        logging.info(f"{count} аккаунт зареган")

        print(f"{phone}:{password}")
        logging.info(f"{phone}:{password}")

        write_log(login=phone, password=password, proxy=proxy)

    for _ in range(15):
        try:
            vk = vk_auth(login=phone, password=password, proxy=proxy)
            break
        except (requests.exceptions.ProxyError, requests.exceptions.ConnectionError):
            print(f"Ошибка авторизации Bad proxy {proxy}")
            logging.error(f"Ошибка авторизации Bad proxy {proxy}")
            sleep(20)
        except vk_api.Captcha as captcha:
            captcha_solver(captcha)

    try:
        upload_photo(vk)
    except vk_api.Captcha as captcha:
        captcha_solver(captcha)

    try:
        subscribe(vk)
    except vk_api.Captcha as captcha:
        captcha_solver(captcha)


def main():
    needCount = int(input("Необходимое количество аккаунтов: "))
    threadCount = int(input("Количество потоков (кратно количеству акков): "))
    for _ in range(int(needCount / threadCount)):
        threads = []
        for thread in range(threadCount):
            try:
                proxy = proxyes[thread]
            except:
                print("Прокси закончились.")
                return
            procces = Thread(target=signup, args=(proxy,))
            threads.append(procces)
            procces.start()
        for thread in threads:
            thread.join()
        print(f"Задержка на {delay}")
        sleep(delay)


if __name__ == '__main__':
    count = 0
    proxyes = get_proxy()
    main()
