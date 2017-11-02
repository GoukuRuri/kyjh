# -*- coding:utf-8 -*-
'''
Created on 2017-07-31
@author: Hugh
@introduciton: Spider for http://www.gs.whu.edu.cn/index.php/index-show-tid-40.html
'''


import scrapy
import re
from ..items import TechItem
from scrapy.spiders import Spider
import scrapy
from scrapy.selector import Selector

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class WHU_GS(Spider):
    name = 'whu_gs'
    school = u'武汉大学'
    department = u'研究生院'
    url_prefix = 'http://www.gs.whu.edu.cn'
    old = 0
    type = 0
    current_page = 1
    max_page = 0
    download_delay = 5.0
    start_urls = [
        'http://www.gs.whu.edu.cn/index.php/index-show-tid-40.html'
    ]

    def item_callback(self, result):
        if not result:
            self.old += 1

    def parse(self, response):
        '''

        :param response:  url_list
        :return:
        '''
        if self.old >= 1:
            return
        sel = Selector(response)
        urls = sel.xpath(r'//div[@class="ulnotice"]/ul/li/a/@href').extract()
        page = sel.xpath(r'//div[@class="fenye"]/p/span/text()').extract()[0]
        self.max_page = int(page)
        for url in urls:
            if 'http' in url:
                wurl = url
            else:
                wurl = self.url_prefix + url
            yield scrapy.Request(url=wurl, callback=self.parse_content, priority=1, dont_filter=True)
        if self.current_page < self.max_page:
            self.current_page += 1
            wurl = 'http://www.gs.whu.edu.cn/index.php/index-show-tid-40-p-' + str(self.current_page) + '.html'
            yield  scrapy.Request(url=wurl, callback=self.parse, priority=2, dont_filter=True)

    def parse_content(self, response):
        '''

        :param response: url_page
        :return: content of each page
        '''

        item = TechItem()
        sel_page = Selector(response)
        try:
            title = sel_page.xpath(r'//div[@class="ny_con news_con_ny"]/h3/text()').extract()[0]
            self.type = 0
        except:
            title = sel_page.xpath(r'//div[@class="neiyeMin630 neiyeRightCon"]/h3/text()').extract()[0]
            self.type = 1
        try:
            ap = sel_page.xpath(r'//div[@class="ny_con news_con_ny"]/p[@class="news_time"]/span/text()').extract()[0]
        except:
            ap = sel_page.xpath(r'//div[@class="neiyeMin630 neiyeRightCon"]/h4/text()').extract()[0]
        year = ap[0:4]
        month = ap[5:7]
        day = ap[8:10]
        publish_time = year + '-' + month + '-' + day
        if self.type == 0:
            contents = sel_page.xpath(r'//div[@class="ny_con news_con_ny"]/p[@class="MsoNormal"]/span')
            if contents != []:
                pass
            else:
                contents = sel_page.xpath(r'//div[@class="ny_con news_con_ny"]/span/span')
        else:
            contents = sel_page.xpath(r'//div[@class="neiyeMin630 neiyeRightCon"]/p[@class="MsoNormal"]/span')
            if contents != []:
                pass
            else:
                contents = sel_page.xpath(r'//div[@class="ny_con news_con_ny"]/span/span')
        string = ''
        for content in contents:
            temp = ''
            for text in content.xpath(r'.//text()').extract():
                temp += text.encode('utf-8')
            if temp.strip() != "":
                string += temp + '\n'

        item['school'] = self.school
        item['department'] = self.department
        item['publish_time'] = publish_time
        item['title'] = title
        item['content'] = string
        item['url'] = response.url
        item['author'] = ''
        yield item


