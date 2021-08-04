import json
import re
import threading
import time

import openpyxl
from loguru import logger
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from get_chromedriver import get_chromedriver
from misc import ads_list, data, delete_acc, key, proxy_list, bad_ads, bad_proxy

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
    driver, proxy = get_chromedriver(use_proxy, mobile=True)
    return driver, proxy


def get_info_ads(driver, link_ads):
    try:
        driver.get(link_ads)
        title = driver.find_element_by_xpath(
            '//*[@id="app"]/div/div[2]/div/div[2]/div/div[1]/div/div[1]/div/h1/span').text
        price = driver.find_element_by_xpath(
            '/html/body/div[1]/div/div[2]/div/div[2]/div/div[1]/div/div[2]/p/span/span').text
        return title, price
    except:
        return 0, 0


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
        try:
            time.sleep(2)
            browser.find_element_by_xpath('//*[@id="modal"]/div/div/div/div[1]/a[1]')
            return 0
        except:
            return 1
    return 1


def get_links_in_xslx():
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


class Link:
    def __init__(self, link, bad):
        self.link = link
        self.bad = bad

    def get_params(self):
        return self.link, self.bad


class AuthVK:
    def __init__(self, login, password, or_not_proxy, soc):
        self.login = login
        self.password = password
        self.proxy = or_not_proxy
        self.bad = 0
        self.soc = soc

    def auth_vk(self, driver):
        try:
            driver.get('http://vk.com')
            time.sleep(2)

            driver.find_element_by_name('email').send_keys(self.login)
            # time.sleep(1)
            driver.find_element_by_name('pass').send_keys(self.password)
            # time.sleep(1)
            driver.find_element_by_xpath('//*[@id="mcont"]/div[1]/div[2]/div/div/form/div[1]/input').click()
            try:
                driver.find_element_by_id('captcha')

                driver.quit()
                return -1
            except:
                pass
            time.sleep(2)

            feed = driver.find_element_by_id('header__title').text
            if feed == 'Новости' or feed == 'News':
                logger.info('Auth VK - OK')
                return 1
            else:
                return 0
        except Exception as e:
            print(e)
            if 'unknown error: net::ERR_PROXY_CONNECTION_FAILED' in str(e):
                return -2
            return 0

    def auth_ok(self, driver):
        try:
            driver.get('https://m.ok.ru/cdk/st.cmd/main/tkn/890?_prevCmd=mainLanding')
            time.sleep(2)
            driver.find_element_by_name('fr.login').send_keys(self.login)
            driver.find_element_by_name('fr.password').send_keys(self.password)
            driver.find_element_by_xpath('/html/body/div[1]/div[2]/div/div[1]/form/div/div[3]/div/input').click()
            time.sleep(3)
            try:
                driver.find_element_by_class_name('content-card_avatar').text
                logger.info('Auth OK - OK')
                return 1
            except Exception:
                return 0
        except Exception:
            return 0

    @logger.catch()
    def test_auth_token(self):
        vk, ok = None, None
        try:
            driver, curr_proxy = get_driver(self.proxy)
            if self.soc == 1:
                vk = self.auth_vk(driver)
            else:
                ok = self.auth_ok(driver)
            if vk == 1 or ok:
                driver.get('https://m.avito.ru/profile/settings#login?forceMode=true')
                while is_bad_proxy(driver):
                    driver.get('https://m.avito.ru/profile/settings#login?forceMode=true')
                if ok:
                    driver.find_element_by_xpath('/html/body/div[3]/div/div/div/div[1]/a[2]/div').click()
                    time.sleep(2)
                    driver.switch_to.window(driver.window_handles[1])
                    driver.find_element_by_xpath('/html/body/div/form/div/div[3]/button').click()
                    time.sleep(8)
                    if len(driver.window_handles) > 1:
                        driver.refresh()
                        time.sleep(8)
                    try:
                        driver.switch_to.window(driver.window_handles[0])
                    except AttributeError:
                        pass
                elif vk:
                    driver.find_element_by_xpath('//*[@id="modal"]/div/div/div/div[1]/a[1]').click()
                    time.sleep(8)
                    try:
                        driver.switch_to_window(driver.window_handles[1])
                        driver.find_element_by_xpath(
                            '/html/body/div[2]/div[2]/div[2]/div/div[3]/div/div/div[2]/form/div/input').click()
                        time.sleep(3)
                    except:
                        pass
                    if len(driver.window_handles) > 1:
                        driver.refresh()
                        time.sleep(8)
                        driver.switch_to_window(driver.window_handles[0])

                try:
                    check_auth = driver.find_element_by_xpath('/html/body/div[3]/div/div/div/div[2]').text
                    if str(check_auth).lower() == 'войти через телефон или почту':
                        delete_acc(self.login, self.password, 'vk.txt' if vk else 'ok.txt')
                        logger.error(
                            f'BAN IN AVITO || VK - {self.login}' if vk else f'BAN IN AVITO || OK - {self.login}')
                        driver.quit()
                        return 0
                except:
                    pass
                time.sleep(3)
                lock = threading.Lock()
                while ads_list:
                    lock.acquire()
                    link, bad = ads_list.pop()
                    while 'avito.ru' not in link:
                        link, bad = ads_list.pop()
                    lock.release()
                    if bad >= 5:
                        bad_ads.append(link)
                        continue
                    item_id = link.split('_')[-1]
                    api_get_number_offer = f'https://m.avito.ru/api/1/items/{item_id}/phone?key={key}'
                    driver.get(api_get_number_offer)
                    phone_key = driver.find_element_by_xpath('/html/body/pre').text
                    phone_number = get_numb(phone_key)
                    if phone_number:
                        title, price = get_info_ads(driver, link)
                        if not title or not price:
                            logger.error(f'ID_ITEM: {item_id} || LOGIN: {self.login}')
                            ads_list.insert(0, (link, bad + 1))
                            self.bad += 1
                            return
                        wp = f'https://api.whatsapp.com/send?phone={phone_number}'
                        logger.success(f'ID_ITEM: {item_id} || NUMBER: {phone_number} || LOGIN: {self.login}')
                        self.bad = 0
                        data.append(
                            [title, price, phone_number, link, wp, self.login])
                    else:
                        if self.bad > 10:
                            driver.quit()
                            logger.error(f'ID_ITEM: {item_id} || DEAD ACC: {self.login}')
                            return
                        logger.error(f'ID_ITEM: {item_id} || LOGIN: {self.login}')
                        ads_list.insert(0, (link, bad + 1))
                        self.bad += 1
                driver.quit()
            else:
                driver.quit()
                if self.soc:
                    if vk == -1:
                        logger.error('Auth VK - Captcha | Bad Proxy')
                        if curr_proxy:
                            curr_proxy[1] += 1
                    elif vk == 0:
                        delete_acc(self.login, self.password, 'vk.txt')
                        logger.error(f'Auth VK - ERROR || {self.login}')
                    if vk == -2 or (curr_proxy and curr_proxy[1] >= 3):
                        logger.error(f'BAD PROXY - DELETING || {curr_proxy[0]}')
                        proxy_list.remove(curr_proxy)
                        bad_proxy.append(curr_proxy[0])
                else:
                    logger.error(f'Auth OK - ERROR || {self.login}')
                    delete_acc(self.login, self.password, 'ok.txt')
        except Exception as e:
            print(e)


def start(acc, or_not_proxy, soc):
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
    autorization = AuthVK(acc[0], acc[1], or_not_proxy, soc)
    autorization.test_auth_token()

# if __name__ == '__main__':
#     start_vk()
