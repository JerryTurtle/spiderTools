# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

from scrapy import Item, Field


class DataspidersItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


#日志记录
class SpiderLogItem(Item):
    task_id = Field()
    state = Field()
    spider_stage = Field()
    http_code = Field()
    proxy = Field()
    msg = Field()
    url = Field()
    type1 = Field()
    type2 = Field()
    type3 = Field()
    type4 = Field()
    type5 = Field()
    insert_time = Field()


#存储最终的页面
class SpiderDataItem(Item):
    task_id = Field()
    type1 = Field()
    type2 = Field()
    type3 = Field()
    type4 = Field()
    type5 = Field()
    url = Field()
    html = Field()
    insert_time = Field()

#记录二级url
class SpiderUrlMysqlItem(Item):
    task_id = Field()
    type1 = Field()
    type2 = Field()
    type3 = Field()
    type4 = Field()
    type5 = Field()
    url = Field()
    from_url = Field()
    insert_time = Field()


class SpiderUrlRedisItem(Item):
    info = Field()