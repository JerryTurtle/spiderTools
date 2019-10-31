# -*- coding=utf-8 -*-
import os,time

import configparser

import pymysql

import json

import redis

# 读取数据库配置
cf = configparser.ConfigParser()
# configparser 用以读写配置文件
cf.read('DatabaseConfig.ini', encoding='utf-8')

cf_redis_name = "REDIS_TEST"
# mysql
redis_db = cf.get(cf_redis_name, 'redis_db')
redis_host = cf.get(cf_redis_name, 'redis_host')
redis_port = cf.get(cf_redis_name, 'redis_port')
# mysql_user = cf.get(cf_redis_name, 'mysql_user')
redis_passwd = cf.get(cf_redis_name, 'redis_passwd')
r = redis.StrictRedis(host=redis_host, port=int(redis_port), db=int(redis_db), password=redis_passwd)

cf_mysql_name = "MYSQL_TEST"
# mysql
mysql_db = cf.get(cf_mysql_name, 'mysql_db')
mysql_host = cf.get(cf_mysql_name, 'mysql_host')
mysql_port = cf.get(cf_mysql_name, 'mysql_port')
mysql_user = cf.get(cf_mysql_name, 'mysql_user')
mysql_passwd = cf.get(cf_mysql_name, 'mysql_passwd')
#每隔
def mysql2redis(id):


    mysql_conn = pymysql.connect(mysql_host, mysql_user, mysql_passwd, mysql_db, int(mysql_port), charset="utf8")
    mysql_cur = mysql_conn.cursor()
    select_sql = "SELECT task_id,type1,type2,type3,type4,type5,url" \
                " FROM policy_spider_log WHERE state = 0 AND "\
                 "spider_stage = 2 AND task_id = %s;" % id
    mysql_cur.execute(select_sql)
    i = 0
    url_list = []
    while True:

        row = mysql_cur.fetchone()
        if not row:
            InsertQueue(url_list,task_id)
            break
        i=i+1
        task_id = row[0]
        type1 = row[1]
        type2 = row[2]
        type3 = row[3]
        type4 = row[4]
        type5 = row[5]
        url = row[6]
        url_info = {url: dict(url=url, task_id=task_id,type1=type1, type2=type2 ,\
                                type3=type3, type4=type4, type5=type5, \
                                insert_time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))}
        url_list.append(url_info)
        if i%200 == 0:
            url_list = list(set(url_list))
            InsertQueue(url_list,str(task_id))
            url_list.clear()


    # 将任务存入redis队列中
def InsertQueue(url_list,table_name):
    #url_list = item['info']
    with r.pipeline(transaction=False) as p:
        for url_info in url_list:
            c = json.dumps(url_info)
            p.lpush(table_name, c)
        p.execute()


def write_task(task_id):
    f = open('./spiders/config.ini', 'w', encoding='utf-8')
    f.write("[1]\n")
    f.write("task_id = %s\n" % task_id)
    f.close()

def run():
    os.system("scrapy crawl PolicySpider2")
import sys
if __name__ == "__main__":
    # if len(sys.argv) !=2:
    #     print("Error parameter!")
    # else:
    #     i = input("Input y and continue:")
    #     if i == "y":
    #         id=sys.argv[1]
    #         mysql2redis(id)
    #         write_task(id)
    #         run()
    #     else:
    #         print("exit！")

        id=sys.argv[1]
        mysql2redis(id)
        write_task(id)
        run()

