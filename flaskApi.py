"""
1.路由命名规范： 返回html页面的，全部以/html开头；
                返回json的接口，工具类以test开头、爬虫类以spider开头、其他的以PEP8为准
"""
from flask import Flask, render_template, redirect, url_for
from config import DevConfig
from flask_cors import CORS
import configparser
import pymongo
import redis
from selenium import webdriver
from lxml import etree
from flask import request
import json
import os
from celery import Celery
from urllib.parse import quote
from exts import db
from models import PolicySpiderUrlInfo, PolicySpiderTaskInfo, PolicyDataAnalysisRules, PolicySpiderDataInfo
import datetime
from flask_json import as_json, json_response
import requests
import time
import urllib
import re
import pymysql
app = Flask(__name__)
app.config.from_object(DevConfig)
db.init_app(app)
celery = Celery(app.name, broker=DevConfig.CELERY_BROKER_URL)


cf = configparser.ConfigParser()
# configparser 用以读写配置文件
cf.read('DatabaseConfig.ini', encoding='utf-8')

cf_mysql_name = "MYSQL_TEST"
# mysql
mysql_db = cf.get(cf_mysql_name, 'mysql_db')
mysql_host = cf.get(cf_mysql_name, 'mysql_host')
mysql_port = cf.get(cf_mysql_name, 'mysql_port')
mysql_user = cf.get(cf_mysql_name, 'mysql_user')
mysql_passwd = cf.get(cf_mysql_name, 'mysql_password')

# mongo
cf_mongo_name = "MONGODB_TEST"
mongo_host = cf.get(cf_mongo_name, 'mongo_host')
mongo_port = cf.get(cf_mongo_name, 'mongo_port')
mongo_db = cf.get(cf_mongo_name, 'mongo_db')
mongo_table = cf.get(cf_mongo_name, 'mongo_table')
mongo_user = cf.get(cf_mongo_name, 'mongo_user')
mongo_password = cf.get(cf_mongo_name, 'mongo_password')

cf_redis_name = "REDIS_TEST"
# redis
redis_db = cf.get(cf_redis_name, 'redis_db')
redis_host = cf.get(cf_redis_name, 'redis_host')
redis_port = cf.get(cf_redis_name, 'redis_port')
redis_password = cf.get(cf_redis_name, 'redis_password')
print(os.path.split(os.path.abspath('.'))[-1])


orderno = 'ZF20191080074lV0fOf'
secret = 'ac66770b075947eca6cb2f09dc776d00'


# 执行sql
def excute_sql(sql):
    mysql_conn = pymysql.connect(mysql_host, mysql_user, mysql_passwd, mysql_db, int(mysql_port), charset="utf8")
    mysql_cur = mysql_conn.cursor()
    mysql_cur.execute(sql)
    mysql_conn.commit()
    mysql_cur.close()
    mysql_conn.close()


# 代理ip,身份验证签名生成
def generate_proxy_auth():
    import hashlib
    import time
    timestamp = str(int(time.time()))
    string = 'orderno=' + orderno + ',' + 'secret=' + secret + ',' + 'timestamp=' + timestamp
    string = string.encode()
    md5_string = hashlib.md5(string).hexdigest()
    sign = md5_string.upper()
    auth = 'sign=' + sign + '&' + 'orderno=' + orderno + '&' + 'timestamp=' + timestamp
    return auth


# 使用chromeDriver获取网页内容
def get_content(list_url, extension, time_delay=5):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.get(list_url)
    time.sleep(int(time_delay))
    if extension is not None and extension != '':
        eval(extension)
    try:
        driver.switch_to.frame(0)
    except Exception as e:
        print(e)
    content = driver.page_source
    print(content)
    driver.close()
    return content


# 使用requests获取网页html数据
def get_content_request(list_url):
    auth = generate_proxy_auth()
    proxy = {'http': 'http://forward.xdaili.cn:80'}
    headers = {'Proxy-Authorization': auth,
               'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) '
                             'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36'}
    r = requests.get(list_url, headers=headers,
                     proxies=proxy, verify=False, allow_redirects=False)
    r.encoding = 'UTF-8'
    print(r.text)
    return r.text


