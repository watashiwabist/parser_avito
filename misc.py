import hashlib
import random
import string
import threading
import time
import uuid

import pandas as pd
import pyaes
from python_anticaptcha import AnticaptchaClient

encode_str = 'windows-1251'
ads_list = []
thread_list = []
data = []
threads = []
bad_ads = []
bad_proxy = []
good_acc = []
ZERO_ACC = '89515490575:228007da*'
LOGIN = 'admin'
PASSWORD = 'k3fa4'
admin_builds = ['a660a555c570e8d2bf5004ebf68829bf81d3651b709c7e1d3f9b22b2a8e471e3',
                'fd8ceebf8605c623e877bbcd8f7eb4828b98d69c7fd545be97d5150202e3f0f1',
                'a17ea537c511bb1991e25c466eea2472d96eab2cb601e4f7939c6f0a042aaa04',
                'd4710ab48ae334543ed105666ec50e03477b79f95577c7d367643ea7ca7566f2']  # 1mac, 2win, 3og

key = 'af0deccbgcgidddjgnvljitntccdduijhdinfgjgfjir'
crypt_key = 'pbyebb2LOi31KBx2eTyVRhxLC0kDbagD'

with open('vk.txt', 'r', encoding=encode_str) as vk:
    vk = vk.read()
    vk = vk.split('\n') if vk != '' else ''

with open('ok.txt', 'r', encoding=encode_str) as ok:
    ok = ok.read()
    ok = ok.split('\n') if ok != '' else ''

with open('proxy.txt', mode='r', encoding=encode_str) as proxy_list:
    proxy_list = proxy_list.read()
    proxy_list = proxy_list.split('\n') if proxy_list != '' else ''
    proxy_list = [(i, 0) for i in proxy_list]

with open('sessid.txt', 'r', encoding=encode_str) as sessid:
    sessid = sessid.read()
    sessid = sessid.split('\n') if sessid != '' else ''


def id_generator(size=5, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def current_build():
    mac_addr = hex(uuid.getnode()).replace('0x', '').encode(encode_str)
    return hash_crypt(mac_addr)


def hash_crypt(text):
    hash = hashlib.sha256(text)
    return hash.hexdigest()


def create_xlsx():
    print('create')
    df = pd.DataFrame(data, columns=['Название', 'Цена', 'Номер', 'Ссылка', 'WP', 'Логин'])
    df = df.set_index(df['Логин']).sort_index().drop(['Логин'], axis=1)
    df.to_excel('result.xlsx')


def out_bad(lst, path):
    with open(path, 'w') as file:
        for line in lst:
            file.write(f'{line}\n')


def read_txt(path):
    with open(path) as link_file:
        for link in link_file:
            ads_list.append((link.strip(), 0))
    return link_file


def delete_acc(login, password, path):
    with open(path, 'r+') as file:
        accs = file.readlines()
        accs = [i.strip() for i in accs]
        acc = f'{login}:{password}'
        if acc in accs:
            accs.remove(f'{login}:{password}')
    with open(path, 'w') as file:
        [file.write(f'{acc}\n') for acc in accs]


def encode(text):
    curr_key = crypt_key.encode('utf-8')
    aes = pyaes.AESModeOfOperationCTR(curr_key)
    ciphertext = aes.encrypt(text)
    return ciphertext


def decode(text):
    curr_key = crypt_key.encode('utf-8')
    aes = pyaes.AESModeOfOperationCTR(curr_key)
    decrypted = aes.decrypt(text).decode('utf-8')
    return decrypted


def create_txt(path):
    with open(path, 'w') as file:
        pass


def output_txt(path, acc):
    with open(path, 'a') as file:
        if type(acc) == list:
            map(lambda x: file.write(f'{x[0]}\n' if path == 'unparsed_links.txt' else f'{x}\n'), acc)
        else:
            file.write(f'{acc}\n')


def check_login(login, password):
    logged, logged_admin = False, False
    if login == LOGIN and password == PASSWORD:
        logged = True
        logged_admin = True
    else:
        with open('accounts', mode='r+', encoding='windows-1251') as file_accs:
            accs = file_accs.read().splitlines()
            entered_acc = f'{login}:{password}'
            crypted_entered = hash_crypt(encode(entered_acc))
            for account in accs:
                if logged:
                    break
                if crypted_entered == account:
                    with open('machines', mode='r+', encoding='windows-1251') as file_machine:
                        codes = file_machine.read().splitlines()
                        build = current_build()
                        if build in admin_builds:
                            logged_admin = True
                        if build in codes:
                            logged = True
                        elif len(codes) != len(accs):
                            file_machine.write(f'{build}\n')
                            logged = True
    return logged, logged_admin


def auth_start():
    login = input('Введите логин\n')
    password = input('Введите пароль\n')
    return check_login(login, password)


def check_balance(api_key):
    try:
        client = AnticaptchaClient(api_key, language_pool='ru')
        print(f'На вашем счету: {client.getBalance()}$')
    except:
        return -1


def check_threads(threads_was_opened, thread_count, final=None):
    try:
        while len(threading.enumerate()) != threads_was_opened:
            if not final and (thread_count + threads_was_opened > len(threading.enumerate())) and len(good_acc):
                break
            time.sleep(0.5)
    except:
        raise Exception('Close')
