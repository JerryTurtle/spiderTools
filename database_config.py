# -*- coding: utf-8 -*-
import configparser


class DatabaseConfig(object):
    def __init__(self, mysql_name, mongodb_name, redis_name, config_path='DatabaseConfig.ini'):
        self.mysql_name = mysql_name
        self.mongodb_name = mongodb_name
        self.redis_name = redis_name
        self.cf = configparser.ConfigParser()
        self.cf.read(config_path, encoding='utf-8')

    def get_mysql_config(self):
        mysql_db = self.cf.get(self.mysql_name, 'mysql_db')
        mysql_host = self.cf.get(self.mysql_name, 'mysql_host')
        mysql_port = self.cf.get(self.mysql_name, 'mysql_port')
        mysql_user = self.cf.get(self.mysql_name, 'mysql_user')
        mysql_password = self.cf.get(self.mysql_name, 'mysql_password')
        mysql_config = dict(mysql_db=mysql_db, mysql_host=mysql_host,
                            mysql_port=mysql_port, mysql_user=mysql_user,
                            mysql_password=mysql_password)
        return mysql_config

    def get_mongo_config(self):
        mongo_host = self.cf.get(self.mongodb_name, 'mongo_host')
        mongo_port = self.cf.get(self.mongodb_name, 'mongo_port')
        mongo_db = self.cf.get(self.mongodb_name, 'mongo_db')
        mongo_table = self.cf.get(self.mongodb_name, 'mongo_table')
        mongo_user = self.cf.get(self.mongodb_name, 'mongo_user')
        mongo_password = self.cf.get(self.mongodb_name, 'mongo_password')
        mongo_config = dict(mongo_host=mongo_host, mongo_port=mongo_port,
                            mongo_db=mongo_db, mongo_table=mongo_table,
                            mongo_user=mongo_user, mongo_password=mongo_password)
        return mongo_config

    def get_redis_config(self):
        redis_db = self.cf.get(self.redis_name, 'redis_db')
        redis_host = self.cf.get(self.redis_name, 'redis_host')
        redis_port = self.cf.get(self.redis_name, 'redis_port')
        redis_password = self.cf.get(self.redis_name, 'redis_password')
        redis_config = dict(redis_db=redis_db, redis_host=redis_host,
                            redis_port=redis_port, redis_password=redis_password)
        return redis_config
