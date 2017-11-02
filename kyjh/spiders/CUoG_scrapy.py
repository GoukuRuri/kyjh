# -*- coding:utf-8 -*-
'''
Created on 2016-12-4
@author=wuyuhuan
introduction:spider of http://kjc.cug.edu.cn/zrkx/notice.asp and http://kjc.cug.edu.cn/shkx/notice.asp
'''

import codecs
import re
import socket
import scrapy
from scrapy.spiders import CrawlSpider
from scrapy.selector import Selector
from ..items import TechItem
import requests
import datetime,calendar

import sys
reload(sys)
sys.setdefaultencoding("utf-8")


class CUoGSpider(CrawlSpider):
    name = 'cuog'
    school = u"中国地质大学"
    department = u"科发院"
    now = datetime.date.today()
    page = 1
    isFirst = True
    old = 0
    url_prefix = 'http://kjc.cug.edu.cn/'
    url_list = ['http://kjc.cug.edu.cn/zrkx/tzgg.htm',
                'http://kjc.cug.edu.cn/shkx/tzgg.htm'
     ]

    def item_callback(self, result):
        if not result:
            self.old += 1

    def start_requests(self):
        for url in self.url_list:
            yield scrapy.Request(url,callback=self.mx_page,dont_filter=True)

    def mx_page(self, response):
        '''

        :param response:
        :return:  get max page
        '''
        sel_page = Selector(response)
        page = sel_page.xpath('//*[@id="fanye177601"]').extract()[0]
        pattern = re.compile('/(\d+)')
        page = re.findall(pattern, page)
        yield scrapy.Request(url=response.url, callback=self.parse, meta={'page':int(page[0])})

    def parse(self,response):
        '''
        :param response:
        :return:
        取各版块的url并传入到parse_content
        '''
        page = response.meta['page']
        sel=Selector(response)
        hs=sel.xpath('//div[@class="ny_news"]/div[@class="cont"]/ul/li/a/@href').extract()
        for h in hs:
            hi = re.sub('\.\.\/', '', h)
            url = self.url_prefix + hi
            yield scrapy.Request(url=url,callback=self.parse_content,dont_filter=True)

        if page > 1:
            page -= 1
            pattern = re.compile('(.*?tzgg)')
            preurl = re.findall(pattern, response.url)

            nexturl = preurl[0] + '/' + str(page) + '.htm'
            yield scrapy.Request(nexturl,callback=self.parse,dont_filter=True,meta={'page':page})

    def parse_content(self,response):
        '''

        :param self:
        :param response:
        :return: content of each page
        '''
        item=TechItem()
        sel=Selector(response)
        #title
        title=sel.xpath('//*[@id="content"]/div/div[2]/div[2]/div/form/div[1]/text()').extract()

        #content
        ps = sel.xpath('//*[@id="vsb_content"]')

        strings = ''
        for p in ps:
            temp = ''
            for text in p.xpath('.//text()').extract():
                temp += text.encode('utf-8')
            if temp.strip() != "":
                strings += temp + '\n'
        #pubtime
        wtime=sel.xpath('//*[@id="content"]/div/div[2]/div[2]/div/form/div[2]/p/text()').re('(\d+)')
        year=int(wtime[0])
        month=int(wtime[1])
        day=int(wtime[2])
        hour=int(wtime[3])
        minute=int(wtime[4])
        second=int(wtime[5])
        pubtime=datetime.datetime(year,month,day,hour,minute,second,0)
        #item_date=datetime.date(year,month,day)

        item['title']=title[0]
        item['url']=response.url
        item['content']=strings
        item['school']=u'中国地质大学'
        item['publish_time']=pubtime
        item['author'] = ''
        item['department']=u'科发院'
        yield item

    def item_callback(self,result):
        if not result:
            self.old += 1



