from pathlib import Path
import datetime
import sys
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time
from selenium.webdriver.support import expected_conditions as EC


def write_to_log(message='', exception=''):
    # a Open an existing file for appending plain text
    log_file = open('log.log', 'a')
    log_file.write('{0} {1} {2}\n'.format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), message,
                                          exception))
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


def like_it(account):
    usr = ''
    password = ''
    likes = 0
    try:
        arr = account.split('|')
        if len(arr) >= 2:
            usr = arr[0]
            password = arr[1]
            if len(arr) == 2:
                likes = arr[2]
    except Exception as error:
        write_to_log("Exception", error)
        return

    try:
        browser = webdriver.Chrome()
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
        write_to_log("Exception", error)
        browser.quit()
        return

    try:
        # Dein profil
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
        write_to_log("TimeoutException", error)
        browser.quit()
        return
    except NoSuchElementException as error:
        write_to_log("NoSuchElementException", error)
        browser.quit()
        return

    try:
        for user in all_user:
            parent_el = user.find_element(By.XPATH, '..')
            href = parent_el.get_attribute('href')
            id = href.split('/')[4]
            user.click()

    except Exception as error:
        write_to_log("All users elements exception", error)
        browser.quit()
        return


    finally:
        browser.quit()


# ##### START ##### #

accounts_list = read_users_info_to_list('Test Acounts.txt')
if not is_list_empty(accounts_list):
    for account in accounts_list:
        like_it(account)
