# encoding: UTF-8
#spider of guoruan_notice
'''
Created on 2016年05月09日
@author: Cathor
'''

__author__ = 'Cathor'
import re
from scrapy import Selector
from scrapy.spiders import Spider
import datetime
from scrapy import Request, Selector
from ..items import TechItem
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class WHUNewsSpider(Spider):
    name = "WHU_News"
    base_url = "http://news.whu.edu.cn/wdyw/{0}.htm"
    root_domain = "http://news.whu.edu.cn/"    
    old = 0
    max_page = 1
    pages = 1
    isFirst = True
    school = u"武汉大学"
    department = u"武大要闻"
    #download_delay = 10

    def item_callback(self, result):
        if not result:
            self.old += 1

    def parse_items(self, response):
        url = response.url
        # print real_url
        print("Hi,this is in parse_items,url is" + url)
        # print response.body.encode('gbk')
        root = Selector(text=response.body)
        article = root.xpath("//form[@name='_newscontent_fromname']")
        # print article
        # print root
        attributes = article.xpath(".//div[@class='news_attrib']/text()")
        pubdate = attributes.re_first(ur'发布时间：(\d.+:\d+).*')
        author = attributes.re_first(ur'.*作者：(\S*).*')
        source = attributes.re_first(ur'.*来源：(\S*)\s*.*')
        print pubdate
        # print author.encode('utf-8')
        print source.encode('utf-8')
        if author != "":
            author = author + " " + source
        else:
            author = source
        title = article.xpath(".//div[@class='news_title']/text()").extract_first()
        title = re.sub(r'\s', '', title)
        subtitle = article.xpath("//div[@class='news_ytitle']/text()").extract_first()
        if subtitle is not None:
            subtitle = re.sub(r'\s', '', subtitle)
            title = title + ' ' + subtitle
        print title
        content = ""
        ps = article.xpath(".//div[@class='news_content']//p")
        if len(ps) > 0:
            for pp in ps:
                for text in pp.xpath(".//text()").extract():
                    content += text
                content += "\n"
        else:
            texts = root.xpath("//body/div[2]//text()").extract()
            for text in texts:
                content += text
        # print content.decode("unicode_escape").encode('gbk')
        yield TechItem(url=url.encode('utf-8'), department=self.department.encode('utf-8'),
                       school=self.school.encode('utf-8'), content=content.encode('utf-8'), 
                       publish_time=pubdate, title=title.encode('utf-8'), author=author)

    def start_requests(self):
        return [Request('http://news.whu.edu.cn/wdyw.htm', method="GET", callback=self.parse), ]

    def parse(self, response):
        root = response.selector
        # print real_body
        if self.old < 5:
            if self.isFirst:
                root_page = root.xpath("//td[@align='left']//a[@class='Next'][1]/@href").re_first(r"wdyw/(\d+)\.htm")
                print root_page
                self.max_page = int(root_page) + 1
                self.isFirst = False
            self.log('Hi, this is an page! %s' % response.url)
            self.new = 0
            self.pages += 1
            links = root.xpath("//div[@class='page_index_left']//div[@class='list']//div[@class='infotitle']/a")
            print links
            for a in links:
                iurl = a.xpath("@href").extract_first()
                print iurl
                str_url = str(iurl).split('/', 1)[1]
                # print arg_id
                iurl = self.root_domain + str_url
                print iurl
                yield Request(iurl, method="GET", callback=self.parse_items)
            print "here go to next page "+str(self.pages)
            if self.pages <= self.max_page:
                yield Request(self.base_url.format(self.max_page - self.pages + 1), method="GET", callback=self.parse)
