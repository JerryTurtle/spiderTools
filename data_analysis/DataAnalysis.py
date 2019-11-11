# -*- coding: utf-8 -*-
import pymongo
from lxml import etree
from jparser import PageModel
import datetime
import configparser

# from ..z.database_config import DatabaseConfig
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from sqlalchemy import Column, String, Integer, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
import sys
Model = declarative_base()


class PolicySpiderUrlInfo(Model):
    __tablename__ = 'policy_spider_url_info'

    id_ = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    task_id = Column(Integer)
    type1 = Column(String(64))
    type2 = Column(String(64))
    type3 = Column(String(64))
    type4 = Column(String(64))
    type5 = Column(String(64))
    url = Column(Text)
    insert_time = Column(DateTime)
    from_url = Column(String(255))

    def __init__(self, task_id, type1, type2, type3, type4, type5):
        self.task_id = task_id
        self.type1 = type1
        self.type2 = type2
        self.type3 = type3
        self.type4 = type4
        self.type5 = type5

    def __repr__(self):
        return '<PolicySpiderUrlInfo %r>' % self.task_id


class PolicySpiderTaskInfo(Model):
    __tablename__ = 'policy_spider_task_info'
    id_ = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    task_id = Column(Integer)
    state = Column(Integer)
    type1 = Column(String(64))
    type2 = Column(String(64))
    type3 = Column(String(64))
    type4 = Column(String(64))
    type5 = Column(String(64))

    rules_organization = Column(String(512))
    rules_subject = Column(String(512))
    rules_keywords = Column(String(512))
    rules_file_number = Column(String(512))
    rules_create_date = Column(String(512))
    rules_release_date = Column(String(512))
    rules_enforcement_date = Column(String(512))
    rules_invalid_date = Column(String(512))
    rules_index_number = Column(String(512))
    rules_author = Column(String(512))

    urls = Column(Text)
    insert_time = Column(DateTime)

    def __init__(self, task_id, type1, type2, type3, type4, type5):
        self.task_id = task_id
        self.type1 = type1
        self.type2 = type2
        self.type3 = type3
        self.type4 = type4
        self.type5 = type5

    def __repr__(self):
        return '<PolicySpiderTaskInfo %r>' % self.task_id


class PolicySpiderDataInfo(Model):
    __tablename__ = 'policy_spider_data_info'
    id_ = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    task_id = Column(Integer)
    type1 = Column(String(64))
    type2 = Column(String(64))
    type3 = Column(String(64))
    type4 = Column(String(64))
    type5 = Column(String(64))

    title = Column(String(1024))
    content = Column(Text)
    author = Column(String(1024))
    organization = Column(String(1024))
    subject = Column(String(1024))
    keywords = Column(String(1024))
    file_number = Column(String(1024))
    create_date = Column(String(1024))
    release_date = Column(String(1024))
    enforcement_date = Column(String(1024))
    invalid_date = Column(String(1024))
    index_number = Column(String(1024))

    image_path = Column(String(1024))
    attachment = Column(String(1024))

    url = Column(Text)
    insert_time = Column(DateTime)

    def __repr__(self):
        return '<PolicySpiderDataInfo %r>' % self.task_id


class PolicyDataAnalysisRules(Model):
    __tablename__ = 'policy_data_analysis_rules'
    id_ = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    task_id = Column(Integer)
    meaning = Column(String(512))
    rule_name = Column(String(512))
    rule_type = Column(String(512))
    rule = Column(String(512))
    insert_time = Column(DateTime)

    def __repr__(self):
        return '<PolicyDataAnalysisRules %r>' % self.rule


result_dic = dict(rules_organization='',
                  rules_subject='',
                  rules_keywords='',
                  rules_file_number='',
                  rules_create_date='',
                  rules_release_date='',
                  rules_enforcement_date='',
                  rules_invalid_date='',
                  rules_index_number='',
                  rules_author='')


