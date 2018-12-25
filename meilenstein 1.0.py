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
import Proxy


class SeleniumTest(object):
    def __init__(self):
        # self.proxy = Proxy.Proxy()
        # self.proxy = self.proxy.get_proxy()

        self.chrome_options = webdriver.ChromeOptions()
        # self.chrome_options.add_argument('--proxy-server=%s' % self.proxy)

        self.chrome_options.add_argument("headless")
        self.url = 'https://de.lovoo.com/login_check'
        self.driver = webdriver.Chrome(chrome_options=self.chrome_options)
        # self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 10)

    def get_like_button(self):
        try:
            self.button = self.driver.find_element(By.XPATH, '//*[@id="profile-details"]/div/div[3]/div/button')
            return self.button
        except Exception:
            return False

    def login(self, user, password):
        self.driver.get(self.url)

        try:
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

            login_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="form"]/div[2]/div[2]/button')))
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
            self.driver.quit()

        self.el = 1
        while True:
            self.user = self.wait.until(EC.presence_of_element_located(
                (By.XPATH,
                 '//*[@id="page-content"]/list-page/infinite-list/div[1]/div[' + str(self.el) + ']/div/a/div[1]')))

            self.user.click()
            # Like button not active//*[@id="profile-details"]/div/div[3]/div/div
            # Like button active    //*[@id="profile-details"]/div/div[3]/div/button

            parent_el = self.user.find_element(By.XPATH, '..')
            href = parent_el.get_attribute('href')

            self.like_btn = self.get_like_button()

            if self.like_btn:
                print(href + ' OK')
            else:
                print(href + ' NOT OK')

            time.sleep(3)
            webdriver.ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
            self.el += 1
            time.sleep(3)


sel = SeleniumTest()

sel.read_accoutn_list()
sel.read_black_list()
sel.login('ranmi1@web.de', 'immer123')
