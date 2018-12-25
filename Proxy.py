from lxml import html

import requests


class Proxy(object):
    proxy_url = 'https://www.ip-adress.com/proxy-list'
    proxy_list = []

    def __init__(self):
        r = requests.get(self.proxy_url)
        str = html.fromstring(r.content)
        # ip_port = str.xpath("concat(/html/body/main/table/tbody/tr[*]/td[1]/a/text(), /html/body/main/table/tbody/tr[*]/td[1])")
        ips = str.xpath(
            "/html/body/main/table/tbody/tr[*]/td[1]/a/text()")
        ports = str.xpath("//html/body/main/table/tbody/tr[*]/td[1]/text()")

        for idx, ip in enumerate(ips):
            self.proxy_list.append(ip + ports[idx])

        self.proxy_list

    def get_proxy(self):
        for proxy in self.proxy_list:
            url = 'http://' + proxy
            try:
                r = requests.get('https://www.google.com/', proxies={'http': url})
                if r.status_code == 200:
                    return url
            except requests.exceptions.ConnectionError:
                continue
