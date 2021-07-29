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
LOGIN = 'admin'
PASSWORD = 'admin'


def generate_user():
    source = string.ascii_lowercase + string.digits
    login = ''.join((random.choice(source)) for _ in range(5))
    password = ''.join((random.choice(source)) for _ in range(5))
    return login, password


def current_build():
    return 'aboba'
    hwid = str(subprocess.check_output(
        'wmic csproduct get uuid')).split('\\r\\n')[1].strip('\\r').strip().encode('utf-8')
    hash = hashlib.sha256(hwid)
    return hash.hexdigest()


def create_csv():
    print('create')
    df = pd.DataFrame(data, columns=['Название', 'Цена', 'Номер', 'Ссылка', 'WP', 'Логин'])
    df = df.set_index(df['Логин']).sort_index()
    df.to_excel('aboba.xlsx')

