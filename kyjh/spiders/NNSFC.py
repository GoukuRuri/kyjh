# -*- coding:utf-8 -*-
'''
Created on 2017-7-19
@author: Hugh
introduction: Spider for nation natural science foundation of China
'''


import re
from ..items import TechItem
from scrapy.spiders import Spider
import scrapy
from scrapy.selector import Selector

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class NNSFCSpider(Spider):
    name = "nnsfc"
    school = u"国家自然科学基金委员会"
    department = u"项目指南"
    old = 0
    first = True
    download_delay = 5.0
    max_page = 0
    current_page = 10
    url_prefix = "http://www.nsfc.gov.cn"
    start_urls = [
        "http://www.nsfc.gov.cn/publish/portal0/tab434/module1132/more.htm"
    ]

    def item_callback(self, result):
        if not result:
            self.old += 1

    def parse(self,response):
        if self.old >= 5:
            return
        item = TechItem()
        sel = Selector(response)
        urls = sel.xpath(r'//ul[@class="C_InfoList"]/li[@class="clearfix"]/span[@class="fl"]/a/@href').extract()
        #print urls
        if self.first == True:
            for url in urls[1:]:
                self.first = False
                wurl = self.url_prefix + url
                yield scrapy.Request(url=wurl, callback=self.parse_content, cookies={}, priority=1, dont_filter=True)
        else:
            for url in urls:
                wurl = self.url_prefix + url
                yield scrapy.Request(url=wurl,callback=self.parse_content,cookies={},priority=1,dont_filter=True)
        pages = sel.xpath(r'//tr/td[@class="Normal"]/text()').extract()
        print pages[1][1]
        self.max_page = int(pages[1][1])
        self.current_page += 1
        if self.current_page <= self.max_page:
            next_url = "http://www.nsfc.gov.cn/publish/portal0/tab452/module1197/page" + str(self.current_page) +".htm"
            yield  scrapy.Request(url=next_url,callback=self.parse,cookies={},priority=2,dont_filter=True)

    def parse_content(self,response):
        item = TechItem()
        sel = Selector(response)
        title = sel.xpath(r'//div[@style="width: 100%;"]/div[@class="title_xilan"]/h1/text()').extract()
        #print title[0]
        ap = sel.xpath(r'//div[@style="width: 100%;"]/div[@class="line_xilan"]/text()').extract()[0]
        pattern = re.compile(r'(\d+)')
        ap_pattern = re.findall(pattern, ap)
        publish_time = ap_pattern[0] + "-" + ap_pattern[1] + "-" + ap_pattern[2]
        #print publish_time
        contents = sel.xpath(r'//div[@style="width: 100%;"]/div[@class="content_xilan"]/span[@class="normal105"]/p')

        string = ''
        for content in contents:
            temp = ''
            for text in content.xpath('.//text()').extract():
                temp += text.encode('utf-8')
            if temp.strip() != "":
                string += temp + '\n'
        item['title'] = title[0].encode('utf-8')
        item['school'] = self.school
        item['department'] = self.department
        item['url'] = response.url
        item['author'] = ""
        item['publish_time'] = publish_time
        item['content'] = string
        yield item