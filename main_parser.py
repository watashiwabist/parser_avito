import json
import os
import re
import threading
import time
import copy
import openpyxl
from loguru import logger
from python_anticaptcha import AnticaptchaClient, ImageToTextTask
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from get_chromedriver import get_chromedriver
from misc import ads_list, data, delete_acc, key, proxy_list, id_generator, create_txt, auth_start, \
    read_txt, check_balance, ok, vk, check_threads, hash_crypt, encode, output_txt, create_xlsx, good_acc, sessid

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

            try:
                bad_prxy = browser.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/h1/span').text
            except:
                return 0
            if bad_prxy.lower() == 'не удается получить доступ к сайту':
                return -1
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


def check_captcha(driver):
    try:
        captcha_link = driver.find_element_by_id('captcha').get_attribute('src')
        return captcha_link
    except NoSuchElementException:
        return 0


def get_captcha(driver):
    try:
        file_name = f'{id_generator(size=25)}.png'
        with open(file_name, 'wb') as file:
            file.write(driver.find_element_by_id('captcha').screenshot_as_png)
        # api_key = 'f3167e161abf12aa48a91735265e8162'
        captcha_fp = open(file_name, 'rb')
        captcha_fp = open(file_name, 'rb')
        client = AnticaptchaClient(api_key)
        task = ImageToTextTask(captcha_fp)
        job = client.createTask(task)
        job.join()
        captcha_fp.close()
        try:
            os.remove(os.getcwd() + f'\\{file_name}')
        except FileNotFoundError:
            logger.error('Не удалось удалить фото капчи')
        logger.success('Капча распознана')
        return job.get_captcha_text()
    except Exception as e:
        print(e)
        logger.error('Не удалось распознать капчу')


