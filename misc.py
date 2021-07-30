import hashlib
import random
import string
import subprocess

import pandas as pd
import numpy as np

ads_list = []
proxy_list = []
thread_list = []
data = []
threads = []
admin_builds = ['eeebf960884ae7850df9a65be2d13737fa61c704223c716415bbc2a5680a17da']
LOGIN = 'admin'
PASSWORD = 'admin'

key = 'af0deccbgcgidddjgnvljitntccdduijhdinfgjgfjir'

with open('vk.txt', 'r') as vk:
    vk = vk.read().split('\n')

with open('ok.txt', 'r') as ok:
    ok = ok.read().split('\n')


def current_build():
    hwid = str(subprocess.check_output(
        'wmic csproduct get uuid')).split('\\r\\n')[1].strip('\\r').strip().encode('utf-8')
    hash = hashlib.sha256(hwid)
    return hash.hexdigest()


def create_csv():
    print('create')
    df = pd.DataFrame(data, columns=['Название', 'Цена', 'Номер', 'Ссылка', 'WP', 'Логин'])
    df = df.set_index(df['Логин']).sort_index().drop(['Логин'], axis=1)
    df.to_excel('aboba.xlsx')

def delete_acc(login, password, path):
    with open(path,'r+') as file:
        accs = file.readlines()
        accs.remove(f'{login}:{password}\n')
    with open(path, 'w') as file:
        [file.write(acc) for acc in accs]

