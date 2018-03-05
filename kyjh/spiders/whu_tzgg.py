# -*- coding:utf-8 -*-
'''
Created on 2017-12-31
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

class WHU_tzgg(Spider):
    name = 'whu_tzgg'
    old = 0
    school = u'武汉大学'
    department = u'通知公告'
    download_delay = 1.0
    max_page = 0
    page = 1
    start_urls = [
        'http://www.whu.edu.cn/tzgg.htm'
    ]
    url_prefix = 'http://www.whu.edu.cn/'
    root_url = 'http://www.whu.edu.cn/tzgg/{}.htm'

    def item_callback(self, result):
        if not result:
            self.old += 1

    def parse(self, response):
        if self.old >20:
            return
        sel = Selector(response)
        li = sel.xpath('//div[@class="row"]/ul/li')

        title = sel.xpath('//div[@class="row"]/ul/li/div[@class="col-xs-12 col-sm-6 col-md-6"]/a/text()').extract()
        url = sel.xpath('//div[@class="row"]/ul/li/div[@class="col-xs-12 col-sm-6 col-md-6"]/a/@href').extract()
        p_d = sel.xpath('//div[@class="row"]/ul/li/center/div/text()').extract()
        department = sel.xpath('//div[@class="row"]/ul/li/center/div/text()').extract()

        for i in range(0, len(title)):
            s_title = title[i]
            s_url = url[i]
            pubtime = p_d[2*i + 1]
            if 'info' in s_url:
                s_url = self.url_prefix + s_url
            yield scrapy.Request(s_url,callback=self.parse_content,meta={'title':s_title,'pubtime':pubtime},priority=1)

        max_page = sel.xpath('//*[@id="fanye46693"]/text()').extract()[0]
        pattern = re.compile('1/(\d+)')
        t = re.findall(pattern, max_page)
        self.max_page = int(t[0])
        next_url = self.url_prefix.format(self.max_page - self.page)
        yield scrapy.Request(next_url, callback=self.parse_2,priority=2)

    def parse_2(self, response):
        if self.old >20:
            return
        sel = Selector(response)
        li = sel.xpath('//div[@class="row"]/ul/li')
        title = sel.xpath('//div[@class="row"]/ul/li/div[@class="col-xs-12 col-sm-6 col-md-6"]/a/text()').extract()
        url = sel.xpath('//div[@class="row"]/ul/li/div[@class="col-xs-12 col-sm-6 col-md-6"]/a/@href').extract()
        p_d = sel.xpath('//div[@class="row"]/ul/li/center/div/text()').extract()
        department = sel.xpath('//div[@class="row"]/ul/li/center/div/text()').extract()
        if len(title) > 25:
            for i in range(6,26):
                s_title = title[i]
                s_url = url[i]
                pubtime = p_d[2*i + 1]
                if 'info' in s_url:
                    s_url = self.url_prefix + s_url.replace('../','')
                yield scrapy.Request(s_url,callback=self.parse_content,meta={'title':s_title,'pubtime':pubtime},priority=1)
        if len(title)<25:
            for i in range(6,len(title)):
                s_title = title[i]
                s_url = url[i]
                pubtime = p_d[2*i + 1]
                if 'info' in s_url:
                    s_url = self.url_prefix + s_url
                yield scrapy.Request(s_url,callback=self.parse_content,meta={'title':s_title,'pubtime':pubtime},priority=1)

        self.page += 1
        if self.page < self.max_page:
            next_url = self.root_url.format(self.max_page - self.page)
            yield scrapy.Request(next_url, callback=self.parse_2, priority=2)

    def parse_content(self, response):
        item = TechItem()
        title = response.meta['title']
        pubtime = response.meta['pubtime']
        sel = Selector(response)
        contents = sel.xpath('//div[@class="v_news_content"]/p')
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
