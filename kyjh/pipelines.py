# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
from scrapy.exceptions import DropItem
class KyjhPipeline(object):
    def __init__(self):
        self.url_record = set()
        self.file = open('item.json', 'wb')
    def process_item(self, item, spider):
        if item['url'] in self.url_record:
            raise DropItem("Crawled Item")
        else:
            self.url_record.add(item['url'])
            item['publish_time'] = str(item['publish_time'])
            line = json.dumps(dict(item),ensure_ascii=False) + '\n'
            self.file.write(line)
            return item