# 提取数据测试接口
@app.route('/api/test/analysis_data', methods=['GET', 'POST'])
@as_json
def data_test():
    if request.method == 'POST':
        data = json.loads(request.get_data())
        url = data['url']
        rule_type = int(data['rule_type'])
        rule = data['rule']
        html = get_content_request(url)
        page = etree.HTML(html)
        if rule_type == 2:
            result = page.xpath(rule)
        else:
            result = re.findall(html, rule)
        return json_response(result=result, msg='success')
    else:
        return json_response(status_=405, msg='fail', error_description='Wrong request method!')


# 爬虫阶段一，点击下一页测试工具
@app.route('/api/test/next_page', methods=['GET', 'POST'])
@as_json
def next_page_test():
    time_delay = 3
    if request.method == 'POST':
        data = json.loads(request.get_data())
        start_url = data['start_url']
        rule_type = int(data['rule_type'])
        rules_next_page = data['rules_next_page']
        extension = data['extension']
        if rule_type == 2:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            driver = webdriver.Chrome(chrome_options=chrome_options)
            driver.get(start_url)
            time.sleep(int(time_delay))
            if extension is not None and extension != '':
                eval(extension)
            try:
                driver.find_element_by_partial_link_text(rules_next_page).click()
                time.sleep(time_delay)
                return json_response(result=1, msg='success')
            except Exception as e:
                print(e)
                try:
                    driver.switch_to.frame(0)
                    driver.find_element_by_partial_link_text(rules_next_page).click()
                    return json_response(result=1, msg='success')
                except Exception as e:
                    print(e)
                    return json_response(result=0, msg='success')
                return json_response(result=0, msg='success')
            finally:
                driver.close()
        else:
            pass
    else:
        return json_response(status_=405, msg='fail', error_description='Wrong request method!')


# 提取数据测试接口
@app.route('/api/test/get_urls', methods=['GET', 'POST'])
@as_json
def urls_test():
    if request.method == 'POST':
        data = json.loads(request.get_data())
        url = data['url']
        rule_type = int(data['rule_type'])
        rule = data['rule']
        extension = data['extension']
        html = get_content(url,extension)
        page = etree.HTML(html)
        if rule_type == 2:
            result = page.xpath(rule)
        else:
            result = re.findall(html, rule)
        return json_response(result=[result], msg='success')
    else:
        return json_response(status_=405, msg='fail', error_description='Wrong request method!')


# 获取已经爬取的详情页url的数量
@app.route('/api/count/urls')
def get_detail_url_count():
    task_id = int(request.args.get('task_id') or 1)
    count = PolicySpiderUrlInfo.query.filter_by(task_id=task_id).count()
    return json_response(count=str(count))


def get_detail_url_count(task_id):
    # task_id = int(request.args.get('task_id') or 1)
    count = PolicySpiderUrlInfo.query.filter_by(task_id=task_id).count()
    return str(count)


# 删除某一task的所有的详情页url
@app.route('/api/delete/urls')
def del_detail_url():
    task_id = int(request.args.get('task_id') or 0)
    policy_spider_url_list = PolicySpiderUrlInfo.query.filter_by(task_id=task_id).all()
    for item in policy_spider_url_list:
        db.session.delete(item)
    db.session.commit()
    return json_response(msg='success')


# 删除mongo中的数据
@app.route('/api/delete/mongo')
def del_mongo_pages():
    task_id = int(request.args.get('task_id') or 0)
    mongo_client = pymongo.MongoClient(host=mongo_host, port=int(mongo_port))
    db_auth = mongo_client.admin
    db_auth.authenticate(mongo_user, mongo_password)
    mongo_db_ = mongo_client[mongo_db]
    mongo_table_ = mongo_db_[mongo_table]
    mongo_table_.remove({"task_id": task_id})
    mongo_client.close()
    return json_response(msg='success')


