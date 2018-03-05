# -*- coding:utf-8 -*-
'''
Created on 2018-03-05
@author: Hugh
introduction:
'''


import re
from ..items import TechItem
from scrapy.spiders import Spider
import scrapy
from scrapy.selector import Selector

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class WHU_cs_news(Spider):
    name = 'whu_cs_news'
    old = 0
    school = u'武汉大学'
    department = u'计算机学院-新闻动态'
    download_delay = 1.0
    max_page = 0
    page = 1
    start_urls = [
        'http://cs.whu.edu.cn/a/xinwendongtaifabu/'
    ]
    url_prefix = 'http://cs.whu.edu.cn'
    root_url = 'http://cs.whu.edu.cn/a/xinwendongtaifabu/list_37_{}.html'

    def item_callback(self, result):
        if not result:
            self.old += 1

    def parse(self, response):
        sel = Selector(response)
        url_list = sel.xpath('//*[@id="container"]/dl/dd/a/@href').extract()
        for i in url_list:
            yield scrapy.Request(url=self.url_prefix + i,callback=self.parse_content,priority=1)
        print len(url_list)
        if len(url_list)==15:
            self.page += 1
            url = self.root_url.format(self.page)
            yield scrapy.Request(url=url,callback=self.parse,priority=2)


    def parse_content(self, response):

        item = TechItem()
        sel = Selector(response)
        title = sel.xpath('//*[@id="container"]/dl/dt/text()').extract()[0]
        pubdate = sel.xpath('//*[@id="container"]/dl/dd[1]/span/text()').extract()[-1]
        pattern = re.compile('(\d+)')
        t = re.findall(pattern, pubdate)
        a = t[-5:]
        pubtime = a[0] + '-' + a[1] + '-' + a[2]
        contents = sel.xpath('//*[@id="container"]/dl/dd[2]')
        string = ''
        for content in contents:
            temp = ''
            for text in content.xpath('.//text()').extract():
                temp += text.encode('utf-8')
            if temp.strip() != "":
                string += temp + '\n'

        item['title'] = title.encode('utf-8')
        item['school'] = self.school
        item['department'] = self.department
        item['url'] = response.url
        item['author'] = ""
        item['publish_time'] = pubtime
        item['content'] = string
        yield item