class AuthVK:
    def __init__(self, login, password, or_not_proxy, soc, sess=None):
        self.login = login
        self.password = password
        self.proxy = or_not_proxy
        self.bad = 0
        self.soc = soc
        self.sess = sess

    def auth_vk(self, driver):
        try:
            driver.get('http://vk.com')
            time.sleep(2)
            captcha_link = check_captcha(driver)
            if captcha_link:
                captcha_value = get_captcha(driver)
                driver.find_element_by_name('captcha_key').send_keys(captcha_value)
            driver.find_element_by_name('email').send_keys(self.login)
            driver.find_element_by_name('pass').send_keys(self.password)
            driver.find_element_by_xpath('//*[@id="mcont"]/div[1]/div[2]/div/div/form/div[1]/input').click()
            time.sleep(2)
            captcha_link = check_captcha(driver)
            if captcha_link:
                driver.find_element_by_name('pass').send_keys(self.password)
                captcha_value = get_captcha(driver)
                driver.find_element_by_name('captcha_key').send_keys(captcha_value)
                driver.find_element_by_xpath('//*[@id="mcont"]/div[1]/div[2]/div/div/form/div[1]/input').click()
            time.sleep(2)
            try:
                feed = driver.find_element_by_id('header__title').text
                if feed == 'Новости' or feed == 'News':
                    logger.info('Auth VK - OK')
                    return 1
                else:
                    return 0
            except:
                return 0
        except Exception as e:
            if 'unknown error: net::ERR_PROXY_CONNECTION_FAILED' in str(e):
                return -2
            return 0

    def auth_ok(self, driver):
        try:
            driver.get('https://m.ok.ru/cdk/st.cmd/main/tkn/890?_prevCmd=mainLanding')
            time.sleep(2)
            driver.find_element_by_name('fr.login').send_keys(self.login)
            driver.find_element_by_name('fr.password').send_keys(self.password)
            if check_captcha(driver):
                captcha_value = get_captcha(driver)
                if captcha_value is None:
                    captcha_value = get_captcha(driver)
                else:
                    driver.find_element_by_id('field_code').clear()
                    driver.find_element_by_id('field_code').send_keys(captcha_value)
            driver.find_element_by_class_name('base-button_target').click()
            time.sleep(3)
            try:
                driver.find_element_by_name('accept_profile').click()
            except:
                pass
            else:
                try:
                    if check_captcha(driver):
                        captcha_value = get_captcha(driver)
                        if captcha_value is None:
                            captcha_value = get_captcha(driver)
                        else:
                            driver.find_element_by_id('field_code').clear()
                            driver.find_element_by_id('field_code').send_keys(captcha_value)
                            driver.find_element_by_class_name('base-button_target').click()
                            time.sleep(2)
                            driver.find_element_by_class_name('base-button_target').click()

                except:
                    return 0
            if check_captcha(driver):
                captcha_value = get_captcha(driver)
                driver.find_element_by_id('field_code').clear()
                driver.find_element_by_id('field_code').send_keys(captcha_value)
                driver.find_element_by_class_name('base-button_target').click()
                time.sleep(3)
            try:
                driver.find_element_by_class_name('content-card_avatar')
                logger.info('Auth OK - OK')
                return 1
            except Exception:
                pass
            try:
                feed_text = driver.find_element_by_xpath('/html/body/div[1]/div[6]/div/div[1]/div[1]/span/h1').text
                if 'с чего начать' in str.lower(feed_text):
                    logger.info('Auth OK - OK')
                    return 1
            except:
                pass
            return 0
        except Exception as e:
            for i in e.args:
                if 'unknown error: net::ERR_PROXY_CONNECTION_FAILED' in i:
                    return -2
            return 0

    def delete_account(self):
        if self.soc == 0:
            delete_acc(self.login, self.password, 'ok.txt')
        elif self.soc == 1:
            delete_acc(self.login, self.password, 'vk.txt')


    def click_vk_button(self, driver):
        driver.find_element_by_xpath('//*[@id="modal"]/div/div/div/div[1]/a[1]').click()
        time.sleep(8)
        try:
            driver.switch_to.window(driver.window_handles[1])
            driver.find_element_by_xpath(
                '/html/body/div[2]/div[2]/div[2]/div/div[3]/div/div/div[2]/form/div/input').click()
            time.sleep(3)
            if len(driver.window_handles) > 1:
                driver.refresh()
                time.sleep(5)
                driver.switch_to.window(driver.window_handles[0])
        except:
            pass

    def click_ok_button(self, driver):
        driver.find_element_by_xpath('/html/body/div[3]/div/div/div/div[1]/a[2]/div').click()
        time.sleep(2)
        driver.switch_to.window(driver.window_handles[1])
        driver.find_element_by_xpath('/html/body/div/form/div/div[3]/button').click()
        time.sleep(4)
        if len(driver.window_handles) > 1:
            driver.refresh()
            time.sleep(8)
        try:
            driver.switch_to.window(driver.window_handles[0])
        except AttributeError:
            pass

    def compare_with_lst(self):
        for index, item in enumerate(good_acc):
            if self.login == item.login and self.password == item.password:
                return index
        return False

    def del_from_list(self):
        index = self.compare_with_lst()
        if index:
            del good_acc[index]

    @logger.catch()
    def test_auth_token(self):
        vk, ok = None, None
        lock = threading.Lock()
        driver, curr_proxy = get_driver(self.proxy)
        try:
            if self.soc == 1:
                vk = self.auth_vk(driver)
            elif self.soc == 0:
                ok = self.auth_ok(driver)
            if vk == 1 or ok == 1:
                driver.get('https://m.avito.ru/profile/settings#login?forceMode=true')
                bp = is_bad_proxy(driver)
                while bp == 1:
                    driver.get('https://m.avito.ru/profile/settings#login?forceMode=true')
                    bp = is_bad_proxy(driver)
                if bp == -1:
                    driver.quit()
                    logger.error(f'BAD PROXY - DELETING || {curr_proxy[0]}')
                    lock.acquire()
                    if curr_proxy in proxy_list:
                        proxy_list.remove(curr_proxy)
                        output_txt('bad_proxy.txt', curr_proxy[0])
                    lock.release()
                    self.test_auth_token()
                if ok:
                    try:
                        self.click_ok_button(driver)
                    except:
                        driver.quit()
                        logger.error(f'Auth OK - ERROR || {self.login}')
                        self.del_from_list()
                        if self.sess:
                            sessid.append(self.sess)
                        self.delete_account()
                        return
                elif vk:
                    try:
                        self.click_vk_button(driver)
                    except:
                        driver.quit()
                        logger.error(f'Auth VK - ERROR || {self.login}')
                        self.del_from_list()
                        if self.sess:
                            sessid.append(self.sess)
                        self.delete_account()
                        return
                try:
                    check_auth = driver.find_element_by_xpath('/html/body/div[3]/div/div/div/div[2]').text
                    if str(check_auth).lower() == 'войти через телефон или почту':
                        logger.error(
                            f'BAN IN AVITO || VK - {self.login}' if vk else f'BAN IN AVITO || OK - {self.login}')
                        self.delete_account()
                        driver.quit()
                        return
                    elif 'новый код' in str(check_auth).lower():
                        logger.error(
                            f'BAN IN AVITO || VK - {self.login}' if vk else f'BAN IN AVITO || OK - {self.login}')
                        self.delete_account()
                        driver.quit()
                        return 0
                except:
                    logger.success(f'Удачная авторизация в Авито || {self.login}')
                time.sleep(3)
                driver.refresh()
                time.sleep(2)
                if self.sess:
                    sess = self.auth_sess(driver)
                    if sess == 0:
                        return
                if not self.compare_with_lst():
                    good_acc.append(self)
                while ads_list:

                    lock.acquire()
                    if ads_list:
                        link, bad = ads_list.pop()
                    else:
                        return
                    while (ads_list and 'avito.ru' not in str(link)) or bad >= 5:
                        link, bad = ads_list.pop()
                    lock.release()

                    driver.get(link)
                    try:
                        text = driver.find_element_by_xpath('/html/body/div/div/h1').text
                        if 'доступ' in str.lower(text):
                            logger.error(f'Аккаунт ограничен | {self.login}')
                            driver.quit()
                            return
                    except:
                        pass
                    try:
                        button = driver.find_element_by_xpath(
                            '/html/body/div[1]/div/div[1]/div[4]/div/div/button/span').text
                        if str(button).lower() == 'подтвердить телефон':
                            logger.error(f'Потвердите телефон | {link}')
                            return
                    except:
                        pass
                    try:
                        bad_link = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[2]').text
                    except:
                        bad_link = None
                    if 'ой! такой страницы' in str(bad_link).lower():
                        logger.error('Плохая ссылка, берем следующую')
                        continue
                    try:
                        bad_link = driver.find_element_by_xpath('/html/body/div[2]/div[1]/div/h1').text
                    except:
                        bad_link = None
                    if 'ой! такой страницы' in str(bad_link).lower():
                        logger.error('Плохая ссылка, берем следующую')
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
                        logger.success(
                            f'ID_ITEM: {item_id} || NUMBER: {phone_number} || SESSID: {self.sess}'
                            if self.sess
                            else f'ID_ITEM: {item_id} || NUMBER: {phone_number} || LOGIN: {self.login}')
                        self.bad = 0
                        data.append(
                            [title, price, phone_number, link, wp, self.sess if self.sess else self.login])
                        output_txt('PARSED_LINKS.txt', link)
                    else:
                        logger.error(f'ID_ITEM: {item_id} || SESSID: {self.sess}'
                                     if self.sess
                                     else f'ID_ITEM: {item_id} || LOGIN: {self.login}')
                        ads_list.insert(0, (link, bad + 1))
                        self.bad += 1
                        if self.bad >= 10:
                            driver.quit()
                            logger.error(f'ID_ITEM: {item_id} || Наступил лимит на аккаунте, попробуйте загрузить его позже: {self.sess}'
                                         if self.sess
                                         else f'ID_ITEM: {item_id} || Наступил лимит на аккаунте, попробуйте загрузить его позже: {self.login}')
                            if self.sess:
                                output_txt('SESS_LIMIT.txt', self.sess)
                            elif self.soc == 0:
                                output_txt('OK_LIMIT.txt', f'{self.login}:{self.password}')
                            elif self.soc == 1:
                                output_txt('VK_LIMIT.txt', f'{self.login}:{self.password}')
                            return
                driver.quit()
            elif vk == 0:
                driver.quit()
                logger.error(f'Auth VK - ERROR || {self.login}')
                self.del_from_list()
                if self.sess:
                    sessid.append(self.sess)
                self.delete_account()
            elif ok == 0:
                driver.quit()
                logger.error(f'Auth OK - ERROR || {self.login}')
                self.del_from_list()
                if self.sess:
                    sessid.append(self.sess)
                self.delete_account()

            elif vk == -1:
                driver.quit()
                logger.error(f'Auth VK - CAPTCHA || {self.login}')

            elif ok == -1:
                driver.quit()
                logger.error(f'Auth OK - CAPTCHA || {self.login}')
                if curr_proxy and curr_proxy[1] >= 3:
                    logger.error(f'BAD PROXY - DELETING || {curr_proxy[0]}')
                    lock.acquire()
                    if curr_proxy in proxy_list:
                        proxy_list.remove(curr_proxy)
                    lock.release()
                    output_txt('bad_proxy.txt', curr_proxy[0])
            elif vk == -2:
                driver.quit()
                logger.error(f'BAD PROXY - DELETING || {curr_proxy[0]}')
                lock.acquire()
                if curr_proxy in proxy_list:
                    proxy_list.remove(curr_proxy)
                    output_txt('bad_proxy.txt', curr_proxy[0])
                lock.release()
                self.test_auth_token()
            elif ok == -2:
                driver.quit()
                logger.error(f'BAD PROXY - DELETING || {curr_proxy[0]}')
                lock.acquire()
                if curr_proxy in proxy_list:
                    proxy_list.remove(curr_proxy)
                    output_txt('bad_proxy.txt', curr_proxy[0])
                lock.release()
                self.test_auth_token()
        except Exception as e:
            driver.quit()
            print(e)

    def auth_sess(self, driver):
        cookie = driver.get_cookie('sessid')
        cookie.update(value=self.sess)
        driver.add_cookie(cookie)
        driver.refresh()
        time.sleep(3)
        try:
            new_profile = driver.find_element_by_xpath(
                '//*[@id="app"]/div/div[2]/div[1]/div/div/div[1]/div[1]/div[1]/div/div[3]').text
        except:
            logger.error(f'Не работающие sessid || {self.sess} || Удаляю')
            driver.quit()
            return 0
        logger.success(f'Удачная авторизация через sessid || {self.sess}')
        return 1


