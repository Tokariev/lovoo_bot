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
    info = exc_info
    # a Open an existing file for appending plain text
    log_file = open('log.log', 'a')
    log_file.write('{0} {1} {2}\n'.format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), message,
                                          exception, info))
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
    max_likes = None
    try:
        arr = account.split('|')
        if len(arr) >= 2:
            usr = arr[0]
            password = arr[1]
            if len(arr) == 3:
                try:
                    max_likes = int(arr[2])
                except ValueError as error:
                    write_to_log('', error, sys.exc_info())
    except Exception as error:
        write_to_log("Exception", error, sys.exc_info())
        return

    try:
        browser = webdriver.Chrome()
        browser.implicitly_wait(5)  # seconds
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
        browser.find_element(By.XPATH, '//*[contains(text(), "Dein Profil")]').click()

        # Mögen dich
        browser.find_element(By.XPATH,
                             '/html/body/div[1]/ng-view/div/div[2]/div/div[1]/div/ng-include/nav[2]/a[2]').click()

        # Self icon
        browser.find_element(By.XPATH, '//a[contains(@border,"2")]')

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

                try:
                    # find like button
                    like = browser.find_element(By.XPATH, '//*[@id="profile-details"]/div/div[3]/div/button')
                    like.click()
                except:
                    # Next iteration wile liked
                    webdriver.ActionChains(browser).send_keys(Keys.ESCAPE).perform()
                    write_to_log('Account ' + str(user.get_attribute('title')) + ' was already liked.', exc_info=sys.
                                 exc_info())
                    time.sleep(1)
                    continue

                try:
                    # Try to catch congratulations message popup
                    browser.find_element(By.XPATH, '/html/body/div[*]/div/div/div/div[1]/div/i')
                    time.sleep(2)
                    add_to_black_list(id)
                    if max_likes is not None:
                        max_likes -= 1
                        if max_likes == 0:
                            break
                except Exception as error:
                    write_to_log("Account " + id + " is not active or not verficated", error, sys.exc_info())
                    break
                finally:
                    webdriver.ActionChains(browser).send_keys(Keys.ESCAPE).perform()
                    time.sleep(1)
                    webdriver.ActionChains(browser).send_keys(Keys.ESCAPE).perform()
                    time.sleep(1)
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