# 获取mongodb中已经采集的数据的数量
@app.route('/api/count/mongo')
def get_mongo_count():
    task_id = int(request.args.get('task_id') or 0)
    mongo_client = pymongo.MongoClient(host=mongo_host, port=int(mongo_port))
    db_auth = mongo_client.admin
    db_auth.authenticate(mongo_user, mongo_password)
    mongo_db_ = mongo_client[mongo_db]
    mongo_table_ = mongo_db_[mongo_table]
    mongo_row = mongo_table_.count({"task_id": task_id})
    mongo_client.close()
    return json_response(count=str(mongo_row))


def get_mongo_count(task_id):
    mongo_client = pymongo.MongoClient(host=mongo_host, port=int(mongo_port))
    db_auth = mongo_client.admin
    db_auth.authenticate(mongo_user, mongo_password)
    mongo_db_ = mongo_client[mongo_db]
    mongo_table_ = mongo_db_[mongo_table]
    mongo_row = mongo_table_.count({"task_id": task_id})
    mongo_client.close()
    return str(mongo_row)


# 获取redis中剩余的任务数量
@app.route('/api/count/redis')
def get_redis_count():
    task_id = int(request.args.get('task_id') or 0)
    r = redis.StrictRedis(host=redis_host, port=int(redis_port), db=int(redis_db), password=redis_password)
    length = r.llen(str(task_id))
    return json_response(count=str(length))


# 数据采集数量监控接口
@app.route('/api/monitor/data')
def monitor():
    task_id = int(request.args.get('task_id') or 0)
    mongo_count = get_mongo_count(task_id)
    url_count = get_detail_url_count(task_id)
    data_count = PolicySpiderDataInfo.query.filter_by(task_id=task_id).count()
    data = dict(mongo_count=int(mongo_count),
                url_count=int(url_count),
                data_count=int(data_count))
    return json_response(data=data, msg='success')


# 数据分析规则删除接口
@app.route('/api/delete/rule')
def delete_rule():
    id_ = int(request.args.get('id_') or 0)
    try:
        rule = PolicyDataAnalysisRules.query.filter_by(id_=id_).first()
        db.session.delete(rule)
        db.session.commit()
    except Exception as e:
        print(e)
        return json_response(msg='fail')
    return json_response(msg='success')


# 数据分析规则录入接口
@app.route('/api/add/rule', methods=['POST', 'GET'])
@as_json
def add_rule():
    if request.method == "POST":
        data = json.loads(request.get_data())
        rule_ = PolicyDataAnalysisRules()
        rule_.task_id = data['task_id']
        rule_.meaning = data['meaning']
        rule_.rule_name = data['rule_name']
        rule_.rule_type = data['rule_type']
        rule_.rule = data['rule']
        rule_.insert_time = datetime.datetime.now()
        try:
            db.session.add(rule_)
            db.session.commit()
        except Exception as e:
            print(e)
            return json_response(msg='fail', error_description=str(e))
        return json_response(msg='success')
    return json_response(status_=405, msg='fail', error_description='Wrong request method!')


# 爬虫类型选择接口
@app.route('/api/spider/choice', methods=['GET', 'POST'])
@as_json
def spider_choice():
    task_id = int(request.args.get('task_id') or 0)
    if request.method == 'POST':
        data = json.loads(request.get_data())
        policy_spider_task_info = PolicySpiderTaskInfo.query.filter_by(task_id=task_id).first()
        policy_spider_task_info.spider_type = int(data['spider_type'])
        if data['spider_type'] == '1':
            policy_spider_task_info.urls = data['urls']
        elif data['spider_type'] == '2':
            policy_spider_task_info.start_url = data['start_url']
            policy_spider_task_info.rules_next_page = data['rules_next_page']
            policy_spider_task_info.extension_1 = data['extension']
        else:
            policy_spider_task_info.ajax_url = data['ajax_url']
            policy_spider_task_info.ajax_data = data['ajax_data']
        policy_spider_task_info.rules_url = data['rules_url']
        policy_spider_task_info.url_head = data['url_head']
        db.session.add(policy_spider_task_info)
        db.session.commit()
        return json_response(msg='success')
    else:
        return json_response(status_=405, msg='fail', error_description='Wrong request method!')


# 改变爬虫状态（state）
# def change_task_state(task_id, state):
#     policy_spider_task_info = PolicySpiderTaskInfo.query.filter_by(task_id=task_id).first()
#     policy_spider_task_info.state = state
#     db.session.add(policy_spider_task_info)
#     db.session.commit()


