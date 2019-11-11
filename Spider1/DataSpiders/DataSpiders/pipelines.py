# -*- coding: utf-8 -*-
from .items import SpiderLogItem, SpiderDataItem, SpiderUrlMysqlItem, SpiderUrlRedisItem

import pymysql

import pymongo

import copy

import configparser

import os

import json

import redis


class DataspidersPipeline(object):
    def process_item(self, item, spider):
        return item


# 存储数据库管道
class DatabasePipeline(object):
    def open_spider(self, spider):
        # 读取数据库配置
        cf = configparser.ConfigParser()
        # configparser 用以读写配置文件
        cf.read('DatabaseConfig.ini', encoding='utf-8')
        cf_mysql_name = "MYSQL_TEST"
        # mysql
        mysql_db = cf.get(cf_mysql_name, 'mysql_db')
        mysql_host = cf.get(cf_mysql_name, 'mysql_host')
        mysql_port = cf.get(cf_mysql_name, 'mysql_port')
        mysql_user = cf.get(cf_mysql_name, 'mysql_user')
        mysql_password = cf.get(cf_mysql_name, 'mysql_password')
        self.mysql_conn = pymysql.connect(mysql_host, mysql_user, mysql_password, mysql_db, int(mysql_port), charset="utf8")
        self.mysql_cur = self.mysql_conn.cursor()
        #mongo
        cf_mongo_name = "MONGODB_TEST"
        mongo_host = cf.get(cf_mongo_name, 'mongo_host')
        mongo_port = cf.get(cf_mongo_name, 'mongo_port')
        mongo_db = cf.get(cf_mongo_name, 'mongo_db')
        mongo_table = cf.get(cf_mongo_name, 'mongo_table')
        mongo_user = cf.get(cf_mongo_name, 'mongo_user')
        mongo_password = cf.get(cf_mongo_name, 'mongo_password')
        self.mongo_client = pymongo.MongoClient(host=mongo_host, port=int(mongo_port))
        self.db_auth = self.mongo_client.admin
        self.db_auth.authenticate(mongo_user, mongo_password)
        mongo_db = self.mongo_client[mongo_db]
        self.mongo_table = mongo_db[mongo_table]

        cf_redis_name = "REDIS_TEST"
        # mysql
        redis_db = cf.get(cf_redis_name, 'redis_db')
        redis_host = cf.get(cf_redis_name, 'redis_host')
        redis_port = cf.get(cf_redis_name, 'redis_port')
        #mysql_user = cf.get(cf_redis_name, 'mysql_user')
        redis_password = cf.get(cf_redis_name, 'redis_password')
        self.r = redis.StrictRedis(host=redis_host, port=int(redis_port), db=int(redis_db), password=redis_password)

    def close_spider(self,spider):
        #mysql
        self.mysql_conn.commit()
        self.mysql_conn.close()
        #mongo
        self.mongo_client.close()

    #mysql使用函数向数据库中插入数据，mangodb直接序列化成字典插入表中
    def process_item(self, item, spider):
        item = copy.deepcopy(item)
        if isinstance(item, SpiderLogItem):
            self.insert_db_spider_log(item)
            self.mysql_conn.commit()

        if isinstance(item, SpiderDataItem):
            data = dict(item)
            self.mongo_table.insert(data)

        if isinstance(item, SpiderUrlMysqlItem):
            self.insert_db_spider_url(item)
            self.mysql_conn.commit()

        if isinstance(item, SpiderUrlRedisItem):
            self.InsertQueue(item)

    def insert_db_spider_log(self,item):
        values = (
            item["task_id"],
            item["state"],
            item["spider_stage"],
            item["http_code"],
            item["msg"],
            item["url"],
            item["type1"],
            item["type2"],
            item["type3"],
            item["type4"],
            item["type5"],
            item["insert_time"],
            item["proxy"]
        )
        sql = "INSERT INTO policy_spider_log(task_id,state,spider_stage,http_code,msg,url,type1,type2,type3,type4,type5,insert_time,proxy) " \
              "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        self.mysql_cur.execute(sql, values)

    def insert_db_spider_url(self,item):
        values = (
            item["task_id"],
            item["url"],
            item["type1"],
            item["type2"],
            item["type3"],
            item["type4"],
            item["type5"],
            item["from_url"],
            item["insert_time"]
        )
        sql = "INSERT INTO policy_spider_url_info(task_id,url,type1,type2,type3,type4,type5,from_url,insert_time) " \
              "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        self.mysql_cur.execute(sql, values)


    # 将任务存入redis队列中
    def InsertQueue(self, item):
        #url_list = item['info']
        with self.r.pipeline(transaction=False) as p:
            for url_info in item['info']:
                c = json.dumps(url_info)
                p.lpush("url_zhangye", c)
            p.execute()