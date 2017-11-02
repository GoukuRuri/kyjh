# -*- coding: UTF-8 -*-
import codecs
import re
__author__ = 'qiaoruikai'
import scrapy
from ..items import TechItem
import datetime
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# spider of whu news
"""
Created on 2015年10月2日

@author: qiaoruikai
@introduction: spider of WHU RSB
"""


class WHUSpider(scrapy.Spider):
    name = "WHU_RSB"
    allowed_domains = ["rsb.whu.edu.cn"]
    start_urls = [
        "http://rsb.whu.edu.cn/index.php?c=content&a=list&catid=18"
    ]
    school = "武汉大学"
    department = '人事部'
    max_page = 1
    pages = 1
    old = 0
    isFirst = True

    
    def item_callback(self, result):
        if not result:
            self.old += 1

    def parse(self, response):
        """

        :param response:
        :return:

        取各版块的url并传入到parse_pages

        """
        if self.old >= 5:
            return
        self.log('Hi, this is an page! %s' % response.url)
        # new = 11
        # total_new = 0
        # url = response.url
        # hasNext = True
        # now =  datetime.date.today()
        # delay = datetime.timedelta(days=1)
        # pages = 1
        # while self.new > 10 and self.hasNext:
        root = response.selector
        div = root.xpath("//div[@class='fuwu_text2']")
        lis = div.xpath(".//li")
        if self.isFirst:
            count = int(div.xpath(".//div[@class='page']//a[1]/text()").re_first(ur'共(\d+)条'))
            max_page = count / 20
            if max_page * 20 < count:
                max_page += 1
            self.max_page = max_page
            self.isFirst = False
        self.pages += 1

        
        print root
        
        for li in lis:
            item = TechItem()
            title = li.xpath(".//a/text()").extract_first()
            pubdate = li.xpath(".//span/text()").extract_first()
            item["title"] = title
            item["school"] = self.school
            item["department"] = self.department
            item["publish_time"] = pubdate
            item['author'] = ''
            iurl = li.xpath(".//a/@href").extract_first()
            if str(iurl).startswith("/"):
                iurl = "http://rsb.whu.edu.cn" + iurl
                item['url'] = iurl
                print "HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHh"
                yield scrapy.Request(iurl, self.parse_inner, meta={'item': item})
            else:
                item['url'] = iurl
                item['content'] = ''
                # if (not updatetool.hasUrl(iurl)) and  self.now - item_date < self.delay:
                # fp.process_item(item, "123")
                yield item
        if self.pages <= self.max_page:
            url = 'http://rsb.whu.edu.cn/index.php?c=content&a=list&catid=18&page=' + str(self.pages)
            print url
            # self.hasNext = False
            yield scrapy.Request(url, self.parse)

    def parse_inner(self, response):
        item = response.meta['item']
        root = response.selector
        div = root.xpath("//div[@class='xiangxi_text']")
        ps = div.xpath(".//p")
        content = ""
        for p in ps:
            temp = ''
            for text in p.xpath('.//text()').extract():
                temp += text.encode('utf-8')
            if temp.strip() != "":
                content += temp + '\n'
        item['content'] = content
        pub_time = root.xpath("//h1[@class='xiangxi_h1']/text()").re_first('.*(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}).*')
        item["publish_time"] = pub_time
        yield item
