from pathlib import Path
import datetime
import sys
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import sys, os


def write_to_log(message='', exception='', exc_info=''):
    exc_type, exc_obj, exc_tb = exc_info
    # a Open an existing file for appending plain text
    log_file = open('log.log', 'a')
    log_file.write('{0} {1} {2} {3}, line {4}\n'.format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), message,
                                                  exception, exc_type, exc_tb.tb_lineno))
    log_file.close()


def read_users_info_to_list(path_to_file):
    path = Path(path_to_file)
    if path.is_file():
        try:
            file = open(path, 'r+')
            lines = [line.rstrip('\n') for line in file.readlines()]
            return lines
        except Exception as error:
            write_to_log('Failed to read', error)
        finally:
            file.close()
    else:
        sys.exit('File not exist ' + path_to_file)


def is_list_empty(l):
    if not l:
        print("List is empty")
        write_to_log('Try to read empty list')
        return True
    else:
        return False


def is_id_in_blacklist(id):
    path = Path('black_list.txt')
    try:
        open(path, 'r')
        if id in open('black_list.txt', 'r').read():
            return True
        else:
            return False
    except IOError as error:
        open(path, 'w')
        write_to_log('No black_list file. File was created.', error, sys.exc_info())


def add_to_black_list(id):
    path = Path('black_list.txt')
    black_list = open(path, 'a')
    black_list.write(id + '\n')
    black_list.close()


def like_it(account):
    usr = ''
    password = ''
    likes = 0
    try:
        arr = account.split('|')
        if len(arr) >= 2:
            usr = arr[0]
            password = arr[1]
            if len(arr) == 3:
                likes = arr[2]
    except Exception as error:
        write_to_log("Exception", error, sys.exc_info())
        return

    try:
        browser = webdriver.Chrome()
        browser.implicitly_wait(10)  # seconds
        browser.set_window_position(900, 0)
        browser.get("https://de.lovoo.com/")
        login_btn = browser.find_element(By.XPATH, '//*[contains(text(), "Einloggen")]')
        login_btn.click()
        email_input = browser.find_element(By.XPATH, '//input[@name="authEmail"]')
        email_input.send_keys(usr)
        password_input = browser.find_element(By.XPATH, '//input[@name="authPassword"]')
        password_input.send_keys(password)
        time.sleep(1)
        login_btn = browser.find_element(By.XPATH, '//*[@id="form"]/div[2]/div[2]/button')
        login_btn.click()
    except Exception as error:
        write_to_log("Exception", error, sys.exc_info())
        browser.quit()
        return

    try:
        # Dein profil
        browser.find_element(By.XPATH, '//*[contains(text(), "Dein Profil")]')
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[contains(text(), "Dein Profil")]'))
        ).click()

        # Mögen dich
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '/html/body/div[1]/ng-view/div/div[2]/div/div[1]/div/ng-include/nav[2]/a[2]'))
        ).click()

        # Self icon
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//a[contains(@border,"2")]'))
        )
        all_user = browser.find_elements(By.XPATH, '//div[contains(@class, "user-image user-userpic")]')
        # all_user = browser.find_elements(By.XPATH, '// a[contains( @ href, "/profile/")]')
    except TimeoutException as error:
        write_to_log("TimeoutException", error, sys.exc_info())
        browser.quit()
        return
    except NoSuchElementException as error:
        write_to_log("NoSuchElementException", error, sys.exc_info())
        browser.quit()
        return

    try:
        for user in all_user:
            parent_el = user.find_element(By.XPATH, '..')
            href = parent_el.get_attribute('href')
            id = href.split('/')[4]
            if not is_id_in_blacklist(id):
                # Open_account_detail_window
                user.click()
                time.sleep(2)
                # Click on like button
                WebDriverWait(browser, 1).until(
                    EC.presence_of_element_located((By.XPATH,
                                                    '//*[@id="profile-details"]/div/div[3]/div/button'))
                ).click()
                try:
                    # Try to catch congratulations message popup
                    WebDriverWait(browser, 1).until(
                        EC.presence_of_element_located((By.XPATH, '/html/body/div[*]/div/div/div/div[1]/div/i')))
                    time.sleep(2)
                    add_to_black_list(id)
                except TimeoutException as error:
                    # Try to catch not active message popup /html/body[contains(@class, 'alert-error')]
                    WebDriverWait(browser, 1).until(
                        EC.presence_of_element_located((By.XPATH, '/html/body[contains(@class, "alert-error")]')))
                    time.sleep(2)
                    write_to_log("Account " + id + " is not activ", error, sys.exc_info())
                    pass
                finally:
                    webdriver.ActionChains(browser).send_keys(Keys.ESCAPE).perform()
                    time.sleep(2)
                    webdriver.ActionChains(browser).send_keys(Keys.ESCAPE).perform()
                    time.sleep(2)
    except Exception as error:
        write_to_log("Try to make like", error, sys.exc_info())

    except Exception as error:
        write_to_log("All users elements exception", error, sys.exc_info())
        browser.quit()
        return


    finally:
        browser.quit()


# ##### START ##### #

accounts_list = read_users_info_to_list('Test Acounts.txt')
if not is_list_empty(accounts_list):
    for account in accounts_list:
        like_it(account)