def change_task_state(task_id, state):
    sql = "UPDATE policy_spider_task_info SET state = %s WHERE task_id = %s"%(state,task_id)
    excute_sql(sql)


# 爬虫一celery任务
@celery.task(name="celery_start_spider1")
def celery_start_spider1(task_id):
    if os.path.split(os.path.abspath('.'))[-1] == 'spiderTools':
        os.chdir("Spider1/DataSpiders/DataSpiders")
    print(os.path.dirname(__file__))
    os.system("python3 Spider1Run.py %s" % task_id)
    print(os.path.dirname(__file__))
    if os.path.split(os.path.abspath('.'))[-1] == 'DataSpiders':
        os.chdir("../")
        os.chdir("../")
        os.chdir("../")
    change_task_state(task_id, 3)


# 爬虫二（爬虫阶段二）celery任务
@celery.task(name="celery_start_spider2")
def celery_start_spider2(task_id):
    print(os.path.dirname(__file__))
    if os.path.split(os.path.abspath('.'))[-1] == 'spiderTools':
        os.chdir("Spider2/DataSpiders/DataSpiders")
    print(os.path.dirname(__file__))
    os.system("python3 Spider2Run.py %s" % task_id)
    if os.path.split(os.path.abspath('.'))[-1] == 'DataSpiders':
        os.chdir("../")
        os.chdir("../")
        os.chdir("../")
    change_task_state(task_id, 4)


# 爬虫二（爬虫阶段二）补充celery任务
@celery.task(name="celery_start_spider2_add")
def celery_start_spider2_add(task_id):
    print(os.path.dirname(__file__))
    if os.path.split(os.path.abspath('.'))[-1] == 'spiderTools':
        os.chdir("Spider2/DataSpiders/DataSpiders")
    print(os.path.dirname(__file__))
    os.system("python3 Spider2Run_add.py %s" % task_id)
    if os.path.split(os.path.abspath('.'))[-1] == 'DataSpiders':
        os.chdir("../")
        os.chdir("../")
        os.chdir("../")
    change_task_state(task_id, 4)


# 爬虫三（爬虫阶段一，使用点击下一页获取详情页url）celery任务
@celery.task(name='celery_start_spider3')
def celery_start_spider3(task_id, policy_spider_task_info):
    content_list = get_all_content(policy_spider_task_info)
    url_list = analysis_content(content_list=content_list, policy_spider_task_info=policy_spider_task_info)
    insert_url(policy_spider_task_info=policy_spider_task_info, url_list=url_list)
    change_task_state(task_id, 3)


# 数据解析celery任务
@celery.task(name="analysis_data")
def analysis_data(task_id):
    print(os.path.dirname(__file__))
    if os.path.split(os.path.abspath('.'))[-1] == 'spiderTools':
        os.chdir("data_analysis/")
    print(os.path.dirname(__file__))
    os.system("python3 DataAnalysis.py %s" % task_id)
    if os.path.split(os.path.abspath('.'))[-1] == 'data_analysis':
        os.chdir("../")
    change_task_state(task_id, 6)


# 爬虫阶段一启动接口
@app.route('/api/celery/spider1')
def start_spider1():
    task_id = int(request.args.get('task_id') or 0)
    policy_spider_task_info = PolicySpiderTaskInfo.query.filter_by(task_id=task_id).first()
    if policy_spider_task_info.state < 0:
        return json_response(msg='fail')
    if policy_spider_task_info.spider_type == 1:
        change_task_state(task_id, 1)
        with app.app_context():
            celery_start_spider1.delay(task_id)
        return json_response(msg='success', task_id=str(task_id))
    elif policy_spider_task_info.spider_type == 2:
        change_task_state(task_id, 1)
        policy_spider_task_info = PolicySpiderTaskInfo.query.filter_by(task_id=task_id).first()
        info_dict = dict(start_url=policy_spider_task_info.start_url,
                         task_id=policy_spider_task_info.task_id,
                         rules_next_page=policy_spider_task_info.rules_next_page,
                         url_head=policy_spider_task_info.url_head,
                         rules_url=policy_spider_task_info.rules_url,
                         type1=policy_spider_task_info.type1,
                         type2=policy_spider_task_info.type2,
                         type3=policy_spider_task_info.type3,
                         type4=policy_spider_task_info.type4,
                         type5=policy_spider_task_info.type5,
                         extension_1=policy_spider_task_info.extension_1)
        with app.app_context():
            celery_start_spider3.delay(task_id, info_dict)
        return json_response(msg='success', task_id=str(task_id))
    elif policy_spider_task_info.spider_type == 3:
        change_task_state(task_id, 1)
        with app.app_context():
            celery_start_spider1.delay(task_id)
        return json_response(msg='success', task_id=str(task_id))
    else:
        return json_response(msg='fail')


