# ----------------------------------
# Program by Pcholken
#
#
# Date        Info
# 2020       Config
#
# ----------------------------------
log_type = 1  # 0=login:password, 1=login:password:token, 2=login:password:id, 3=login:password:token:id

sms_token = ""  # Апи ключ sms-hub

delay = 10  # Задержа между потоками в секудах

country = "6"  # http://smshub.org/main#getCountries

captcha_type = 1  # 0=Ручной ввод, 1=Рупча.

rucaptcha_token = ""

first_name = \
'''
Дмитрий
Иван
'''.split("\n")[1:][:-1]

last_name = \
'''
Пчелкин
'''.split("\n")[1:][:-1]

sex = 0  # 0=male 1=female

birthday = "20.07.2000"

to_subscribe = [324355825]  # Страницы на которые аккаунт подпишется (id)

to_subscribe_communities = []  # Группы на которые аккаунт подпишется (id с минусом)
