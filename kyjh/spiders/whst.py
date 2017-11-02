# -*- coding: UTF-8 -*-
'''
Created on 2017-7-12
@author: wuyuhuan
@introduction: Spider for http://www.whst.gov.cn/wsbs/list/554/1.aspx
'''


import re
from scrapy.spiders import Spider
import scrapy
from ..items import TechItem
from scrapy.selector import Selector
import codecs
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class WhstSpider(Spider):
    name = "whst_spider"                      # name of spider
    url_prefix = "http://www.whst.gov.cn"
    max_page = 0                              # max page number
    old = 0                                   # the number of urls that have been crawled
    current_page = 1                          # current page number
    start_urls = [
        "http://www.whst.gov.cn/wsbs/list/554/1.aspx"
    ]

    def item_callback(self, result):
        if not result:
            self.old += 1

    def parse(self, response):
        '''

        :param response:
        :return:
        取各版块的url放到parse_content中
        '''
        if self.old >= 5:
            return
        # <block>
        sel = Selector(response)
        urls = sel.xpath(r'//div[@class="list_news clearfix"]/ul/li/a/@href').extract()
        pages = sel.xpath(r'//div[@class="page"]/span/i/text()').extract()
        self.max_page = int(pages[0])
        for url in urls:
            wurl = self.url_prefix + url
            #print wurl
            yield scrapy.Request(url=wurl,callback=self.parse_content,priority=1,cookies={},dont_filter=True)
        if self.current_page <= self.max_page:
            # self.current_page += 1
            next_url = "http://www.whst.gov.cn/wsbs/list/554/" + str(self.current_page) + ".aspx"
            yield scrapy.Request(url=next_url,callback=self.parse,priority=2,cookies={},dont_filter=True)
        # <end block>

    def parse_content(self,response):
        '''
        :param response:
        :return:  content of each page
        '''
        item = TechItem()
        # <block>
        sel = Selector(response)
        title = sel.xpath(r'//div[@class="news_point"]/div[@class="art_title"]/h4/text()').extract()[0]
        publish_time = sel.xpath(r'//div[@class="art_title"]/div[@class="info"]/span/text()').extract()[0][5:]
        author = sel.xpath(r'//div[@class="art_title"]/div[@class="info"]/span/text()').extract()[2][4:]
        contents = sel.xpath(r'//div[@class="news_point"]/div[@class="art_content clearfix"]/p')
        string = ''
        for content in contents:
            temp = ''
            for text in content.xpath(r'.//text()').extract():
                temp += text.decode('utf-8')
            if temp.strip() != "":
                string += temp + '\n'
        # <end block>
        item['title'] = title.encode('utf-8')
        item['publish_time'] = publish_time.encode('utf-8')
        item['author'] = author.encode('utf-8')
        item['content'] = string.encode('utf-8')
        item['url'] = response.url
        item['school'] = u'武汉市科技局'.encode('utf-8')
        item['department'] = u'公告'.encode('utf-8')
        # file = codecs.open('item.txt','a+',encoding='utf-8')
        # file.write(str(item))
        yield item