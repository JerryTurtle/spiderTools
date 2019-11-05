import configparser

import os

import time

import scrapy

from ..GetUrl import GetUrl

from ..items import SpiderLogItem, SpiderUrlMysqlItem, SpiderUrlRedisItem




class PolicySpider1(scrapy.Spider):

    name = "PolicySpider1"
    start_urls = []

    # configparser用以读写配置文件
    cf = configparser.ConfigParser()
    cf.read(os.path.join(os.path.dirname(__file__), 'config.ini',), encoding='utf-8')
    # 读取任务信息
    cf_id = '1'
    url_head = cf.get(cf_id, 'url_head')
    taskid = cf.get(cf_id, 'task_id')
    type1 = cf.get(cf_id, 'type1')
    type2 = cf.get(cf_id, 'type2')
    type3 = cf.get(cf_id, 'type3')
    type4 = cf.get(cf_id, 'type4')
    type5 = cf.get(cf_id, 'type5')
    rules_url = cf.get(cf_id, 'rules_url')



    # 初始化start_urls列表
    urls = cf.get(cf_id, 'urls')
    for url in urls.split(';'):
        start_urls.append(url)
    print(start_urls)

    def start_requests(self):
        for url in self.start_urls:
            info = dict(url=url, url_head=self.url_head, task_id=self.taskid, type1=self.type1, \
                        type2=self.type2, type3=self.type3, type4=self.type4, type5=self.type5, rules_url=self.rules_url)
            yield scrapy.Request(url=url, callback=self.parse, meta={"info": info,
                                                                     })

    def parse(self, response):
        #print(response.meta["proxy"])
        # print(response.meta["header"])
        # 初始化SpiderLogItem对象
        # url = response.meta["info"]["urls"]
        # url_head = response.meta["info"]["url_head"]
        # task_id = response.meta["info"]["task_id"]
        # type1 = response.meta["info"]["type1"]
        # type2 = response.meta["info"]["type2"]
        # type3 = response.meta["info"]["type3"]
        # type4 = response.meta["info"]["type4"]
        # type5 = response.meta["info"]["type5"]

        spider_log_item = SpiderLogItem()
        spider_log_item["spider_stage"] = 1
        spider_log_item["url"] = response.meta["info"]["url"]
        spider_log_item["task_id"] = response.meta["info"]["task_id"]
        spider_log_item["type1"] = response.meta["info"]["type1"]
        spider_log_item["type2"] = response.meta["info"]["type2"]
        spider_log_item["type3"] = response.meta["info"]["type3"]
        spider_log_item["type4"] = response.meta["info"]["type4"]
        spider_log_item["type5"] = response.meta["info"]["type5"]
        spider_log_item["proxy"] = ""

        spider_log_item["insert_time"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        print("response status：",response.status)

        # 若状态码为200则分析网页，提取二级url并存入redis与mysql
        if response.status == 200:
            spider_log_item["state"] = 1
            spider_log_item["http_code"] = str(response.status)
            spider_log_item["msg"] = "SUCCESS"
            yield spider_log_item

            # 以下部分用来获取二级url并存入redis数据库

            g_u = GetUrl(content=response.text, head_url=self.url_head, info=response.meta["info"])
            href_list = g_u.rule_common1(str(self.rules_url).strip())

            # print(href_list)
            for href in href_list:
                # print(href.values())
                spider_url_mysql_item = SpiderUrlMysqlItem(list(href.values())[0])
                spider_url_mysql_item["from_url"] = response.meta["info"]["url"]
                yield spider_url_mysql_item
            # spider_url_redis_item = SpiderUrlRedisItem()
            # spider_url_redis_item["info"] = href_list
            # yield spider_url_redis_item

        else:
            spider_log_item["state"] = 0
            spider_log_item["http_code"] = str(response.status)
            spider_log_item["msg"] = response.body.decode('utf-8','ignore')
            yield spider_log_item
