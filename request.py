import requests
from bs4 import BeautifulSoup
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
        if  json['success'] == True:
            print('Successfully logged in')
    except:
        print("Authefication error")

#Recursive function for get all users ids
def read_users_id(session, page):
   list_id = []
   response = session.get('https://de.lovoo.com/api_web.php/matches/wantyou?resultLimit=15&resultPage=' + str(page))
   json = response.json()
   users = json['response']['result']
   print('Page # ' + str(page))
   for elem in users:
    list_id.append(elem['id'])
    print(elem['id'])
   if page != 10:
       list_id.append(read_users_id(session, page + 1))
   else:
       return
   return list_id

####### --- START ---- #######
URL = 'https://de.lovoo.com/login_check'
USER = 'llaura.bazutsch@eb.de'
PASS = 'immer123'
session = requests.Session()

login(URL, USER, PASS, session)
read_users_id(session, 1)


