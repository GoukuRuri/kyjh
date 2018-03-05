# -*- coding:utf-8 -*-
'''
Created on 2017-11-04
@author: Hugh
introduction: 中国计算机学会新闻动态爬虫
'''

import re
from ..items import TechItem
from scrapy.spiders import Spider
import scrapy
from scrapy.selector import Selector

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class CCFSpider(Spider):
    name = 'ccf_spider'
    school = u'中国计算机协会'
    department = u'新闻动态'
    old = 0
    download_delay = 1.0
    max_page = 0
    current_page = 0
    url_prefix1 = 'http://www.ccf.org.cn/news/ccfjj/'
    url_prefix2 = 'http://www.ccf.org.cn/news/xwlb/'
    url_list = [
        'http://www.ccf.org.cn/news/ccfjj/',
        'http://www.ccf.org.cn/news/xwlb/'
    ]

    def item_callback(self, result):
        if not result:
            self.old += 1
        #DefaultInfo.printinfo(self.old)

    def start_requests(self):
        yield scrapy.Request(self.url_list[0], callback=self.parse_ccfjj, cookies={})
        yield scrapy.Request(self.url_list[1], callback=self.parse_xwlb, cookies={})

    def parse_ccfjj(self, response):
        sel = Selector(response)
        urls = sel.xpath('//div[@class="media-body"]/h4/a/@href').extract()
        for url in urls:
            if 'ccf.org.cn' not in url:
                url = 'http://www.ccf.org.cn' + url
            yield scrapy.Request(url, callback=self.parse_content, cookies={}, priority=1)
        next_page = sel.xpath('//div[@class="pageBox"]/div/ul/li/a/@href').extract()[-1]
        if '#' in next_page:
            pass
        elif 'http' in next_page:
            yield scrapy.Request(next_page, callback=self.parse_ccfjj, cookies={}, priority=2)
        else:
            next_url = self.url_prefix1 + next_page
            yield scrapy.Request(next_url, callback=self.parse_ccfjj, cookies={}, priority=2)

    def parse_xwlb(self, response):
        sel = Selector(response)
        urls = sel.xpath('//div[@class="media-body"]/h4/a/@href').extract()
        for url in urls:
            if 'ccf.org.cn' not in url:
                url = 'http://www.ccf.org.cn' + url
            yield scrapy.Request(url, callback=self.parse_content, cookies={}, priority=1)
        next_page = sel.xpath('//div[@class="pageBox"]/div/ul/li/a/@href').extract()[-1]
        if '#' in next_page:
            pass
        elif 'http' in next_page:
            yield scrapy.Request(next_page, callback=self.parse_xwlb, cookies={}, priority=2)
        else:
            next_url = self.url_prefix2 + next_page
            yield scrapy.Request(next_url, callback=self.parse_xwlb, cookies={}, priority=2)

    def parse_page(self, response):
        pass


    def parse_content(self, response):
        if 'shtml' not in response.url:
            pass

        item = TechItem()
        sel = Selector(response)
        # title
        title = sel.xpath('//div[@class="borderAll"]/h2/text()').extract()[0]
        # publish_time
        ap = sel.xpath('//div[@class="col-md-4 text-center col-sm-4 col-xs-4"]/text()').extract()[0]
        pattern = re.compile(r'(\d+)')
        ap_pattern = re.findall(pattern, ap)
        publish_time = ap_pattern[0] + "-" + ap_pattern[1] + "-" + ap_pattern[2]
        # content
        contents = sel.xpath('//div[@class="articleCon"]/p')
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