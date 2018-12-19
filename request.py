import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.common.keys import Keys
from requests.adapters import HTTPAdapter



# https://de.lovoo.com/welcome/login
# llaura.bazutsch@eb.de

# url = "https://de.lovoo.com/welcome/login"


def login(url, username, password, session):
    print('LOGIN: ' + str(username))
    try:
        # session.get(url, auth=('llaura.bazutsch@eb.de', 'immer123'))
        data = {'_username': username,
                '_password': password,
                '_remember_me': 'false'
                }
        response = session.post(url, data=data)
        json = response.json()
        if json['success']:
            print('Successfully logged in')
            time.sleep(1)
        else:
            print(json['message'])
    except:
        print("Authefication error")

def read_users_id_not_recursive(session, page, last_list_elem):
    print('Get list of all not liked users')
    list_id = []
    response = session.get(
        'https://de.lovoo.com/api_web.php/matches/wantyou?resultLimit=15&resultPage=' + str(page))
    json = response.json()
    results = json['response']['result']
    if json['response']['allCount'] == 0:
        return

    last_for_elem = results[-1]['user']['id']
    if last_list_elem == last_for_elem:
        print("Finish")
        return
    print('############################################ Page # ' + str(page))
    for elem in results:
        if is_liked(session, elem['id']):
            continue
        else:
            list_id.append(elem['id'])
            print(elem['user']['name'] + ' - ' + elem['id'] + ' no like')
    return list_id



# Recursive function for get all users ids
def read_users_id(session, page, last_list_elem):
    list_id = []
    response = session.get('https://de.lovoo.com/api_web.php/matches/wantyou?resultLimit=15&resultPage=' + str(page))
    json = response.json()
    results = json['response']['result']
    if json['response']['allCount'] == 0:
        return

    last_for_elem = results[-1]['user']['id']
    if last_list_elem == last_for_elem:
        print("Finish")
        return
    print('############################################ Page # ' + str(page))
    for elem in results:
        if is_liked(session, elem['id']):
            continue
        else:
            list_id.append(elem['id'])
            print(elem['user']['name'] + ' - ' + elem['id'] + ' no like')

    r_list = read_users_id(session, page + 1, last_list_elem=last_for_elem)
    # The isinstance() function checks if the object (first argument)
    # is an instance or subclass of classinfo class (second argument).
    if isinstance(r_list, list):
        for el in r_list:
            list_id.append(el)
        #    list_id.append(
        #        read_users_id(session, page + 1, last_list_elem=last_for_elem)
        #    )
    return list_id


def is_liked(session, profil_id):
    # connections GET request: https://de.lovoo.com/api_web.php/users/54a4037ee56da1ea478b4586/connections
    response = session.get('https://de.lovoo.com/api_web.php/users/' + str(profil_id) + '/connections')
    json = response.json()
    if json['response']['hasLiked'] == 0:
        return False
    else:
        return True


def make_like(session, profil_id):
    # POST request https://de.lovoo.com/api_web.php/matches/56dc3238150ba0e2378b4e8b?ref=profile&vote=1
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'
    }
    couns_of_likes = 13
    urlf = 'https://www.facebook.com/tr/?id=515327658632890&ev=SubscribedButtonClick&dl=https%3A%2F%2Fde.lovoo.com%2Fwelcome%2Flogin&rl=https%3A%2F%2Fde.lovoo.com%2Flanding%2Flogout%3F_locale%3Dde%26fb%3D0&if=false&ts=1544715350932&cd[buttonText]=Like&cd[buttonFeatures]=%7B%22name%22%3A%22%22%2C%22id%22%3A%22%22%2C%22tag%22%3A%22button%22%2C%22classList%22%3A%22o-button%20o-button--inverted-gender%20u-border-2%20u-border-radius-round%20u-float-right%22%2C%22value%22%3A%22%22%2C%22innerText%22%3A%22Like%22%2C%22imageUrl%22%3Anull%2C%22numChildButtons%22%3A0%2C%22destination%22%3A%22%22%7D&cd[formFeatures]=%5B%5D&cd[pageFeatures]=%7B%22title%22%3A%22LOVOO%20-%20Online%20Dating%20App%20zum%20Flirten%2C%20Chatten%2C%20Kennenlernen%22%7D&sw=1366&sh=768&v=2.8.34&r=stable&ec=' + str(
        couns_of_likes) + '&o=30&fbp=fb.1.1544704556661.1215624438&it=1544711449533&coo=false&es=automatic'
    url = 'https://de.lovoo.com/api_web.php/matches/' + str(profil_id) + '?ref=profile&vote=1'
    try:
        sf = requests.get(urlf, headers=headers)
        response = requests.post(url, headers=headers)
        json = response.json()
        print(json['statusCode'])
        print("Was liked")
    except:
        print("Account is not active")


