from pathlib import Path
import requests
import datetime
import sys
import Proxy


def read_users_info_to_list(path_to_file):
    path = Path(path_to_file)
    if path.is_file():
        try:
            file = open(path, 'r+')
            user_list = [line.rstrip('\n') for line in file.readlines()]
            if not user_list:
                print("List is empty, exit")
                sys.exit()
            return user_list
        except Exception as error:
            write_to_log('Failed to read', error)
        finally:
            file.close()
    else:
        sys.exit('File not exist ' + path_to_file)


def write_to_log(message='', exception='', exc_info=''):
    info = exc_info
    # a Open an existing file for appending plain text
    log_file = open('log.log', 'a')
    log_file.write('{0} {1} {2}\n'.format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), message,
                                          exception, info))
    log_file.close()


def login(account):
    # Read user info
    try:
        arr = account.split('|')
        if len(arr) >= 2:
            username = arr[0]
            password = arr[1]
    except Exception as error:
        write_to_log("Failed to read " + account, error, sys.exc_info())

    # Login
    proxy = Proxy.Proxy()
    proxy = proxy.get_proxy()

    url = 'https://de.lovoo.com/login_check'
    session = requests.Session()

    try:
        payload = {'_username': username,
                   '_password': password,
                   '_remember_me': 'false'
                   }
        # header = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
        #                        'Chrome/71.0.3578.98 Safari/537.36'}
        # response = sess.get(url, data=data, headers=header, proxies=proxy)
        response = session.post(url, data=payload, proxies={'http': proxy})
        json = response.json()
        if json['success']:
            print('Successfully logged in')
            return session
        else:
            print(json['message'])
    except Exception as error:
        print(error)


def read_id_without_like(session, page):
    url = 'https://de.lovoo.com/api_web.php/matches/wantyou?resultLimit=15&resultPage=' + str(page)

    response = session.get(url)
    json = response.json()
    results = json['response']['result']
    if json['response']['allCount'] == 0:
        print('No result on a page')
        return
    else:
        for el in results:
            # connections GET request: https://de.lovoo.com/api_web.php/users/54a4037ee56da1ea478b4586/connections to
            #  get liked status
            r = session.get('https://de.lovoo.com/api_web.php/users/' + el['user']['id'] + '/connections')
            json = r.json()
            if json['response']['hasLiked'] == 0:
                return el['user']['id']
            else:
                print('Try next ID...')
        read_id_without_like(session, page + 1)


def is_active(session, user_id):

    payload = {"userId": str(user_id),
               "vote": 1,
               "ref": "profile"}

    url = 'https://www.lovoo.com/api_web.php/matches/' + str(user_id) + '?ref=profile&vote=1'

    headers = {
                'accept': 'application/json, text/plain, */*',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7,la;q=0.6',
                'app': 'lovoo',
                'content-length': '62',
                'content-type': 'application/json;charset=UTF-8',
                'origin': 'https://www.lovoo.com',
                'referer': 'https://www.lovoo.com/list/liked-you',
                'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
                }

    params = {
        'ref': 'profile',
        'vote': '1'
    }

    r = session.post(url, data=payload, headers=headers, params=params, )

    print(r)


def do_like(account):
    sess = login(account)
    id_without_like = read_id_without_like(sess, 1)
    print(id_without_like)
    is_active(sess, id_without_like)


# ###### --- START ---- ###### #

accounts_list = read_users_info_to_list('Test_user.txt')

for el_account in accounts_list:
    do_like(el_account)
    break
