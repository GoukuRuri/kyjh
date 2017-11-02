# -*- coding: utf-8 -*-
'''
Created on 2017-10-25
@author: Hugh
introduction: Spider of http://kfy.whut.edu.cn/
'''


import re
from kyjh.items import TechItem
from scrapy.spiders import Spider
import scrapy
from scrapy.selector import Selector
#from utils import DefaultInfo
import datetime
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class WhuoTSpider(Spider):
    name = 'whuot'
    school = u"武汉理工大学"
    department = u"科发院"
    now = datetime.date.today()
    page = 1
    isFirst = True
    old = 0
    url_prefix = 'http://www.whut.edu.cn/2015web/tzgg/'
    start_urls = [
        "http://www.whut.edu.cn/2015web/tzgg/"
    ]

    def item_callback(self, result):
        if not result:
            self.old += 1

    def parse(self, response):
        sel = Selector(response)

        # urls
        urls = sel.xpath('//ul[@class="normal_list2"]/li/span/a/@href').extract()
        for url in urls:
            wurl = self.url_prefix + url[2:]
            yield scrapy.Request(url=wurl, callback=self.parse_content, cookies={}, priority=1, dont_filter=True)

        # page
        pages = sel.xpath('//div[@class="num_nav"]/script[@language="JavaScript"]/text()').extract()[0]
        pattern = re.compile('(\d)')
        max_page = re.findall(pattern, pages)[0]
        if self.page < int(max_page):
            next_url = self.url_prefix + 'index_' + str(self.page) + '.htm'
            yield scrapy.Request(url=next_url,callback=self.parse,cookies={},priority=2,dont_filter=True)


    def parse_content(self, response):
        item = TechItem()
        sel = Selector(response)
        #title
        title = sel.xpath('//div[@class="art_tit"]/h2/text()').extract()[0]
        #publish_time
        ap = sel.xpath('//div[@class="art_info"]/text()').extract()[0]
        pattern = re.compile(r'(\d+)')
        ap_pattern = re.findall(pattern, ap)
        publish_time = ap_pattern[0] + "-" + ap_pattern[1] + "-" + ap_pattern[2]
        #content
        contents = sel.xpath('//div[@class="TRS_Editor"]/p')
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
        item['publish_time'] = publish_time
        item['content'] = string
        yield item