# 爬虫阶段二启动接口
@app.route('/api/celery/spider2')
def start_spider2():
    task_id = int(request.args.get('task_id') or 0)
    policy_spider_task_info = PolicySpiderTaskInfo.query.filter_by(task_id=task_id).first()
    if policy_spider_task_info.state < 0:
        return json_response(msg='fail')
    change_task_state(task_id, 2)
    with app.app_context():
        celery_start_spider2.delay(task_id)
    return json_response(msg='success', task_id=str(task_id))


# 爬虫阶段二补充采集接口
@app.route('/api/celery/spider2add')
def start_spider2_add():
    task_id = int(request.args.get('task_id') or 0)
    change_task_state(task_id, 2)
    with app.app_context():
        celery_start_spider2_add.delay(task_id)
    return str(task_id)


# 数据解析启动接口
@app.route('/api/celery/analysis')
def data_analysis():
    task_id = int(request.args.get('task_id') or 0)
    policy_spider_task_info = PolicySpiderTaskInfo.query.filter_by(task_id=task_id).first()
    if policy_spider_task_info.state < 4:
        return json_response(msg='fail')
    change_task_state(task_id, 5)
    with app.app_context():
        analysis_data.delay(task_id)
    return json_response(msg='success', task_id=str(task_id))


# # 查询数据采集规则的接口
# @app.route('/api/show/rules')
# def show_rules():
#     task_id = int(request.args.get('task_id') or 0)
#     rules_info = PolicySpiderTaskInfo.query.filter_by(task_id=task_id).first()
#     data = dict(
#         rules_organization=rules_info.rules_organization,
#         rules_subject=rules_info.rules_subject,
#         rules_keywords=rules_info.rules_keywords,
#         rules_file_number=rules_info.rules_file_number,
#         rules_create_date=rules_info.rules_create_date,
#         rules_release_date=rules_info.rules_release_date,
#         rules_enforcement_date=rules_info.rules_enforcement_date,
#         rules_index_number=rules_info.rules_index_number,
#         rules_author=rules_info.rules_author)
#     return json_response(data=data)


# spider3的爬虫第一阶段
# 因为celery序列化的限制，不能传递自定义的类， 传递转化后的字典
def get_all_content(policy_spider_task_url, time_delay=5):
    start_url = policy_spider_task_url['start_url']
    rules_next_page = policy_spider_task_url['rules_next_page']
    extension_1 = policy_spider_task_url['extension_1']
    content_list = []
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.get(start_url)
    time.sleep(int(time_delay))
    try:
        while True:
            if extension_1 is not None and extension_1 != '':
                eval(extension_1)
            content = driver.page_source
            content_list.append(content)
            driver.find_element_by_partial_link_text(rules_next_page).click()
            time.sleep(int(time_delay))
    except Exception as e:
        print(e)
    finally:
        driver.close()
    return content_list


# 分析抓取到的html代码
def analysis_content(content_list, policy_spider_task_info):
    url_list = []
    url_head = policy_spider_task_info['url_head']
    rules_url = policy_spider_task_info['rules_url']
    for content in content_list:
        page = etree.HTML(content)
        url_list = url_list + page.xpath(rules_url)
    if url_head != '' or url_head is not None:
        for i in range(0, len(url_list)):
            url_list[i] = urllib.parse.urljoin(url_head, url_list[i])
    return url_list


