import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.common.keys import Keys


# https://de.lovoo.com/welcome/login
# llaura.bazutsch@eb.de

# url = "https://de.lovoo.com/welcome/login"


def login(url, username, password, session):
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
    print('Page # ' + str(page))
    for elem in results:
        if is_liked(session, elem['id']):
            continue
        else:
            list_id.append(elem['id'])
            print(elem['user']['name'] + ' - ' + elem['id'])

    list_id.append(read_users_id(session, page + 1, last_list_elem=last_for_elem))
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


def can_you_like(usr, passw, browser, id):
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
        print('Try to open ' + '//a[contains(@href,"/profile/' + str(id) + '")]/@href')
        MDProfil = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH,
                                            '//a[contains(@href,"/profile/' + id + '")]//div'))
        )
        print('Try to open ' + '//a[contains(@href,"/profile/' + str(id) + '")]/div')
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
                print("Account is not active")
                return False
            except:
                print('Account is active')
                return True
        except:
            print('Except try to like')
    except:
        print("MD profil open error")
        return
    finally:
        # close popup window
        webdriver.ActionChains(browser).send_keys(Keys.ESCAPE).perform()
        time.sleep(2)
        browser.quit()


def give_id_without_like(session, page):
    page = 1
    response = session.get('https://de.lovoo.com/api_web.php/matches/wantyou?resultLimit=15&resultPage=' + str(page))
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





# ###### --- START ---- ###### #
URL = 'https://de.lovoo.com/login_check'
usr = 'llaura.bazutsch@eb.de'

# USER = 'boted@cliptik.net' My test account
passw = 'immer123'
session = requests.Session()


login(URL, usr, passw, session)
id_without_like = give_id_without_like(session, 1)

browser = webdriver.Chrome()
if can_you_like(usr, passw, browser, id_without_like):
    print('Make likes')
else:
    print('Go to next')

# read_users_id(session, 1, 'not_matter')
# liked = is_liked(session, '59b55a70297b50234438f017')
# if (liked == False):
#    make_like(session, '59b55a70297b50234438f017')


# #page-content > list-page > infinite-list > div.o-grid.o-grid--list.o-grid--lg.u-margin-bottom-0 > div:nth-child(1) > div > a
