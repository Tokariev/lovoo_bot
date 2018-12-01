import requests
import json

# https://de.lovoo.com/welcome/login
# llaura.bazutsch@eb.de

# url = "https://de.lovoo.com/welcome/login"

def login(username, password):
    url = "https://de.lovoo.com"
    try:
        session = requests.Session()
        # session.get(url, auth=('llaura.bazutsch@eb.de', 'immer123'))
        data = {'_username': username,
                '_password': password,
                '_remember_me': 'false'
                }
        request = session.post('https://de.lovoo.com/login_check', data=data)
        jsFormat = request.json()
        if(jsFormat['success'] == True):
            print(username + ' --- Entered')
        else:
            print(username + ' --- ' + jsFormat['message'])
    except:
        print("BAD REQUEST")


login(username='llaura.bazutsch@eb.de', password='immer13')