def can_you_like(usr, passw, id):
    print('##### CHECK FOR ACTIVE ACCOUNT #####')
    browser = webdriver.Chrome()
    browser.set_window_position(900, 0)
    browser.get("https://de.lovoo.com/")
    einlogenBtn = browser.find_element(By.XPATH, '/html/body/div[1]/div/div[3]/button[2]')
    einlogenBtn.click()

    emailElem = browser.find_element(By.XPATH, '//*[@id="form"]/div[1]/input')
    emailElem.send_keys(usr)

    passwordElem = browser.find_element(By.XPATH, '//*[@id="form"]/div[2]/div[1]/input')
    passwordElem.send_keys(passw)
    time.sleep(1)

    try:
        einlogenBtn = WebDriverWait(browser, 100).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="form"]/div[2]/div[2]/button'))
        )
        einlogenBtn.click()
        print("Hauptseite login")
    except:
        print("Einloggen error")

    try:
        deinProfil = WebDriverWait(browser, 100).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="topmenu"]/div/nav/div/div[2]/div/ul[1]/li[3]/a'))
        )
        deinProfil.click()
        print("Dein profil seite")
    except:
        print("Dein profil seite error")

    try:
        moegenDich = WebDriverWait(browser, 100).until(
            EC.presence_of_element_located(
                (By.XPATH, '/html/body/div[1]/ng-view/div/div[2]/div/div[1]/div/ng-include/nav[2]/a[2]'))
        )
        moegenDich.click()
        print("Moegen dich seite")
    except:
        print("Moegen dich seite error")

    try:
        MDProfil = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH,
                                            '//a[contains(@href,"/profile/' + id + '")]//div'))
        )
        # Open profil
        MDProfil.click()

        try:
            # Try to like
            like_btn = WebDriverWait(browser, 3).until(
                EC.presence_of_element_located((By.XPATH,
                                                '//*[@id="profile-details"]/div/div[3]/div/button'))
            )
            like_btn.click()
            try:
                # Try to catch error message popup
                WebDriverWait(browser, 2).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'body > div:nth-child(3) > div > div')))
                print("##### ACCOUNT IS NOT ACTIVE #####")
                return False
            except:
                print('##### ACCOUNT IS ACTIVE #####')
                return True
        except:
            print('Except try to like')
    except:
        print("MD profil open error")
        return
    finally:
        # close popup window
        webdriver.ActionChains(browser).send_keys(Keys.ESCAPE).perform()
        time.sleep(1)
        webdriver.ActionChains(browser).send_keys(Keys.ESCAPE).perform()
        time.sleep(2)
        browser.quit()


def give_id_without_like(session, page):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'
    }
    url = 'https://de.lovoo.com/api_web.php/matches/wantyou?resultLimit=15&resultPage=' + str(page)

    response = session.get(url)
    json = response.json()
    results = json['response']['result']
    if json['response']['allCount'] == 0:
        print('No result on a page')
        return 'No results on a page'
    else:
        for el in results:
            # connections GET request: https://de.lovoo.com/api_web.php/users/54a4037ee56da1ea478b4586/connections to get liked status
            r = session.get('https://de.lovoo.com/api_web.php/users/' + el['user']['id'] + '/connections')
            json = r.json()
            if json['response']['hasLiked'] == 0:
                return el['user']['id']
            else:
                print('Try next ID...')
        give_id_without_like(session, page + 1)


