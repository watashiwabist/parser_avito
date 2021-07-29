import json
import re
import threading
import time

import openpyxl
from loguru import logger
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from get_chromedriver import get_chromedriver
from misc import ads_list, data

number_links = 0


def get_numb(number_element):
    link = json.loads(number_element.replace('"', '"'))
    try:
        if link['status'] == 'ok':
            if link['result']['action']['uri'] == 'ru.avito://1/authenticate':
                return 0
            return re.split('[A-z]', link['result']['action']['uri'])[-1]
        else:
            return 0
    except:
        return 0


def get_driver(use_proxy):
    driver = get_chromedriver(use_proxy, mobile=True)
    return driver


def get_info_ads(driver, link_ads):
    driver.get(link_ads)
    title = driver.find_element_by_xpath(
        '//*[@id="app"]/div/div[2]/div/div[2]/div/div[1]/div/div[1]/div/h1/span').text
    price = driver.find_element_by_xpath(
        '/html/body/div[1]/div/div[2]/div/div[2]/div/div[1]/div/div[2]/p/span/span').text
    return title, price


def is_bad_proxy(browser):
    try:
        try:
            WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div/h2')))
        except TimeoutException:
            return 0
        bad_ip_text = browser.find_element_by_xpath('/html/body/div[2]/div/h2').text
        if bad_ip_text == 'Доступ с Вашего IP временно ограничен':
            return 1
    except NoSuchElementException:
        return 0
    return 1


class AuthVK:
    def __init__(self, login, password, or_not_proxy):
        self.login = login
        self.password = password
        self.proxy = or_not_proxy

    def get_links_in_xslx(self):
        wb = openpyxl.load_workbook('result.xlsx')
        wb.active = 0
        sheets = wb.active
        row_count = sheets.max_row
        data = []
        for i in range(int(row_count)):
            name = sheets[('A' + str(i + 1))].value
            price = sheets[('b' + str(i + 1))].value
            link = sheets[('C' + str(i + 1))].value
            data.append([str(name), str(price), str(link)])
        else:
            return data

    def auth_vk(self, driver):
        try:
            driver.get('http://vk.com')
            time.sleep(2)

            driver.find_element_by_name('email').send_keys(self.login)
            # time.sleep(1)
            driver.find_element_by_name('pass').send_keys(self.password)
            # time.sleep(1)
            driver.find_element_by_xpath('//*[@id="mcont"]/div[1]/div[2]/div/div/form/div[1]/input').click()
            time.sleep(2)

            feed = driver.find_element_by_id('header__title').text
            if feed == u'\u041d\u043e\u0432\u043e\u0441\u0442\u0438':
                logger.info('Auth VK - OK')
                return 1
            else:
                return 0
        except Exception:
            return 0

    @logger.catch()
    def test_auth_token(self):
        try:
            driver = get_driver(self.proxy)
            vk = self.auth_vk(driver)
            if vk:
                driver.get('https://m.avito.ru/profile/settings#login?forceMode=true')
                while is_bad_proxy(driver):
                    driver.get('https://m.avito.ru/profile/settings#login?forceMode=true')
                time.sleep(2)
                driver.find_element_by_xpath('//*[@id="modal"]/div/div/div/div[1]/a[1]').click()
                time.sleep(6)
                lock = threading.Lock()
                while ads_list:
                    lock.acquire()
                    link = ads_list.pop()
                    lock.release()
                    item_id = link.split('_')[-1]
                    api_get_number_offer = f'https://m.avito.ru/api/1/items/{item_id}/phone?key=af0deccbgcgidddjgnvljitntccdduijhdinfgjgfjir'
                    driver.get(api_get_number_offer)
                    phone_key = driver.find_element_by_xpath('/html/body/pre').text
                    phone_number = get_numb(phone_key)
                    if phone_number:
                        title, price = get_info_ads(driver, link)
                        wp = f'https://api.whatsapp.com/send?phone={phone_number}'
                        logger.success(f'ID_ITEM: {item_id} || NUMBER: {phone_number}')
                        data.append(
                            [title, price, phone_number, link, wp, self.login])
                    else:
                        logger.error(f'ID_ITEM: {item_id}')
                driver.close()
            else:
                logger.error('Auth VK - ERROR')
        except Exception as e:
            print(e)


def start_vk(acc, or_not_proxy):
    # global number_links
    # try:
    #     file = open('final.txt', 'w')
    #     file.close()
    # except:
    #     pass
    # else:
    #     acc = ['89515490575', '228007da*']
    #     wb = openpyxl.load_workbook('result.xlsx')
    #     wb.active = 0
    #     sheets = wb.active
    #     row_count = sheets.max_row
    #     autorization = AuthVK(acc[0], acc[1])
    #     if number_links == row_count:
    #         logger.debug('Full Numbers Accepted')
    #     else:
    #         autorization.test_auth_token()
    autorization = AuthVK(acc[0], acc[1], or_not_proxy)
    autorization.test_auth_token()

# if __name__ == '__main__':
#     start_vk()
