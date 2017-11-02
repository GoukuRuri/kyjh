# encoding: utf-8

from scrapy.spiders import Spider
from scrapy import Selector, Request
from ..items import TechItem
import datetime

class WhuUgsSpider(Spider):

    name = "whu_ugs_spider"
    school = "武汉大学"
    department = "本科生院"
    download_delay = 0.3
    url_root = "http://ugs.whu.edu.cn/"
    current_page = -1
    old = 0

    def item_callback(self, result):
        if not result:
            self.old += 1

    def start_requests(self):
        return [Request("http://ugs.whu.edu.cn/tzgg.htm", callback=self.parse)]

    def parse(self, response):
        if self.old > 5:
            return
        root = response.selector
        if self.current_page < 0:
            self.current_page = int(root.xpath('//td[@id="fanye44478"]/text()').re_first('1/(\d+)'))
        links = root.xpath('//td[@class="substance_r"]/ul[1]/li/a/@href').extract()
        for link in links:
            if link.startswith('..'):
                a = self.url_root + link[3:]
            else:
                a = self.url_root + link
            yield Request(a, callback=self.parse_content)
        if self.current_page > 1:
            self.current_page -= 1
            yield Request("http://ugs.whu.edu.cn/tzgg/%d.htm" % self.current_page, callback=self.parse)

    def parse_content(self, response):
        root = response.selector
        title = root.xpath('//div[@class="c_title"]/div[@class="title"]/text()').extract_first().encode('utf-8')
        infos = root.xpath('//td[@class="otherdate"]/text()').re('(\d{4}-\d{2}-\d{2})\s*\|\s*\S+:(\S*)')
        item = TechItem()
        item['title'] = title
        item['url'] = response.url
        item['school'] = self.school
        item['publish_time'] = infos[0]
        item['department'] = self.department
        item['author'] = infos[1].encode('utf-8')
        # title
        # url
        # content
        # school
        # publish_time
        # author
        # department
        ps = root.xpath('//div[@id="vsb_newscontent"]//p')
        content = ''
        for p in ps:
            temp = ''
            for text in p.xpath('.//text()').extract():
                temp += text.encode('utf-8')
            if temp.strip() != "":
                content += temp + '\n'
        item['content'] = content[:-1]
        yield item