def start(autorization):
    autorization.test_auth_token()


def end():
    output_txt('UNPARSED_LINKS.txt', ads_list)
    logger.info(f'Создан файл UNPARSED_LINKS.txt с {len(ads_list)} необработанными ссылками.')
    ads_list.clear()
    return


if __name__ == '__main__':
    try:
        create_txt('bad_proxy.txt')
        logged, logged_admin = auth_start()
        while True:
            if not logged:
                print('Вы не авторизовались. Попробуйте ещё раз.')
                logged, logged_admin = auth_start()
            else:
                text = "Для старта парсера напишите: 1\n" \
                       "Для выдачи доступа напишите: 2\n" \
                       "Для выхода из программы напишите: 3\n" \
                    if logged_admin \
                    else "Для старта парсера напишите: 1\n" \
                         "Для выхода из программы напишите: 3\n"
                action = input(text)
                if action == '3':
                    raise Exception('Close')
                elif action == '1':
                    global link_path
                    link_path = input('Введите названия txt файла с ссылками (пример: links.txt):\n')
                    while True:
                        try:
                            link_file = read_txt(link_path)
                            break
                        except Exception as e:
                            link_path = input('Файл не был найден. Введите названия excel (пример: log.txt):\n')
                    global api_key
                    api_key = input('Введите ключ от anti-captcha.com\n')
                    while check_balance(api_key):
                        api_key = input('Вы ввели неверный ключ.\nВведите ключ от anti-captcha.com\n')
                    thread_count = int(input('Сколько потоков: '))
                    threads_was_opened = len(threading.enumerate())
                    or_not = True if len(proxy_list) > 0 else False
                    while ads_list:
                        rng = (thread_count - len(threading.enumerate())) + threads_was_opened
                        _ = 0
                        while _ < rng:
                            soc = None
                            acc = None
                            sess = None
                            if len(ok):
                                acc = ok.pop()
                                soc = 0
                            elif len(vk):
                                acc = vk.pop()
                                soc = 1
                            elif len(sessid):
                                if len(good_acc):
                                    sess = sessid.pop()
                            else:
                                logger.info('Аккаунты закончились')
                                check_threads(threads_was_opened, thread_count, final=True)
                                end()
                                break
                            if not acc and not sess:
                                time.sleep(0.5)
                                continue
                            elif not sess:
                                autorization = AuthVK(*acc.split(':'), or_not, soc)
                            else:
                                autorization = copy.deepcopy(good_acc[0])
                                autorization.sess = sess
                            if not ads_list:
                                break
                            logger.info(
                                f'Запущено потоков: {len(threading.enumerate()) - threads_was_opened}\nЗапускаю еще один поток.')
                            threading.Thread(target=start, args=([autorization])).start()
                            _ += 1
                        check_threads(threads_was_opened, thread_count)
                    check_threads(threads_was_opened, thread_count, final=True)
                    create_xlsx()
                    logger.success('Работа завершена.')
                elif action == '2' and logged_admin:
                    while True:
                        login = 'user'
                        password = id_generator()
                        with open('accounts', encoding='windows-1251') as file:
                            lines = file.read().splitlines()
                            crypted_acc = f"{hash_crypt(encode(f'{login}:{password}'))}"
                            if crypted_acc not in lines:
                                break
                    with open('accounts', 'a') as accs:
                        accs.write(f'\n{crypted_acc}')
                    print(f'Пользователь создан: {login} {password}\n\n')
                else:
                    print('Вы ввели неверную команду, попробуйте заново.\n')
    except Exception as e:
        if 'Close' in e.args:
            logger.info('Программа была закрыта.')
            time.sleep(5)
            exit()
        elif 'NoAccsException' in e.args:
            logger.error('Закончились аккаунты в базе. Завершаю выполнение программы.')
            time.sleep(5)
        elif 'bytes must be in range(0, 256)' in e.args:
            logger.info('Логин и пароль должны быть на английском языке')
