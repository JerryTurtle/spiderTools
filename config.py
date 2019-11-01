from urllib.parse import quote
import configparser

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


class Config(object):
    pass


class ProdConfig(Config):
    pass


class DevConfig(Config):
    DEBUG = True
    JSON_ADD_STATUS = True
    JSON_DATETIME_FORMAT = '%d/%m/%Y %H:%M:%S'
    JSON_STATUS_FIELD_NAME = 'status'
    # PASSWORD = quote('123456a?')
    CELERY_BROKER_URL = 'redis://:{}@120.79.147.1:6379/0'.format(quote('123456a?'))
    # CELERY_TASK_SERIALIZER = 'pickle'
    # CELERY_RESULT_SERIALIZER = 'pickle'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://' + mysql_user + ':' \
                              + mysql_password + '@' + mysql_host + ':' \
                              + mysql_port + '/' + mysql_db