def do_like(ids, browser, first_reguest):
    black_list_id = ''
    if first_reguest == 1:
        first_reguest = True
    else:
        first_reguest = False
    if first_reguest == True:
        browser.set_window_position(700, 0)
        browser.get("https://de.lovoo.com/")

        try:
            einlogenBtn = WebDriverWait(browser, 100).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[3]/button[2]'))
            )
            einlogenBtn.click()
            time.sleep(2)
        except:
            print("Einloggen error")


    #    einlogenBtn = browser.find_element(By.XPATH, '/html/body/div[1]/div/div[3]/button[2]')
    #    einlogenBtn.click()

        emailElem = browser.find_element(By.XPATH, '//*[@id="form"]/div[1]/input')
        emailElem.send_keys(usr)

        passwordElem = browser.find_element(By.XPATH, '//*[@id="form"]/div[2]/div[1]/input')
        passwordElem.send_keys(passw)
        time.sleep(1)

        try:
            einlogenBtn = WebDriverWait(browser, 100).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="form"]/div[2]/div[2]/button'))
            )
            einlogenBtn.click()
        except:
            print("Einloggen error")

        try:
            deinProfil = WebDriverWait(browser, 100).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="topmenu"]/div/nav/div/div[2]/div/ul[1]/li[3]/a'))
            )
            deinProfil.click()
        except:
            print("Dein profil seite error")
        try:
            moegenDich = WebDriverWait(browser, 100).until(
                EC.presence_of_element_located(
                    (By.XPATH, '/html/body/div[1]/ng-view/div/div[2]/div/div[1]/div/ng-include/nav[2]/a[2]'))
            )
            moegenDich.click()
        except:
            print("Moegen dich seite error")
    # ############## #
    # Liking process #
    # ############## #
    for elem_id in ids:
        try:
            # Open to open profile
            MDProfil = WebDriverWait(browser, 100).until(
                EC.presence_of_element_located((By.XPATH,
                                                '//a[contains(@href,"/profile/' + str(elem_id) + '")]//div'))
            )
            MDProfil.click()
        except:
            print("MD profil open error")
            webdriver.ActionChains(browser).send_keys(Keys.ESCAPE).perform()
            time.sleep(2)
            continue
        try:
            # Try to like
            like_btn = WebDriverWait(browser, 3).until(
                EC.presence_of_element_located((By.XPATH,
                                                '//*[@id="profile-details"]/div/div[3]/div/button'))
            )
            like_btn.click()
            time.sleep(2)

            try:
                # Try to catch congratulations message popup
                WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located((By.XPATH, '/html/body/div[*]/div/div/div/div[1]/div/i')))
                time.sleep(2)
                webdriver.ActionChains(browser).send_keys(Keys.ESCAPE).perform()
                time.sleep(2)
                webdriver.ActionChains(browser).send_keys(Keys.ESCAPE).perform()
                time.sleep(2)
            except:
                print("Break")
                continue
        except:
            print('Except try to like')
            break

        black_list_id = elem_id
        print(elem_id + ' go to blacklist')



# ###### --- START ---- ###### #
URL = 'https://de.lovoo.com/login_check'
usr = 'ranmi1@web.de'  # My test account
passw = 'immer123'
session = requests.Session()

login(URL, usr, passw, session)
id_without_like = give_id_without_like(session, 1)


if isinstance(id_without_like, str):
    if can_you_like(usr, passw, id_without_like):
        print('Make likes')
        # Get list all not liked user

        max_page = 5
        page = 1
        browser = webdriver.Chrome()
        browser.set_window_position(900, 0)
        while page < max_page:
            ids = read_users_id_not_recursive(session, page, 'Not matter')
            time.sleep(3)
            print('_')
            do_like(ids, browser, page)
            page += 1
        print('-FINISH-')
        browser.quit()
    else:
        print('Go to next')
else:
    print('No accounts without likes')


