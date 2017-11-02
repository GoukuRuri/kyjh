# encoding=utf-8
import re
import sys

#from utils import DefaultInfo

reload(sys)
sys.setdefaultencoding('utf-8')
"""
Spider for WHU kfb
@author: Cathor
"""

from scrapy.spiders import Spider
import scrapy
from ..items import TechItem
from scrapy.selector import Selector


class WHUSpider(Spider):
    name = "whu_spider"
    school = u"武汉大学"
    department = u'科发部'
    old = 0
    first = True
    url_root = "http://kfy.whu.edu.cn"
    url_prefix = "http://kfy.whu.edu.cn/xwzx/tzgg/"
    max_page = 0
    download_delay = 1
    current_page = 0
    start_urls = [
        "http://kfy.whu.edu.cn/xwzx/tzgg.htm",
    ]

    def item_callback(self, result):
        if not result:
            self.old += 1

    def parse(self, response):
        if self.old >= 5:
            return
        lis = response.xpath('//div[@class="index2_right_list3"]//li')
        for li in lis:
            href = li.xpath("span/a/@href").extract_first()
            print href
            index = str(href).rindex("../")
            url = self.url_root + href[index + 2:]
            yield scrapy.Request(url=url, callback=self.parse_inner, priority=1,meta={'dont_redirect':True})
        if self.first:
            self.max_page = int(response.xpath('//td[@id="fanye43211"]/text()').re_first(r'.+1/(\d+)\s*'))
            #DefaultInfo.printinfo(self.max_page)
            self.first = False
            self.current_page = self.max_page
        self.current_page -= 1
        to_url = self.url_prefix + str(self.current_page) + ".htm"
        print to_url
        if self.current_page > 1:
            yield scrapy.Request(url=to_url, callback=self.parse, priority=2)

    def parse_inner(self, response):
        url = response.url
        content = response.body
        charset = re.compile(r'content="text/html;.?charset=(.*?)"').findall(content)
        print charset
        print len(charset)
        try:
            if len(charset) > 0:
                content = content.decode(charset).encode('utf-8')
        except:
            pass
        root = Selector(text=content)
        title = root.xpath('//span[@class="wenzhang_title_font1"]/text()').extract_first()
        time = root.xpath('//span[@class="wenzhang_title_font2"]/text()').re_first(".*(.{10})")
        ps = root.xpath('//div[@id="vsb_newscontent"]//p//text()').extract()
        content = ""
        for p in ps:
            content += p + "\n"
        yield TechItem(url=url.encode('utf-8'), school=self.school.encode('utf-8'), department = self.department.encode('utf-8'), content=content.encode('utf-8'), publish_time=time, title=title.encode('utf-8'), author="")
