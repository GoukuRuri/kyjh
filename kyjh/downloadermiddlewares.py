# -*- coding:utf-8 -*-
'''
Created on 2017-10-21
@author: Hugh
introduction: Analog IP
'''

import random
from scrapy.downloadermiddlewares.httpproxy import HttpProxyMiddleware


# IP
class HTTPPROXY(HttpProxyMiddleware):
    def __init__(self, ip=''):
        self.ip = ip

    def process_request(self, request, spider):
        item = random.choice(IPPOOL)
        try:
            print("The IP address currently in use is "+item[spider.name + "_ipaddr"])
            request.meta["proxy"] = "http://" + item[spider.name + "_ipaddr"]
        except Exception as e:
            print(e)
            return None

# define IPPOOL
IPPOOL = [
    {"nnsfc_ipaddr":"111.13.109.27:80", "whuot_ipaddr":"202.114.88.20"},
]