from pathlib import Path
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import sys
import Model
import logging
from logging_utils import setup_logging_to_file
import linecache
import atexit
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials


class Controller(object):
    def __init__(self):
        # self.proxy = Proxy.Proxy()
        # self.proxy = self.proxy.get_proxy()
        # self.chrome_options = webdriver.ChromeOptions()
        # self.chrome_options.add_argument('--proxy-server=%s' % self.proxy)
        # self.chrome_options.add_argument("headless")
        self.url = 'https://de.lovoo.com/login_check'
        # self.driver = webdriver.Chrome(chrome_options=self.chrome_options)

    def write_to_log(self):
        exc_type, exc_obj, tb = sys.exc_info()
        f = tb.tb_frame
        lineno = tb.tb_lineno
        filename = f.f_code.co_filename
        linecache.checkcache(filename)
        line = linecache.getline(filename, lineno, f.f_globals)
        log_file = open('log.log', 'a')
        log_file.write('{} EXCEPTION IN ({}, LINE {} "{}"): {}'
                       .format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                               filename, lineno, line.strip(), exc_obj))
        log_file.close()

    def get_like_button(self):
        try:
            # //*[@id="profile-details"]/div/div[3]/button
            # //*[@id="profile-details"]/div/div[2]/online-status

            self.login_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="profile-details"]/div/div[2]/online-status')))

            self.button = self.driver.find_element(By.XPATH, '//*[@id="profile-details"]/div/div[3]/div/button')
            return self.button
        except Exception:
            return False

    def is_congratulations_message(self, driver):
        try:
            self.heart_icon = driver.find_element(By.XPATH, '/html/body/div[*]/div/div/div/div[1]/div/i')
            return self.heart_icon
        except:
            print()
            return False

    def add_to_black_list(self, user_id):
        try:
            model.black_list.append(user_id)
        except Exception as error:
            self.write_to_log()

    def read_info_about_account(self, account):
        usr = ''
        password = ''
        # As default
        max_likes = -1
        try:
            arr = account.split('|')
            if len(arr) >= 2:
                usr = arr[0]
                password = arr[1]
                if len(arr) == 3:
                    try:
                        max_likes = int(arr[2])
                    except ValueError as e:
                        self.write_to_log()
            return usr, password, max_likes
        except Exception as e:
            self.write_to_log()
            print("Failed to read account info")
            return

    def scroll_down(self, driver):
        SCROLL_PAUSE_TIME = 0.5
        # Get scroll height
        last_height = driver.execute_script("return document.body.scrollHeight")
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Wait to load page
        sleep(SCROLL_PAUSE_TIME)

    def get_next_user(self, element, driver):
        # If last element on the page
        if element % 25 == 0:
            self.scroll_down(driver)
            print(element)
        try:
            self.next_user = self.wait.until(
                EC.presence_of_element_located((By.XPATH,
                                                 '//*[@id="page-content"]/list-page/infinite-list/div[1]/div[' + str(
                                                     element) + ']/div/a/div[1]')))
            return self.next_user
        except Exception as e:
            print('Next user was not found')
            self.write_to_log()
            return False

    def close_info_window(self, driver):
        sleep(2)
        webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        sleep(2)
        webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        sleep(2)

    def is_captcha(self, driver):
        try:
            driver.refresh()
            captcha = self.wait.until(
                EC.presence_of_element_located((By.XPATH,
                                                '//*[@id="challenge-form"]/script')))
            data_sitekey = captcha.get_attribute('data-sitekey')
            print('Captcha was found')
            return data_sitekey
        except:
            return False

    def login(self, driver, user, password):
        try:
            driver.get(self.url)
            self.login_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[contains(text(), "Einloggen")]')))
            self.login_btn.click()
            # self.driver.find_element(By.XPATH, '//*[contains(text(), "Einloggen")]').click()
            self.email_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, '//input[@name="authEmail"]')))
            self.email_input.send_keys(user)
            self.password_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, '//input[@name="authPassword"]')))
            self.password_input.send_keys(password)
            login_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH,
                                                                    '//*[@id="form"]/div[2]/div[2]/button')))
            sleep(1)

            login_btn.click()
            # Your profile
            self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[contains(text(), "Dein Profil")]'))).click()
            # Like you site
            self.wait.until(EC.element_to_be_clickable((By.XPATH,
                                                        '/html/body/div[1]/ng-view/div/div[2]/div/div[1]/div/ng-include/nav[2]/a[2]'))).click()
            # Self icon
            self.wait.until(EC.presence_of_element_located((By.XPATH, '//a[contains(@border,"2")]')))
            print('Mögen dich Seite')
            return True
        except Exception as e:
            self.write_to_log()
            print("Except login")
            return False

    def like(self, account_list):
        for account in account_list:
            user, password, max_likes = self.read_info_about_account(account)
            self.chrome_options = webdriver.ChromeOptions()
            # self.chrome_options.add_argument('--proxy-server=%s' % self.proxy)
            # self.chrome_options.add_argument("headless")
            self.url = 'https://de.lovoo.com/login_check'
            self.driver = webdriver.Chrome(options=self.chrome_options)
            self.driver.implicitly_wait(15)
            self.wait = WebDriverWait(self.driver, 30)

            if self.login(self.driver, user, password):
                pass
            else:
                # Try to solve captcha
                data_sitekey = self.is_captcha(self.driver)
                if data_sitekey:
                    self.solve_captcha(data_sitekey, self.driver)
                    sleep(5)
                    self.driver.refresh()
                    sleep(5)
                    self.login(self.driver, user, password)
                else:
                    self.driver.quit()
                    continue

            self.user_number = 1
            self.like_counter = 0

            while max_likes != self.like_counter:
                self.next_user = self.get_next_user(self.user_number, self.driver)

                if not self.next_user:
                    print('No more users')
                    break

                parent_el = self.next_user.find_element(By.XPATH, '..')
                href = parent_el.get_attribute('href')
                title = self.next_user.get_attribute('title')
                img_background_url = self.next_user.get_attribute('style').split(';')[4]
                self.user_id = href.split('/')[4]

                if 'default_user' in img_background_url:
                    self.add_to_black_list(self.user_id)
                    self.user_number += 1
                    print('User without photo.')
                    continue

                if self.is_id_in_black_list(self.user_id):
                    print(title + ' is in black list')
                    # self.close_info_window(self.driver)
                    self.user_number += 1
                    sleep(0.5)
                    continue

                try:
                    self.next_user.click()
                except:
                    # Try to solve captcha
                    print("Except next user click")
                    data_sitekey = self.is_captcha(self.driver)
                    if data_sitekey:
                        self.solve_captcha(data_sitekey, self.driver)
                        sleep(5)
                        self.driver.refresh()
                        sleep(5)
                    else:
                        self.close_info_window(self.driver)
                        self.user_number += 1
                        continue

                self.like_btn = self.get_like_button()

                if self.like_btn:
                    # Set like
                    try:
                        self.like_btn.click()
                    except:
                        # Try to solve captcha
                        data_sitekey = self.is_captcha(self.driver)
                        if data_sitekey:
                            self.solve_captcha(data_sitekey, self.driver)
                            sleep(5)
                            self.driver.refresh()
                            sleep(5)
                        else:
                            self.close_info_window(self.driver)
                            self.user_number += 1
                            continue

                    if self.is_congratulations_message(self.driver):
                        self.add_to_black_list(self.user_id)
                        self.like_counter += 1
                        print(str(self.like_counter) + ' likes pro ' + str(user) + ' max Anzahl ' + str(max_likes))
                    else:
                        print(user + ' account not active, go to next')
                        # self.driver.quit()
                        break
                else:
                    self.add_to_black_list(self.user_id)
                    print(title + ' was liked')

                self.close_info_window(self.driver)
                self.user_number += 1

            self.driver.quit()

    def read_accoutn_list(self, path_to_accounts):

        path = Path(path_to_accounts)
        if path.is_file():
            try:
                file = open(path, 'r+')
                model.accoutn_list = [line.rstrip('\n') for line in file.readlines()]
                if not model.accoutn_list:
                    print('\nAccount list is empty')
                    input('Press Enter to exit...')
            except Exception as e:
                self.write_to_log()
                input('Failed to read ' + str(path))
            finally:
                file.close()
        else:
            print('File ' + str(path) + ' not exist.')
            input('"Press Enter to exit..."')
            sys.exit()

    def read_black_list(self, path_to_file):
        path = Path(path_to_file)
        if path.is_file():
            try:
                file = open(path, 'r+')
                model.black_list = [line.rstrip('\n') for line in file.readlines()]
            except IOError as e:
                open(path, 'w')
                print('Failed to read ' + str(path))
                self.write_to_log()
            finally:
                file.close()
        else:
            file = open(path, 'w+')
            file.close()

    def is_id_in_black_list(self, user_id):
        # It will return True, if element exists in list else return false.
        return user_id in model.black_list

    def save_black_list_to_file(self, path, black_list):
        with open(path, 'w') as file:
            for user_id in black_list:
                file.write("%s\n" % user_id)
        print('Save black list.\n')

    def solve_captcha(self, data_sitekey, driver):
        # Add these values
        API_KEY = '4bfbf3a52ca3d8fdf437db6b49e03eeb'  # Your 2captcha API KEY
        site_key = data_sitekey
        url = driver.current_url

        s = requests.Session()
        ### Get cookie from Selenium
        cookies = driver.get_cookie()
        for cookie in cookies:
            s.cookies.set(cookie['name'], cookie['value'])

        captcha_id = s.post(
            "http://2captcha.com/in.php?key={}&method=userrecaptcha&googlekey={}&pageurl={}".format(API_KEY, site_key,
                                                                                                    url))
        recaptcha_answer = s.get("http://2captcha.com/res.php?key={}&action=get&id={}".format(API_KEY, captcha_id)).text
        print("solving ref captcha...")
        while 'CAPCHA_NOT_READY' in recaptcha_answer:
            sleep(5)
            recaptcha_answer = s.get(
                "http://2captcha.com/res.php?key={}&action=get&id={}".format(API_KEY, captcha_id)).text
        recaptcha_answer = recaptcha_answer.split('|')[1]
        payload = {
            'key': 'value',
            'gresponse': recaptcha_answer
        }
        response = s.post(url, payload)
        print("Captcha was solved")

    def read_remote_secret(self):
        # use creds to create a client to interact with the Google Drive API
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
        client = gspread.authorize(creds)
        # Find a workbook by name and open the first sheet
        # Make sure you use the right name here.
        sheet = client.open("keep_secret").sheet1
        # Extract and print all of the values
        list_of_hashes = sheet.get_all_values()

        if not list_of_hashes:
            print("Password was not found")
            input("Press Enter to exit...")
            sys.exit()
        else:
            for el in list_of_hashes:
                if el[0] == 'Lovoo':
                    secret = (el[1])
        return secret

    def check_password(self, secret):
        password = input("Enter password: ")
        try_count = 0
        while secret != password:
            print("Wrong password. Try again.\n\n")
            password = input("Enter password: ")
            try_count += 1
            if try_count == 5:
                sys.exit()



# ### RUN ### #

try:
    ctrl = Controller()
    secret = ctrl.read_remote_secret()
    ctrl.check_password(secret)

    model = Model.Model()
    accoutn_list_path = 'accounts.txt'
    black_list_path = 'black_list.txt'
    ctrl.read_accoutn_list(accoutn_list_path)
    ctrl.read_black_list(black_list_path)
    ctrl.like(model.accoutn_list)
except Exception as e:
    ctrl.write_to_log()
finally:
    ctrl.save_black_list_to_file(black_list_path, model.black_list)
    ctrl.driver.quit()
    input("Press Enter to continue...")

atexit.register(ctrl.save_black_list_to_file(black_list_path, model.black_list))