# 将解析出的url插入数据库
def insert_url(policy_spider_task_info, url_list):
    task_id = policy_spider_task_info['task_id']
    type1 = policy_spider_task_info['type1']
    type2 = policy_spider_task_info['type2']
    type3 = policy_spider_task_info['type3']
    type4 = policy_spider_task_info['type4']
    type5 = policy_spider_task_info['type5']
    from_url = ''
    for url in url_list:
        policy_spider_url_info = PolicySpiderUrlInfo()
        policy_spider_url_info.task_id = task_id
        policy_spider_url_info.url = url
        policy_spider_url_info.type1 = type1
        policy_spider_url_info.type2 = type2
        policy_spider_url_info.type3 = type3
        policy_spider_url_info.type4 = type4
        policy_spider_url_info.type5 = type5
        policy_spider_url_info.from_url = from_url
        policy_spider_url_info.insert_time = datetime.datetime.now()
        with app.app_context():
            db.session.add(policy_spider_url_info)
            db.session.commit()


@app.route('/')
def index():
    return redirect(url_for("index_html"))


# 主页
@app.route('/index')
def index_html():
    page = int(request.args.get('page') or 1)
    page_obj = PolicySpiderTaskInfo.query.paginate(page, 10)
    return render_template('index.html', pagination=page_obj)


# 工具选择页面
@app.route('/tools')
def spider_tools():
    return render_template('tools.html')


# 数据查询工具
@app.route('/tools/sql')
def tools_sql_html():
    return render_template("tools_sql.html")


# 数据分析规则测试工具页面
@app.route('/tools/data/test')
def test_data_html():
    return render_template("tools_data_test.html")


# 爬虫阶段一获取urls测试页面
@app.route('/tools/urls/test')
def test_urls_html():
    return render_template("tools_urls_test.html")


# 爬虫阶段一获取urls测试页面
@app.route('/tools/next/test')
def test_next_html():
    return render_template("tools_next_page_test.html")


# 爬虫启动工具
@app.route('/tools/spider/start')
def start_spider1_html():
    return render_template("tools_spider_start.html")


# 详情页url查询工具
@app.route('/tools/show/urls')
def show_urls_tools():
    return render_template("tools_show_urls.html")


# 任务监控页面
@app.route('/tools/monitor/task')
def monitor_task_tools():
    page_obj = PolicySpiderTaskInfo.query.filter_by(type2="组成部门").all()
    page_obj = {"data": page_obj}
    return render_template("tools_monitor.html", pageObj=page_obj)


# 爬虫启动规则配置页面
@app.route('/spider/choice')
def spider_choice_html():
    task_id = int(request.args.get('task_id') or 0)
    policy_spider_task_info = PolicySpiderTaskInfo.query.filter_by(task_id=task_id).first()
    return render_template('spider_choice.html', psti=policy_spider_task_info)


# 爬虫启动页面
@app.route('/spider/start')
def start_spider_html():
    task_id = int(request.args.get('task_id') or 0)
    return render_template('spider_start.html', task_id=task_id)


# 已采集详情页url页面
@app.route('/show/urls')
def get_detail_urls():
    task_id = int(request.args.get('task_id') or 0)
    # 传递的页码数量
    page = int(request.args.get('page') or 1)
    # 页码page，每页显示10条
    count = PolicySpiderUrlInfo.query.filter_by(task_id=task_id).count()
    page_obj = PolicySpiderUrlInfo.query.filter_by(task_id=task_id).paginate(page, 10)
    return render_template('show_urls.html',
                           pagination=page_obj, task_id=task_id, count=count)


# 数据分析规则录入页面
@app.route('/show/analysis/rules')
def get_rules():
    task_id = int(request.args.get('task_id') or 1)
    rules_info = PolicyDataAnalysisRules.query.filter_by(task_id=task_id).all()
    return render_template('show_analysis_rules.html', data=rules_info, task_id=task_id)


@app.route('/tools/generate/urls')
def generate_urls():
    return render_template('tools_generate_urls.html')


if __name__ == '__main__':
    CORS(app, supports_credentials=True)
    app.run(host='0.0.0.0', port=5000)
