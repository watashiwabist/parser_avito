import hashlib
import subprocess
import uuid

import pandas as pd
import pyaes

ads_list = []
proxy_list = []
thread_list = []
data = []
threads = []
bad_ads = []
bad_proxy = []
LOGIN = 'admin'
PASSWORD = 'admin'
admin_builds = ['eeebf960884ae7850df9a65be2d13737fa61c704223c716415bbc2a5680a17da', 'aboba',
                'eeef90277a7fadff4c98de649878a3fc6b61ea10c4afca773ad3dd072fef1085']
key = 'af0deccbgcgidddjgnvljitntccdduijhdinfgjgfjir'
crypt_key = 'pbyebb2LOi31KBx2eTyVRhxLC0kDbagD'

with open('vk.txt', 'r') as vk:
    vk = vk.read()
    vk = vk.split('\n') if vk != '' else ''

with open('ok.txt', 'r') as ok:
    ok = ok.read()
    ok = ok.split('\n') if ok != '' else ''


def current_build():
    mac_addr = hex(uuid.getnode()).replace('0x', '')
    return hash_crypt(mac_addr)


def hash_crypt(text):
    hash = hashlib.sha256(text)
    return hash.hexdigest()


def create_csv():
    print('create')
    df = pd.DataFrame(data, columns=['Название', 'Цена', 'Номер', 'Ссылка', 'WP', 'Логин'])
    df = df.set_index(df['Логин']).sort_index().drop(['Логин'], axis=1)
    df.to_excel('result.xlsx')


def out_bad(lst, path):
    with open(path, 'w') as file:
        for line in lst:
            file.write(f'{line}\n')


def delete_acc(login, password, path):
    with open(path, 'r+') as file:
        accs = file.readlines()
        accs = [i.strip() for i in accs]
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