class DataAnalysis(object):

    def __init__(self):
        dc = DatabaseConfig(mysql_name='MYSQL_TEST',
                            mongodb_name='MONGODB_TEST',
                            redis_name='REDIS_TEST')
        self.mysql_config = dc.get_mysql_config()
        self.mongodb_config = dc.get_mongo_config()
        self.redis_config = dc.get_redis_config()
        # 初始化数据库连接:
        mysql_string = 'mysql+pymysql://' + \
                       self.mysql_config['mysql_user'] + ':' + \
                       self.mysql_config['mysql_password'] + '@' + \
                       self.mysql_config['mysql_host'] + ':' + \
                       self.mysql_config['mysql_port'] + '/' + \
                       self.mysql_config['mysql_db']+'?charset=utf8'
        engine = create_engine(mysql_string, pool_size=5, pool_recycle=1800)
        # 创建DBSession类型:
        self.DBSession = sessionmaker(bind=engine)

    def test_add(self):
        # 创建session对象:
        session = self.DBSession()
        # 创建新User对象:
        import datetime
        new_user = PolicySpiderDataInfo(task_id=66666, url='66666', insert_time=datetime.datetime.now())
        # 添加到session:
        session.add(new_user)
        # 提交即保存到数据库:
        session.commit()
        # 关闭session:
        session.close()

    def test_select(self):
        session = self.DBSession()
        pd = session.query(PolicySpiderDataInfo).filter_by(task_id=2).first()
        session.close()
        print(pd.content)

    def get_rules(self, task_id):
        session = self.DBSession()
        policy_spider_data_info = \
            session.query(PolicySpiderTaskInfo).filter_by(task_id=task_id).first()
        session.close()
        return policy_spider_data_info

    # 分析html，返回文章标题与内容
    @staticmethod
    def content_extraction(html):
        try:
            pm = PageModel(html)
            result = pm.extract()
            title = result['title']
            content = ''
            for x in result['content']:
                if x['type'] == 'text':
                    content = '%s%s%s' % (content, x['data'], '\n')
            result = {}.fromkeys(("title", "content"))
            result["title"] = title
            result["content"] = content
            return result
        except Exception as e:
            print(e)
            return {"title": "", "content": ""}

    # 使用多个规则分析提取所需字段，选择提取出的长度最长的返回
    @staticmethod
    def get_info(page1, rules):
        if rules == '':
            return ''
        rules_list = rules.split(';')
        result_list = []
        for rule in rules_list:
            try:
                para = page1.xpath(rule)[0]
                result_list.append(para)
            except Exception as e:
                print(e)
                result_list.append('')
        if len(result_list) == 0:
            return ''
        result_list.sort(key=lambda i: len(i), reverse=True)
        return result_list[0]

    def select_mongo(self, task_id):
        rules = self.get_rules(task_id)
        mongo_conn = pymongo.MongoClient(self.mongodb_config['mongo_host'],
                                         int(self.mongodb_config['mongo_port']))
        mongo_db_auth = mongo_conn.admin
        mongo_db_auth.authenticate(self.mongodb_config['mongo_user'],
                                   self.mongodb_config['mongo_password'])
        mongo_db = mongo_conn[self.mongodb_config['mongo_db']]
        mongo_table = mongo_db[self.mongodb_config['mongo_table']]
        mongo_cursor = mongo_table.find({"task_id": int(task_id)})
        print(mongo_cursor.count())

        mysql_session = self.DBSession()
        for item in mongo_cursor:
            policy_spider_data_info = PolicySpiderDataInfo()
            policy_spider_data_info.task_id = item["task_id"]
            policy_spider_data_info.url = item["url"]
            policy_spider_data_info.type1 = item["type1"]
            policy_spider_data_info.type2 = item["type2"]
            policy_spider_data_info.type3 = item["type3"]
            policy_spider_data_info.type4 = item["type4"]
            policy_spider_data_info.type5 = item["type5"]
            html = item["html"]
            page = etree.HTML(html)
            c = DataAnalysis.content_extraction(html)
            policy_spider_data_info.title = c["title"]
            policy_spider_data_info.content = c["content"]
            # noinspection PyArgumentList
            policy_spider_data_info.index_number = \
                DataAnalysis.get_info(page, rules.rules_index_number)
            # noinspection PyArgumentList
            policy_spider_data_info.organization = \
                DataAnalysis.get_info(page, rules.rules_organization)
            # noinspection PyArgumentList
            policy_spider_data_info.file_number = \
                DataAnalysis.get_info(page, rules.rules_file_number)
            # noinspection PyArgumentList
            policy_spider_data_info.keywords = \
                DataAnalysis.get_info(page, rules.rules_keywords)
            # noinspection PyArgumentList
            policy_spider_data_info.subject = \
                DataAnalysis.get_info(page, rules.rules_subject)
            # noinspection PyArgumentList
            policy_spider_data_info.create_date = \
                DataAnalysis.get_info(page, rules.rules_create_date)
            # noinspection PyArgumentList
            policy_spider_data_info.release_date = \
                DataAnalysis.get_info(page, rules.rules_release_date)
            # noinspection PyArgumentList
            policy_spider_data_info.enforcement_date = \
                DataAnalysis.get_info(page, rules.rules_enforcement_date)
            # noinspection PyArgumentList
            policy_spider_data_info.invalid_data = \
                DataAnalysis.get_info(page, rules.rules_invalid_date)
            # noinspection PyArgumentList
            policy_spider_data_info.author = \
                DataAnalysis.get_info(page, rules.rules_author)
            # index_number,organization,file_number,keywords,subject,create_date,release_date,enforcement_date,invalid_data,author
            policy_spider_data_info.insert_time = datetime.datetime.now()
            mysql_session.add(policy_spider_data_info)
            mysql_session.commit()
        mysql_session.close()

    def read_rules(self, task_id):
        session = self.DBSession()
        policy_data_analysis_rules = session.query(PolicyDataAnalysisRules).filter_by(task_id=task_id).all()
        print(policy_data_analysis_rules)
        session.close()
        return policy_data_analysis_rules

    @staticmethod
    def get_info_xpath(page, rule_xpath):
        rule_xpath = rule_xpath.strip()
        if rule_xpath == '':
            return ''
        try:
            info = page.xpath(rule_xpath)[0]
        except Exception as e:
            print(e)
            info = ''
        return info

    def read_excel(self):
        import xlrd
        file = '部委数据主题标识1023.xlsx'
        wb = xlrd.open_workbook(filename=file)  # 打开文件
        sheet1 = wb.sheet_by_index(0)  # 通过索引获取表格
        session = self.DBSession()
        for i in range(1, 5107):
            id_ = int(sheet1.row(i)[0].value)
            subject = sheet1.row(i)[5].value
            pda = session.query(PolicySpiderDataInfo).filter_by(id_=id_).first()
            pda.subject = subject
            session.add(pda)
            session.commit()
        session.close()

    def count_image_attachment(self):
        pass

    def select_mongo_(self, task_id):
        rules = self.get_rules(task_id)
        mongo_conn = pymongo.MongoClient(self.mongodb_config['mongo_host'],
                                         int(self.mongodb_config['mongo_port']))
        mongo_db_auth = mongo_conn.admin
        mongo_db_auth.authenticate(self.mongodb_config['mongo_user'],
                                   self.mongodb_config['mongo_password'])
        mongo_db = mongo_conn[self.mongodb_config['mongo_db']]
        mongo_table = mongo_db[self.mongodb_config['mongo_table']]
        mongo_cursor = mongo_table.find({"task_id": int(task_id)})
        print(mongo_cursor.count())
        rules_list = self.read_rules(task_id=task_id)
        mysql_session = self.DBSession()
        for item in mongo_cursor:
            policy_spider_data_info = PolicySpiderDataInfo()
            policy_spider_data_info.task_id = item["task_id"]
            policy_spider_data_info.url = item["url"]
            policy_spider_data_info.type1 = item["type1"]
            policy_spider_data_info.type2 = item["type2"]
            policy_spider_data_info.type3 = item["type3"]
            policy_spider_data_info.type4 = item["type4"]
            policy_spider_data_info.type5 = item["type5"]
            html = item["html"]
            page = etree.HTML(html)
            c = DataAnalysis.content_extraction(html)
            policy_spider_data_info.title = c["title"]
            policy_spider_data_info.content = c["content"]
            result_dictionary = dict(rules_organization='',
                                     rules_subject='',
                                     rules_keywords='',
                                     rules_file_number='',
                                     rules_create_date='',
                                     rules_release_date='',
                                     rules_enforcement_date='',
                                     rules_invalid_date='',
                                     rules_index_number='',
                                     rules_author='')
            for rule in rules_list:
                result_dictionary[rule.rule_name] = \
                    self.get_info_xpath(page=page, rule_xpath=rule.rule)
            policy_spider_data_info.index_number = result_dictionary['rules_index_number']
            policy_spider_data_info.organization = result_dictionary['rules_organization']
            policy_spider_data_info.file_number = result_dictionary['rules_file_number']
            policy_spider_data_info.keywords = result_dictionary['rules_keywords']
            policy_spider_data_info.subject = result_dictionary['rules_subject']
            policy_spider_data_info.create_date = result_dictionary['rules_create_date']
            policy_spider_data_info.release_date = result_dictionary['rules_release_date']
            policy_spider_data_info.enforcement_date = result_dictionary['rules_enforcement_date']
            policy_spider_data_info.invalid_date = result_dictionary['rules_invalid_date']
            policy_spider_data_info.author = result_dictionary['rules_author']

            # index_number,organization,file_number,keywords,subject,create_date,release_date,enforcement_date,invalid_data,author
            policy_spider_data_info.insert_time = datetime.datetime.now()
            mysql_session.add(policy_spider_data_info)
            mysql_session.commit()
        mysql_session.close()


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


if __name__ == "__main__":
    t = DataAnalysis()
    task_id = sys.argv[1]
    t.select_mongo_(task_id=task_id)
