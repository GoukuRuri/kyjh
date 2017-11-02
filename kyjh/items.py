# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
#from scrapy_djangoitem import DjangoItem
#from utils.DefaultInfo import HOME_DIR
import sys
#sys.path.insert(0, HOME_DIR)
#from news.models import Tech


# class TechItem(DjangoItem):
#     # title
#     # url
#     # content
#     # school
#     # publish_time
#     # author
#     # department
#     django_model = Tech

class TechItem(scrapy.Item):
    author = scrapy.Field()        # nullable
    title = scrapy.Field()         # not null
    content = scrapy.Field()       # nullable
    publish_time = scrapy.Field()  # not null
    url = scrapy.Field()           # not null
    school = scrapy.Field()        # not null
    department = scrapy.Field()    # not null
