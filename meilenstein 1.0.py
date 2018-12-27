from pathlib import Path
import datetime
import atexit
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import sys, os
import Proxy
import Model
import logging


class Controller(object):
    def __init__(self):
        # self.proxy = Proxy.Proxy()
        # self.proxy = self.proxy.get_proxy()
        # self.chrome_options = webdriver.ChromeOptions()
        # self.chrome_options.add_argument('--proxy-server=%s' % self.proxy)
        # self.chrome_options.add_argument("headless")
        self.url = 'https://de.lovoo.com/login_check'
        # self.driver = webdriver.Chrome(chrome_options=self.chrome_options)
        # self.driver.implicitly_wait(5)
        # self.driver = webdriver.Chrome()
        # self.wait = WebDriverWait(self.driver, 10)
        self.like_counter = 0

    def write_to_log(self, message='', exception='', exc_info=''):
        info = exc_info
        # a Open an existing file for appending plain text
        log_file = open('log.log', 'a')
        log_file.write(
            '{0} {1} {2}\n Error of the line {3}'.format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), message,
                                                         exception, info, info[-1].tb_lineno))
        log_file.close()

    def exit_handler(self):
        print('My application is ending!')

    def get_like_button(self):
        try:
            self.button = self.driver.find_element(By.XPATH, '//*[@id="profile-details"]/div/div[3]/div/button')
            return self.button
        except Exception:
            return False

    def is_congratulations_message(self, driver):
        try:
            self.heart_icon = driver.find_element(By.XPATH, '/html/body/div[*]/div/div/div/div[1]/div/i')
            return self.heart_icon
        except Exception as error:
            self.write_to_log("Account " + str(id) + " is not active or not verficated", error, sys.exc_info())
            logging.exception("message")
            return False

    def add_to_black_list(self, user_id):
        try:
            model.black_list.append(user_id)
        except Exception as error:
            self.write_to_log("Failed to add id to black list", error, sys.exc_info())

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
                    except ValueError as error:
                        self.write_to_log('', error, sys.exc_info())
            return usr, password, max_likes
        except Exception as error:
            self.write_to_log("Exception", error, sys.exc_info())
            print("Failed to read account info")
            return

    def get_next_user(self, element, driver):
        try:
            self.next_user = driver.find_element(By.XPATH,
                                                 '//*[@id="page-content"]/list-page/infinite-list/div[1]/div[' + str(
                                                     element) + ']/div/a/div[1]')
            return self.next_user
        except Exception:
            logging.exception("message")
            return False

    def close_info_window(self, driver):
        time.sleep(3)
        webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        time.sleep(1)
        webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        time.sleep(3)

    def like(self, account_list):
        for account in account_list:
            user, password, max_likes = self.read_info_about_account(account)
            self.chrome_options = webdriver.ChromeOptions()
            # self.chrome_options.add_argument('--proxy-server=%s' % self.proxy)
            # self.chrome_options.add_argument("headless")
            self.url = 'https://de.lovoo.com/login_check'
            self.driver = webdriver.Chrome(chrome_options=self.chrome_options)
            self.driver.implicitly_wait(5)
            self.wait = WebDriverWait(self.driver, 10)
            try:
                self.driver.get(self.url)
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
                time.sleep(1)
                login_btn.click()
                # Your profile
                self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[contains(text(), "Dein Profil")]'))).click()
                # Like you site
                self.wait.until(EC.element_to_be_clickable((By.XPATH,
                                                            '/html/body/div[1]/ng-view/div/div[2]/div/div[1]/div/ng-include/nav[2]/a[2]'))).click()
                # Self icon
                self.wait.until(EC.presence_of_element_located((By.XPATH, '//a[contains(@border,"2")]')))
                print('Mögen dich Seite')
            except Exception:
                logging.exception("message")
                self.driver.quit()
                continue

            self.el = 1
            while max_likes != self.like_counter:
                self.next_user = self.get_next_user(self.el, self.driver)

                if not self.next_user:
                    print('No more users')
                    break

                # Like button not active//*[@id="profile-details"]/div/div[3]/div/div
                # Like button active    //*[@id="profile-details"]/div/div[3]/div/button
                parent_el = self.next_user.find_element(By.XPATH, '..')
                href = parent_el.get_attribute('href')
                self.user_id = href.split('/')[4]

                if self.is_id_in_black_list(self.user_id):
                    print('Is in black list')
                    # self.close_info_window(self.driver)
                    self.el += 1
                    continue

                self.next_user.click()
                self.like_btn = self.get_like_button()

                if self.like_btn:
                    # Set like
                    self.like_btn.click()
                    if self.is_congratulations_message(self.driver):
                        self.add_to_black_list(self.user_id)
                        self.like_counter += 1
                        print(str(self.like_counter) + ' likes pro ' + str(user) + ' max Anzahl ' + str(max_likes))
                    else:
                        print('Account not active, go to next')
                        # self.driver.quit()
                        break
                else:
                    self.add_to_black_list(self.user_id)
                    print(href + ' was liked')

                self.close_info_window(self.driver)
                self.el += 1

            self.driver.quit()

    def read_accoutn_list(self, path_to_file):
        path = Path(path_to_file)
        if path.is_file():
            try:
                file = open(path, 'r+')
                model.accoutn_list = [line.rstrip('\n') for line in file.readlines()]
            except Exception as error:
                self.write_to_log('Failed to read', error)
                print('Failed to read ' + str(path))
            finally:
                file.close()
        else:
            sys.exit('File not exist ' + path_to_file)

    def read_black_list(self, path_to_file):
        path = Path(path_to_file)
        try:
            file = open(path, 'r+')
            model.black_list = [line.rstrip('\n') for line in file.readlines()]
        except IOError as error:
            open(path, 'w')
            self.write_to_log('No black_list file. File was created.', error, sys.exc_info())
        finally:
            file.close()

    def is_id_in_black_list(self, user_id):
        # It will return True, if element exists in list else return false.
        return user_id in model.black_list

    def save_black_list_to_file(self, path, black_list):
        with open(path, 'w') as file:
            for user_id in black_list:
                file.write("%s\n" % user_id)


# ### RUN ### #

try:
    ctrl = Controller()
    model = Model.Model()
    accoutn_list_path = 'Test_user.txt'
    black_list_path = 'black_list.txt'

    ctrl.read_accoutn_list(accoutn_list_path)
    ctrl.read_black_list(black_list_path)
    ctrl.like(model.accoutn_list)
except Exception as error:
    logging.exception("message")
    ctrl.write_to_log("", error, sys.exc_info())
finally:
    ctrl.save_black_list_to_file(black_list_path, model.black_list)
    ctrl.driver.quit()
    print('Save black list')
