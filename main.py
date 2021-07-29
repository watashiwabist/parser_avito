import json
import re
import os
import sys
import threading
import time


from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from misc import ads_list, data

key = 'af0deccbgcgidddjgnvljitntccdduijhdinfgjgfjir'

with open('vk.txt', 'r') as vk:
    vk = vk.read().split('\n')

with open('ok.txt', 'r') as ok:
    ok = ok.read().split('\n')

login_in_via_link = 'https://m.avito.ru/profile/settings#login?forceMode=true'
title_xpath = '/html/body/div[1]/div/div[2]/div/div[2]/div/div[1]/div/div[1]/div/h1/span'
price_xpath = '/html/body/div[1]/div/div[2]/div/div[2]/div/div[1]/div/div[2]/p/span/span'
number_xpath = '/html/body/pre'
api_link = 'https://m.avito.ru/api/1/items/'


def is_bad_social(browser, xpath):
    try:
        browser.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    return True


def is_bad_proxy(browser):
    try:
        try:
            WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div/h2')))
        except TimeoutException:
            return False
        bad_ip_text = browser.find_element_by_xpath('/html/body/div[2]/div/h2').text
        if bad_ip_text == 'Доступ с Вашего IP временно ограничен':
            return True
    except NoSuchElementException:
        return False
    return True


def get_numb(number_element):
    link = json.loads(number_element.replace('"', '"'))
    print(link)
    try:
        if link['status'] == 'ok':
            if link['result']['action']['uri'] == 'ru.avito://1/authenticate':
                return False
            return re.split('[A-z]', link['result']['action']['uri'])[-1]
        else:
            return False
    except:
        return False


def get_info_ads(browser, link_ads, link_id):
    browser.get(f'{api_link}{link_id}/phone?key={key}')
    number_element = browser.find_element_by_xpath(number_xpath).text
    number = get_numb(number_element)
    browser.get(link_ads)
    title = browser.find_element_by_xpath(title_xpath).text
    price = browser.find_element_by_xpath(price_xpath).text
    return title, price, number


def auth_vk(acc, proxy):
    driver = os.getcwd() + '/chromedriver'
    options = webdriver.ChromeOptions()
    # options.add_argument('headless')
    options.add_argument(
        "--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) "
        "CriOS/56.0.2924.75 Mobile/14E5239e Safari/602.1")
    options.add_argument("--incognito")
    if proxy:
        options.add_argument(f'--proxy-server=https://{proxy}')
    browser = webdriver.Chrome(driver, options=options)
    try:
        browser.get('http://m.vk.com')
        login_input = browser.find_element_by_xpath(
            '/html/body/div[2]/div[2]/div[2]/div/div[3]/div[1]/div[2]/div/div/form/dl[1]/dd/label/div/input')
        login_input.send_keys(acc[0])
        password_input = browser.find_element_by_xpath(
            '/html/body/div[2]/div[2]/div[2]/div/div[3]/div[1]/div[2]/div/div/form/dl[2]/dd/label/div/div[1]/input')
        password_input.send_keys(acc[1])
        browser.find_element_by_xpath(
            '/html/body/div[2]/div[2]/div[2]/div/div[3]/div[1]/div[2]/div/div/form/div[1]/input').click()
        time.sleep(2)
        if is_bad_social(browser, '/html/body/div[2]/div[2]/div[2]/div/div[3]/div[1]/div[2]/div/div/div[2]/div/div'):
            with open('vk.txt', 'w') as del_vk:
                del_vk.read().replace(f'{acc[0]}:{acc[1]}', '')
        else:
            browser.get(login_in_via_link)
            time.sleep(2)
            while is_bad_proxy(browser):
                browser.get(login_in_via_link)
            browser.find_element_by_xpath('/html/body/div[3]/div/div/div/div[1]/a[1]/div').click()
            time.sleep(6)
            lock = threading.Lock()
            # if len(browser.window_handles) > 1:
            #     try:
            #         browser.switch_to.windows(browser.window_handles[1])
            #         browser.close()
            #     except AttributeError:
            #         pass

            while len(ads_list) > 0:
                lock.acquire()
                link_ads = ads_list.pop()
                print(link_ads)
                lock.release()
                try:
                    link_id = link_ads.split('_')[-1]
                    title, price, number = get_info_ads(browser, link_ads, link_id)
                    if not number:
                        browser.quit()
                        return
                    data.append([title, price, number, link_ads, f'https://api.whatsapp.com/send?phone={number}', acc[0]])
                    print(f'{title} - {price} - {number}')
                except Exception as e:
                    print(e)
                    ads_list.append(link_ads)
                    break
    except Exception as e:
        print(e)
    finally:
        browser.quit()


# def auth_ok(acc, proxy):
#     driver = os.getcwd()+'/chromedriver'
#     options = webdriver.ChromeOptions()
#     # options.add_argument('headless')
#     options.add_argument(
#         "--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) "
#         "CriOS/56.0.2924.75 Mobile/14E5239e Safari/602.1")
#     options.add_argument("--incognito")
#     if proxy:
#         options.add_argument(f'--proxy-server=https://{proxy}')
#     browser = webdriver.Chrome(driver, options=options)
#     try:
#         browser.get('https://m.ok.ru/cdk/st.cmd/main/tkn/890?_prevCmd=mainLanding')
#         login_input = browser.find_element_by_xpath(
#             '/html/body/div[1]/div[2]/div/div[1]/form/div/div[1]/div/div/input')
#         login_input.send_keys(acc[0])
#         password_input = browser.find_element_by_xpath(
#             '/html/body/div[1]/div[2]/div/div[1]/form/div/div[2]/div/div/input')
#         password_input.send_keys(acc[1])
#         browser.find_element_by_xpath(
#             '/html/body/div[1]/div[2]/div/div[1]/form/div/div[3]/div/input').click()
#         time.sleep(4)
#         if is_bad_social(browser, '/html/body/div[1]/div[2]/div/div[1]/form/div/div[1]'):
#             with open('ok.txt', 'w') as del_vk:
#                 del_vk.read().replace(f'{acc[0]}:{acc[1]}', '')
#         else:
#             browser.get(login_in_via_link)
#             time.sleep(3)
#             while is_bad_proxy(browser):
#                 browser.get(login_in_via_link)
#             time.sleep(2)
#             browser.find_element_by_xpath('/html/body/div[3]/div/div/div/div[1]/a[2]/div').click()
#             windows_handles = browser.window_handles
#             browser.switch_to.window(windows_handles[1])
#             time.sleep(5)
#             browser.find_element_by_xpath('/html/body/div/form/div/div[3]/button').click()
#             browser.switch_to.window(windows_handles[0])
#             lock = threading.Lock()
#             if len(browser.window_handles) > 1:
#                 try:
#                     browser.switch_to.windows(browser.window_handles[1])
#                     browser.close()
#                 except AttributeError:
#                     pass
#             while len(ads_list) > 0:
#                 lock.acquire()
#                 link_ads = ads_list.pop()
#                 lock.release()
#                 try:
#                     link_id = link_ads.split('_')[-1]
#                     title, price, number = get_info_ads(browser, link_ads, link_id)
#                     if not number:
#                         browser.quit()
#                         sys.exit()
#                     data.append([title, price, number, link_ads, f'https://api.whatsapp.com/send?phone={number}'])
#                     print(f'{title} - {price} - {number}')
#                 except:
#                     ads_list.append(link_ads)
#                     break
#     except Exception as e:
#         print(e)
#     finally:
#         browser.quit()



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
