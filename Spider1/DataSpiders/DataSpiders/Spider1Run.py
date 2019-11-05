# -*- coding=utf-8 -*-
"""
从数据库中取出任务，并写入condfig.ini的配置文件
配置文件的存在，是用来在启动脚本和spider之间中转数据用的
"""

import pymysql,time,os

import sys

import configparser



# 读取数据库配置
cf = configparser.ConfigParser()  #configparser用以读写配置文件
#print(os.path.join(os.path.dirname(__file__),os.sep, '/DatabaseConfig.ini'))
cf.read( 'DatabaseConfig.ini',encoding='utf-8')

cf_mysql_name = "MYSQL_TEST"
# mysql
mysql_db =cf.get(cf_mysql_name, 'mysql_db')
mysql_host = cf.get(cf_mysql_name, 'mysql_host')
mysql_port = cf.get(cf_mysql_name, 'mysql_port')
mysql_user = cf.get(cf_mysql_name, 'mysql_user')
mysql_passwd = cf.get(cf_mysql_name, 'mysql_passwd')


#从mysql中取出一条url的任务，并返回一个任务字典
def GetTask(id):
    task_dict = {}
    try:
        db = pymysql.connect(mysql_host, mysql_user, mysql_passwd, mysql_db, port=int(mysql_port), charset="utf8", connect_timeout=300)
        cursor = pymysql.cursors.SSCursor(db)
        select_sql = "SELECT task_id,type1,type2,type3,type4,type5,urls,rules_url,url_head" \
                     " FROM policy_spider_task_info WHERE task_id = %s LIMIT 1;"%id
        cursor.execute(select_sql)
        while True:
            row = cursor.fetchone()
            if not row:
                break
            task_id = row[0]
            type1 = row[1]
            type2 = row[2]
            type3 = row[3]
            type4 = row[4]
            type5 = row[5]
            urls = row[6]
            rules_url = row[7]
            url_head = row[8]
            task_dict["task_id"] = task_id
            task_dict["type1"] = type1
            task_dict["type2"] = type2
            task_dict["type3"] = type3
            task_dict["type4"] = type4
            task_dict["type5"] = type5
            task_dict["urls"] = urls
            task_dict["url_head"] = url_head
            task_dict["rules_url"] = rules_url
        #取出任务后，将认为状态更新为已完成
        update_sql = "UPDATE policy_spider_task_info SET state = 1 WHERE task_id = %s;"%task_id
        cursor.execute(update_sql)
        db.commit()
        cursor.close()
        db.close()
    except Exception as e:
        print(e)
    return task_dict

# 将获取的任务写入配置文件中，覆盖任务文件中原来的任务
# 然后启动爬虫一，获取具体的二级url，并压入redis
def Run(id):
    task_dict = GetTask(id)
    if len(task_dict) > 0:
        f = open('./spiders/config.ini', 'w', encoding='utf-8')
        task_id = task_dict["task_id"]
        type1 = task_dict["type1"]
        type2 = task_dict["type2"]
        type3 = task_dict["type3"]
        type4 = task_dict["type4"]
        type5 = task_dict["type5"]

        url = task_dict["urls"]
        url_head = task_dict["url_head"]
        rules_url = task_dict["rules_url"]

        f.write("[1]\n")
        f.write("task_id = %s\n"%task_id)
        f.write("type1 = %s\n" % type1)
        f.write("type2 = %s\n" % type2)
        f.write("type3 = %s\n" % type3)
        f.write("type4 = %s\n" % type4)
        f.write("type5 = %s\n" % type5)

        f.write("urls = %s\n" % url)
        f.write("url_head = %s\n" % url_head)
        f.write("rules_url = %s\n" % rules_url)
        f.close()

        os.system("scrapy crawl PolicySpider1")


# 通过输入task_id作为参数的形式运行脚本，启动爬虫
if __name__ == "__main__":
    # if len(sys.argv) !=2:
    #     print("Error parameter!")
    # else:
    #     i = input("Input y and continue:")
    #     if i == "y":
    #         id=sys.argv[1]
    #         Run(id)
    #     else:
    #         print("exit！")
    id = sys.argv[1]
    Run(id)

