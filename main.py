import json
import re
import threading
import time
from multiprocessing.pool import ThreadPool
from pprint import pprint

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from threading import Thread

key = 'af0deccbgcgidddjgnvljitntccdduijhdinfgjgfjir'

with open('ads.txt', 'r') as ads:
    ads = ads.read().split('\n')

with open('vk.txt', 'r') as vk:
    vk = vk.read().split('\n')

with open('ok.txt', 'r') as ok:
    ok = ok.read().split('\n')

login_in_via_link = 'https://m.avito.ru/profile/settings#login?forceMode=true'
title_xpath = '/html/body/div[1]/div/div[2]/div/div[2]/div/div[1]/div/div[1]/div/h1/span'
price_xpath = '/html/body/div[1]/div/div[2]/div/div[2]/div/div[1]/div/div[2]/p/span/span'
number_xpath = '/html/body/pre'
api_link = 'https://m.avito.ru/api/1/items/'


def is_bad_vk(browser, xpath):
    try:
        browser.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    return True


def is_bad_proxy(browser):
    try:
        bad_ip_text = browser.find_element_by_xpath('/html/body/div[2]/div/h2').text
        if bad_ip_text == 'Доступ с Вашего IP временно ограничен':
            return True
    except NoSuchElementException:
        return False
    return True


def get_numb(number_element):
    link = json.loads(number_element.replace('"', '"'))
    return re.split('[A-z]', link['result']['action']['uri'])[-1]


def auth_vk(acc):
    driver = '/Users/sbayra/Desktop/chromedriver'
    options = webdriver.ChromeOptions()
    # options.add_argument('headless')
    options.add_argument(
        "--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) "
        "CriOS/56.0.2924.75 Mobile/14E5239e Safari/602.1")
    browser = webdriver.Chrome(driver, options=options)
    link_ads = ads[0]
    link_id = ads[0].split('_')[-1]
    browser.get('http://m.vk.com')
    login_input = browser.find_element_by_xpath(
        '/html/body/div[2]/div[2]/div[2]/div/div[3]/div[1]/div[2]/div/div/form/dl[1]/dd/label/div/input')
    login_input.send_keys('+79950953487')
    password_input = browser.find_element_by_xpath(
        '/html/body/div[2]/div[2]/div[2]/div/div[3]/div[1]/div[2]/div/div/form/dl[2]/dd/label/div/div[1]/input')
    password_input.send_keys('smailbu1')
    browser.find_element_by_xpath(
        '/html/body/div[2]/div[2]/div[2]/div/div[3]/div[1]/div[2]/div/div/form/div[1]/input').click()
    if is_bad_vk(browser, '/html/body/div[2]/div[2]/div[2]/div/div[3]/div[1]/div[2]/div/div/div[2]/div/div'):
        return
    else:
        browser.get(login_in_via_link)
        if is_bad_proxy(browser):
            print('BAD PROXY')
            return 'bad proxy'
        else:
            browser.find_element_by_xpath('/html/body/div[3]/div/div/div/div[1]/a[1]/div').click()
            time.sleep(2)
            browser.get(link_ads)
            title = browser.find_element_by_xpath(title_xpath).text
            price = browser.find_element_by_xpath(price_xpath).text
            browser.get(f'{api_link}{link_id}/phone?key={key}')
            number_element = browser.find_element_by_xpath(number_xpath).text
            number = get_numb(number_element)
            print(f'{title} - {price} - {number}')
            time.sleep(60)


def auth_ok(acc):
    driver = '/Users/sbayra/Desktop/chromedriver'
    options = webdriver.ChromeOptions()
    # options.add_argument('headless')
    options.add_argument(
        "--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) "
        "CriOS/56.0.2924.75 Mobile/14E5239e Safari/602.1")
    browser = webdriver.Chrome(driver, options=options)
    link_ads = ads[0]
    link_id = ads[0].split('_')[-1]
    browser.get('https://m.ok.ru/cdk/st.cmd/main/tkn/890?_prevCmd=mainLanding')
    login_input = browser.find_element_by_xpath(
        '/html/body/div[1]/div[2]/div/div[1]/form/div/div[1]/div/div/input')
    login_input.send_keys('+79178721123')
    password_input = browser.find_element_by_xpath(
        '/html/body/div[1]/div[2]/div/div[1]/form/div/div[2]/div/div/input')
    password_input.send_keys('z94dkt3p')
    browser.find_element_by_xpath(
        '/html/body/div[1]/div[2]/div/div[1]/form/div/div[3]/div/input').click()
    if is_bad_vk(browser, '/html/body/div[1]/div[2]/div/div[1]/form/div/div[1]'):
        return
    else:
        browser.get(login_in_via_link)
        if is_bad_proxy(browser):
            print('BAD PROXY')
            return 'bad proxy'
        browser.find_element_by_xpath('/html/body/div[3]/div/div/div/div[1]/a[2]/div').click()
        windows_handles = browser.window_handles
        browser.switch_to.window(windows_handles[1])
        time.sleep(1)
        browser.find_element_by_xpath('/html/body/div/form/div/div[3]/button').click()
        browser.switch_to.window(windows_handles[0])
        time.sleep(1)
        browser.get(link_ads)
        title = browser.find_element_by_xpath(title_xpath).text
        price = browser.find_element_by_xpath(price_xpath).text
        browser.get(f'{api_link}{link_id}/phone?key={key}')
        number_element = browser.find_element_by_xpath(number_xpath).text
        number = get_numb(number_element)
        print(f'{title}-{price}-{number}')
        time.sleep(60)


# if __name__ == '__main__':
#
#     for i in range(2):
#         threading.Thread(target=auth_vk, args=('',)).start()






# import csv
#
#
# def csv_writer(data, path):
#     """
#     Write data to a CSV file path
#     """
#     with open(path, "w", newline='') as csv_file:
#         writer = csv.writer(csv_file, delimiter=',')
#         for line in data:
#             writer.writerow(line)
#
#
# if __name__ == "__main__":
#     data = ["Название,Прайс,Номер,Ссылка".split(","),
#             "AirPods 2 / AirPods PRO Новые (На гарантии),1900Р,79178721123, "
#             "'https://www.avito.ru/ekaterinburg/audio_i_video/airpods_2_airpods_pro_novye_na_garantii_2154932879"
#             "".split(","),
#             ]
#
#     path = "output.csv"
#     csv_writer(data, path)
