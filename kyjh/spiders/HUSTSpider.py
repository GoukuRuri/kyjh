# -*- coding:utf-8 -*-
'''
Created on 2017-7-11
@author: Hugh
introduction: Spider for HUST kfb
'''


import re
from kyjh.items import TechItem
from scrapy.spiders import Spider
import scrapy
from scrapy.selector import Selector
#from utils import DefaultInfo
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class HUSTSpider(Spider):
    name = "hust_spider"
    school = u"华中科技大学"
    department = u"科发部"
    old = 0
    first = True
    download_delay = 5.0
    max_page = 0
    current_page = 0
    new = 0
    total_new = 0
    url_prefix = "http://kfy.hust.edu.cn/"
    start_urls = [
        "http://kfy.hust.edu.cn/index/tzgg.htm"
    ]

    def item_callback(self, result):
        if not result:
            self.old += 1
        #DefaultInfo.printinfo(self.old)

    def parse(self, response):
        if self.old >= 5:
            return
        item = TechItem()
        sel = Selector(response)

        urls = sel.xpath('//div[@class="nyright"]/div[@class="nynra"]/li/h3/a/@href').extract()
        page = sel.xpath('//td[@id="fanye154518"]/text()').extract()
        pattern1 = re.compile(r'.*?/(\d{2})')
        pages = re.findall(pattern1,page[0])
        self.max_page = int(pages[0])
        print self.max_page
        for url in urls:
            self.new += 1
            url = re.sub(r'\.\.\/','',url)
            wurl = self.url_prefix + url
            yield scrapy.Request(url=wurl, callback=self.parse_content,priority=1, cookies={}, dont_filter=True)
        if self.max_page - self.current_page > 0:
            self.current_page += 1
            next_url = "http://kfy.hust.edu.cn/index/tzgg/" + str(self.max_page - self.current_page) + ".htm"

            print self.current_page
            yield scrapy.Request(url=next_url, callback=self.parse,priority=2, cookies={}, dont_filter=True)
    def parse_content(self, response):
        item = TechItem()
        sel = Selector(response)
        title = sel.xpath(r'//div[@class="wjdtxx"]/h3/text()').extract()[0]
        ap = sel.xpath(r'//div[@class="wjdtxx"]/h4/text()').extract()
        ap_pattern = re.compile(r':(.*?)\xa0')
        ap_content = re.findall(ap_pattern, ap[0])
        author = ap_content[0]
        publish_time = ap_content[1]
        contents = sel.xpath(r'//div[@class="wjdtxx"]/ul/div[@id="vsb_content"]/p|h1')
        string = ''
        for content in contents:
            temp = ''
            for text in content.xpath('.//text()').extract():
                temp += text.encode('utf-8')
            if temp.strip() != "":
                string += temp + '\n'
        #print string

        item['title'] = title
        item['url'] = response.url
        item['content'] = string
        item['publish_time'] = publish_time
        item['author'] = author
        item['school'] = u'华中科技大学'
        item['department'] = u'科发部'
        yield item