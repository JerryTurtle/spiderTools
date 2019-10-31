from flask import Flask,render_template,redirect,url_for
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
from flask_sqlalchemy import SQLAlchemy
from exts import db
from models import PolicySpiderUrlInfo, PolicySpiderTaskInfo, PolicyDataAnalysisRules, PolicySpiderDataInfo
import pymysql
import datetime
from flask_json import as_json, FlaskJSON
import requests
import time
import urllib
app = Flask(__name__)
app.config.from_object(DevConfig)

celery = Celery(app.name, broker=DevConfig.CELERY_BROKER_URL)
db.init_app(app)
# flask_json = FlaskJSON(app)
app.config['JSON_ADD_STATUS'] = True
app.config['JSON_DATETIME_FORMAT'] = '%d/%m/%Y %H:%M:%S'
app.config['JSON_STATUS_FIELD_NAME'] = 'FAILED'
# app.config['CELERY_TASK_SERIALIZER'] = 'pickle'
# app.config['CELERY_RESULT_SERIALIZER'] = 'pickle'
# app.config['CELERY_ACCEPT_CONTENT'] = ['pickle']
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
mongo_passwd = cf.get(cf_mongo_name, 'mongo_password')

cf_redis_name = "REDIS_TEST"
# mysql
redis_db = cf.get(cf_redis_name, 'redis_db')
redis_host = cf.get(cf_redis_name, 'redis_host')
redis_port = cf.get(cf_redis_name, 'redis_port')
# mysql_user = cf.get(cf_redis_name, 'mysql_user')
redis_passwd = cf.get(cf_redis_name, 'redis_password')
print(os.path.split(os.path.abspath('.'))[-1])


success_json = {'msg':1}
failed_json = {'msg':0}

def generate_proxy_auth():
    import hashlib
    import time
    orderno = "ZF20191080074lV0fOf"
    secret = "ac66770b075947eca6cb2f09dc776d00"
    ip = "forward.xdaili.cn"
    port = "80"
    ip_port = ip + ":" + port
    timestamp = str(int(time.time()))
    string = ""
    string = "orderno=" + orderno + "," + "secret=" + secret + "," + "timestamp=" + timestamp
    string = string.encode()
    md5_string = hashlib.md5(string).hexdigest()
    sign = md5_string.upper()
    auth = "sign=" + sign + "&" + "orderno=" + orderno + "&" + "timestamp=" + timestamp
    return auth


#获取网页内容
def get_content(list_url):
    import time
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.get(list_url)
    # driver.find_element_by_xpath('//*[@id="13739"]/table/tbody/tr/td/table/tbody/tr/td[8]/div').click()
    # driver.maximize_window();# 窗口最大化
    # 执行js滚动浏览器窗口到底部
    # driver.execute_script(js)
    # time.sleep(5)  # 不加载图片的话，这个时间可以不要，等待JS执行
    time.sleep(2)
    content = driver.page_source
    # driver.quit()
    driver.close()
    print(content)
    # return None
    return content


def get_content_request(list_url):
    auth = generate_proxy_auth()
    proxy = {"http": 'http://forward.xdaili.cn:80'}
    headers = {"Proxy-Authorization": auth,
               "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) "
                             "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36"}
    r = requests.get(list_url, headers=headers,
                     proxies=proxy, verify=False, allow_redirects=False)
    r.encoding = 'UTF-8'
    # print(r.text)
    return r.text


@app.route('/data/test/',methods=['GET', 'POST'])
def data_test():
    if request.method == 'POST':
        data = json.loads(request.get_data())
        url = data['url']
        rule_type = int(data['rule_type'])
        rule = data['rule']
        html = get_content_request(url)
        page = etree.HTML(html)
        if(rule_type==1):
            result = page.xpath(rule)[0]
            return str(result)


# 获取字段
def get_content_detail(xpath_dic,content):
    #结果字典
    result_dic = {}
    #获取url列表，并去除列表中空项
    temp = etree.HTML(content)
    #href_list = page.xpath(xpath_detail_url)
    for k in xpath_dic:
        try:
            result_dic[k] = str(temp.xpath(xpath_dic[k])[0])
        except:
            result_dic[k] = ""
    return result_dic



#执行sql
def excute_select_sql(sql):
    mysql_conn = pymysql.connect(mysql_host, mysql_user, mysql_passwd, mysql_db, int(mysql_port), charset="utf8")
    mysql_cur = mysql_conn.cursor()
    mysql_cur.execute(sql)
    try:
        row = mysql_cur.fetchone()
        data = row[0]
    except:
        return '0'
    #print(row[0])
    mysql_cur.close()
    mysql_conn.close()
    return data


#执行sql
def excute_delete_sql(sql):
    mysql_conn = pymysql.connect(mysql_host, mysql_user, mysql_passwd, mysql_db, int(mysql_port), charset="utf8")
    mysql_cur = mysql_conn.cursor()
    mysql_cur.execute(sql)
    mysql_conn.commit()
    mysql_cur.close()
    mysql_conn.close()
    return ''
#获取已经爬取的详情页url的数量
@app.route('/count/detailurl/<int:task_id>')
def get_detail_url_count(task_id):
    sql = 'SELECT COUNT(*) FROM policy_spider_url_info WHERE task_id = %s'%task_id
    count = excute_select_sql(sql)
    return str(count)


@app.route('/get/taskurl/<int:task_id>')
def get_task_url(task_id):
    sql = 'SELECT url FROM policy_spider_task_info WHERE task_id = %s'%task_id
    url = excute_select_sql(sql)
    url_list = url.split(';')
    return str(url_list[0])



#删除某一task的所有的详情页url
@app.route('/delete/detailurl/<int:task_id>')
def del_detail_url(task_id):
    sql = 'DELETE FROM policy_spider_url_info WHERE task_id = %s'%task_id
    url = excute_delete_sql(sql)
    return str(url)

# 获取mongodb中已经采集的数据的数量
@app.route('/get/mongocount/<int:task_id>')
def get_mongo_count(task_id):
    mongo_client = pymongo.MongoClient(host=mongo_host, port=int(mongo_port))
    db_auth = mongo_client.admin
    db_auth.authenticate(mongo_user, mongo_passwd)
    mongo_db_ = mongo_client[mongo_db]
    mongo_table_ = mongo_db_[mongo_table]
    mongo_row = mongo_table_.count({"task_id":task_id})
    mongo_client.close()
    return str(mongo_row)


#获取redis中剩余的任务数量
@app.route('/get/rediscount')
def get_redis_count():
    r = redis.StrictRedis(host=redis_host, port=int(redis_port), db=int(redis_db), password=redis_passwd)
    len = r.llen("url_zhangye")
    return str(len)


@app.route('/monitor/<int:task_id>')
def monitor(task_id):
    mongo_count = get_mongo_count(task_id)
    url_count = get_detail_url_count(task_id)
    data_count = PolicySpiderDataInfo.query.filter_by(task_id = task_id).count()
    data = dict(mongo_count=int(mongo_count),
                url_count=int(url_count),
                data_count=int(data_count))
    return json.dumps(data)


@app.route('/spider/start/<int:task_id>')
def start_spider_html(task_id):
    return render_template('spider_start.html',task_id=task_id)


# 获取redis中剩余的任务数量
@app.route('/test/xpathcontent',methods=['POST', 'GET'])
def test_xpath_content():
    if request.method == "POST":
        data = json.loads(request.get_data())
        print(data)
        html = get_content_request(data['detail_URI'])
        try:
            data.pop("detail_URI")
        except:
            pass
        result = get_content_detail(data,html)
        print(result)
        return json.dumps(result)


@app.route('/tools')
def spider_tools():
    return render_template('index.html')

@app.route('/')
def home():
    #print(post_id)
    return redirect(url_for("index_html"))

@app.route('/index')
def index_html():
    #task_id = int(request.args.get('taskid') or 1)
    # 传递的页码数量
    page = int(request.args.get('page') or 1)
    # goodslist = Goods.query.all()
    # 页码page，每页显示10条
    pageObj = PolicySpiderTaskInfo.query.paginate(page, 10)

    return render_template('index_1.html', pagination=pageObj)
    #print(post_id)
    #return render_template("index.html")

@app.route('/tools/monitortask')
def monitor_task_tools():
    pageObj = PolicySpiderTaskInfo.query.filter_by(type2 = "组成部门").all()
    pageObj = {"data":pageObj}
    #print(pageObj)
    return render_template("monitor_tools.html",pageObj = pageObj )


@app.route('/mysql/show/urls/')
def get_detail_urls():
    task_id = int(request.args.get('taskid') or 1)
    # 传递的页码数量
    page = int(request.args.get('page') or 1)
    # goodslist = Goods.query.all()
    # 页码page，每页显示10条
    count = PolicySpiderUrlInfo.query.filter_by(task_id=task_id).count()
    pageObj = PolicySpiderUrlInfo.query.filter_by(task_id=task_id).paginate(page, 10)

    return render_template('show_urls.html',
                           pagination=pageObj, task_id=task_id, count = count)


# @app.route('/mysql/show/rules/')
# def get_rules():
#     task_id = int(request.args.get('taskid') or 1)
#     rules_info = PolicySpiderTaskInfo.query.filter_by(task_id=task_id).first()
#     # rules_organization = rules_info.rules_organization.split(';')
#     # rules_subject = rules_info.rules_subject.split(';')
#     # rules_keywords = rules_info.rules_keywords.split(';')
#     # rules_file_number = rules_info.rules_file_number.split(';')
#     # rules_create_date = rules_info.rules_create_date.split(';')
#     # rules_release_date = rules_info.rules_release_date.split(';')
#     # rules_enforcement_date = rules_info.rules_enforcement_date.split(';')
#     # rules_index_number = rules_info.rules_index_number.split(';')
#     # rules_author = rules_info.rules_author.split(';')
#     data = dict(
#         rules_organization=rules_info.rules_organization.split(';'),
#         rules_subject=rules_info.rules_subject.split(';'),
#         rules_keywords=rules_info.rules_keywords.split(';'),
#         rules_file_number=rules_info.rules_file_number.split(';'),
#         rules_create_date=rules_info.rules_create_date.split(';'),
#         rules_release_date=rules_info.rules_release_date.split(';'),
#         rules_enforcement_date=rules_info.rules_enforcement_date.split(';'),
#         rules_index_number=rules_info.rules_index_number.split(';'),
#         rules_author=rules_info.rules_author.split(';'))
#     for k in data:
#         if data[k] == ['']:
#             data[k] = None
#     return render_template('show_analysis_rules.html', **data)

@app.route('/mysql/show/rules/')
def get_rules():
    task_id = int(request.args.get('taskid') or 1)
    rules_info = PolicyDataAnalysisRules.query.filter_by(task_id=task_id).all()
    return render_template('show_analysis_rules.html', data = rules_info,task_id = task_id)

@app.route('/mysql/delete/rule/<int:id_>')
def delete_rule(id_):
    try:
        rule = PolicyDataAnalysisRules.query.filter_by(id_=id_).first()
        db.session.delete(rule)
        db.session.commit()
    except Exception as e:
        print(e)
        return 'FAILED'
    return 'SUCCESS'

@app.route('/mysql/add/rule/', methods=['POST', 'GET'])
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
            return failed_json
        return success_json


@app.route('/spider/<int:task_id>')
def spider_choice_html(task_id):
    psti = PolicySpiderTaskInfo.query.filter_by(task_id=task_id).first()
    return render_template('spider_choice.html', psti=psti)


@app.route('/spider/choice/<int:task_id>',methods=['GET','POST'])
@as_json
def spider_choice(task_id):
    if request.method == 'POST':
        data = json.loads(request.get_data())
        psti = PolicySpiderTaskInfo.query.filter_by(task_id = task_id).first()
        psti.spider_type = int(data['spider_type'])
        if data['spider_type'] == '1':
            psti.urls = data['urls']
        elif data['spider_type'] == '2':
            psti.start_url = data['start_url']
            psti.rules_next_page = data['rules_next_page']
        else:
            psti.ajax_url = data['ajax_url']
            psti.ajax_data = data['ajax_data']
        psti.rules_url = data['rules_url']
        psti.url_head = data['url_head']
        db.session.add(psti)
        db.session.commit()
        return success_json


@app.route('/sqltools')
def sqltools_html():
    #print(post_id)
    return render_template("sql_tools.html")


@app.route('/datatest')
def datatest_html():
    #print(post_id)
    return render_template("data_test_tools.html")

@app.route('/startspider1')
def start_spider1_html():
    #print(post_id)
    return render_template("start_spider1_tools.html")


def change_task_state(task_id,state):
    sql = "UPDATE policy_spider_task_info SET state = %s WHERE task_id = %s"%(state,task_id)
    excute_delete_sql(sql)

@celery.task(name="celery_start_spider1")
def celery_start_spider1(task_id):
    if os.path.split(os.path.abspath('.'))[-1] == 'spiderTools':
        os.chdir("Spider1/DataSpiders/DataSpiders")
    print(os.path.dirname(__file__))
    # os.chdir("Spider1/DataSpiders/DataSpiders")
    os.system("python3 Spider1Run.py %s" % task_id)
    change_task_state(task_id, 3)
    if os.path.split(os.path.abspath('.'))[-1] == 'DataSpiders':
        os.chdir("../")
        os.chdir("../")
        os.chdir("../")


@celery.task(name="celery_start_spider2")
def celery_start_spider2(task_id):
    print(os.path.dirname(__file__))
    if os.path.split(os.path.abspath('.'))[-1] == 'spiderTools':
        os.chdir("Spider2/DataSpiders/DataSpiders")
    print(os.path.dirname(__file__))
    # os.chdir("Spider1/DataSpiders/DataSpiders")
    os.system("python3 Spider2Run.py %s"%task_id)
    change_task_state(task_id, 4)
    if os.path.split(os.path.abspath('.'))[-1] == 'DataSpiders':
        os.chdir("../")
        os.chdir("../")
        os.chdir("../")


@celery.task(name="celery_start_spider2_add")
def celery_start_spider2_add(task_id):
    print(os.path.dirname(__file__))
    if os.path.split(os.path.abspath('.'))[-1] == 'spiderTools':
        os.chdir("Spider2/DataSpiders/DataSpiders")
    print(os.path.dirname(__file__))
    # os.chdir("Spider1/DataSpiders/DataSpiders")
    os.system("python3 Spider2Run_add.py %s"%task_id)
    change_task_state(task_id, 4)
    if os.path.split(os.path.abspath('.'))[-1] == 'DataSpiders':
        os.chdir("../")
        os.chdir("../")
        os.chdir("../")


@celery.task(name='celery_start_spider3')
def celery_start_spider3(task_id, policy_spider_task_info):
    content_list = get_all_content(policy_spider_task_info)
    url_list = analysis_content(content_list=content_list, policy_spider_task_info=policy_spider_task_info)
    insert_url(policy_spider_task_info=policy_spider_task_info, url_list=url_list)
    change_task_state(task_id, 3)


@app.route('/celery/spider1/<int:task_id>')
def start_spider1(task_id):
    psti  = PolicySpiderTaskInfo.query.filter_by(task_id=task_id).first()
    if psti.spider_type == 1:
        change_task_state(task_id, 1)
        with app.app_context():
            celery_start_spider1.delay(task_id)
        return str(task_id)
    elif psti.spider_type == 2:
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
                         type5=policy_spider_task_info.type5)
        with app.app_context():
            celery_start_spider3.delay(task_id, info_dict)
        return str(task_id)
    elif psti.spider_type == 3:
        change_task_state(task_id, 1)
        with app.app_context():
            celery_start_spider1.delay(task_id)
        return str(task_id)
    else:
        return failed_json

@app.route('/celery/spider2/<int:task_id>')
def start_spider2(task_id):
    change_task_state(task_id, 2)
    with app.app_context():
        celery_start_spider2.delay(task_id)
    return str(task_id)


@app.route('/celery/spider2add/<int:task_id>')
def start_spider2_add(task_id):
    change_task_state(task_id, 2)
    with app.app_context():
        celery_start_spider2_add.delay(task_id)
    return str(task_id)

@app.route('/monitor/spider1/<int:task_id>')
def monitor_spider1(task_id):
    sql = 'SELECT state FROM policy_spider_task_info WHERE task_id = %s'%(task_id)
    state = excute_select_sql(sql)

    r = redis.StrictRedis(host=redis_host, port=int(redis_port), db=int(redis_db), password=redis_passwd)
    redis_count = r.llen(str(task_id))


@app.route('/mysql')
def testmysql():
    result = PolicySpiderUrlInfo.query.all()
    for m in result:
        print(m.url)
    print(result)
    return ("s")


@app.route('/tools/showurls')
def show_urls_tools():
    return render_template("show_urls_tools.html")


@app.route('/tools/showrules/<int:task_id>')
def show_rules_tools(task_id):
    rules_info = PolicySpiderTaskInfo.query.filter_by(task_id = task_id).first()
    data = dict(
    rules_organization = rules_info.rules_organization,
    rules_subject = rules_info.rules_subject,
    rules_keywords = rules_info.rules_keywords,
    rules_file_number = rules_info.rules_file_number,
    rules_create_date = rules_info.rules_create_date,
    rules_release_date = rules_info.rules_release_date,
    rules_enforcement_date = rules_info.rules_enforcement_date,
    rules_index_number = rules_info.rules_index_number,
    rules_author = rules_info.rules_author)
    return json.dumps(data)



@app.route('/tools/updaterules/<int:task_id>',methods=['POST', 'GET'])
def update_rules_tools(task_id):
    if request.method == "POST":
        data = json.loads(request.get_data())
        for k in data:
            if data[k] == None:
                data[k]=""
        print(data)

        rules_info = PolicySpiderTaskInfo.query.filter_by(task_id = task_id).first()
        if rules_info.rules_organization !='':
            if data["rules_organization"] != '':
                rules_info.rules_organization = rules_info.rules_organization+";"+data["rules_organization"]
        else:
            rules_info.rules_organization = data["rules_organization"]

        if rules_info.rules_subject !="":
            if data["rules_subject"]!='':
                rules_info.rules_subject = rules_info.rules_subject+";"+data["rules_subject"]
        else:
            rules_info.rules_subject = data["rules_subject"]

        if rules_info.rules_keywords != "":
            if data["rules_keywords"]!='':
                rules_info.rules_keywords = rules_info.rules_keywords+";"+data["rules_keywords"]
        else:
            rules_info.rules_keywords = data["rules_keywords"]

        if rules_info.rules_file_number != "":
            if data["rules_file_number"]!='':
                rules_info.rules_file_number = rules_info.rules_file_number+";"+data["rules_file_number"]
        else:
            rules_info.rules_file_number = data["rules_file_number"]

        if rules_info.rules_create_date !='':
            if data["rules_create_date"] != '':
                rules_info.rules_create_date = rules_info.rules_create_date+";"+data["rules_create_date"]
        else:
            rules_info.rules_create_date = data["rules_create_date"]

        if rules_info.rules_release_date != "" :
            if data["rules_release_date"]!='':
                rules_info.rules_release_date = rules_info.rules_release_date+";"+data["rules_release_date"]
        else:
            rules_info.rules_release_date = data["rules_release_date"]

        if rules_info.rules_enforcement_date !="":
            if data["rules_enforcement_date"]!='':
                rules_info.rules_enforcement_date = rules_info.rules_enforcement_date+";"+data["rules_enforcement_date"]
        else:
            rules_info.rules_enforcement_date = data["rules_enforcement_date"]

        if rules_info.rules_index_number !="":
            if data["rules_index_number"]!='':
                rules_info.rules_index_number = rules_info.rules_index_number+";"+data["rules_index_number"]
        else:
            rules_info.rules_index_number = data["rules_index_number"]

        if rules_info.rules_author!="":
            if data["rules_author"]!='':
                rules_info.rules_author = rules_info.rules_author+";"+data["rules_author"]
        else:
            rules_info.rules_author = data["rules_author"]
        db.session.commit()
        return "SUCCESS"
from copy import deepcopy
def delete_rules(rules_all,rules):
    rules_list = rules_all.split(";")
    copy_rules_list = deepcopy(rules_list)
    for r in rules_list:
        if r == rules:
            copy_rules_list.remove(r)
    if len(copy_rules_list)>0:
        rules_new = ';'.join(copy_rules_list)
    else:
        rules_new = ''
    return rules_new



@app.route('/tools/deleterules/<int:task_id>',methods=['POST', 'GET'])
def delete_rules_tools(task_id):
    if request.method == "POST":
        data = json.loads(request.get_data())
        rules_info = PolicySpiderTaskInfo.query.filter_by(task_id = task_id).first()
        rules_info.rules_organization = delete_rules(rules_info.rules_organization,data["rules_organization"])
        rules_info.rules_subject = delete_rules(rules_info.rules_subject,data["rules_subject"])
        rules_info.rules_keywords = delete_rules(rules_info.rules_keywords,data["rules_keywords"])
        rules_info.rules_file_number = delete_rules(rules_info.rules_file_number,data["rules_file_number"])
        rules_info.rules_create_date = delete_rules(rules_info.rules_create_date,data["rules_create_date"])
        rules_info.rules_release_date = delete_rules(rules_info.rules_release_date,data["rules_release_date"])
        rules_info.rules_enforcement_date = delete_rules(rules_info.rules_enforcement_date,data["rules_enforcement_date"])
        rules_info.rules_index_number = delete_rules(rules_info.rules_index_number,data["rules_index_number"])
        rules_info.rules_author = delete_rules(rules_info.rules_author,data["rules_author"])
        db.session.commit()
        return "SUCCESS"


# 获取网页内容
def get_all_content(policy_spider_task_url, time_delay=3):
    start_url = policy_spider_task_url['start_url']
    rules_next_page = policy_spider_task_url['rules_next_page']
    content_list = []
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.get(start_url)
    time.sleep(int(time_delay))
    i = 1
    try:
        while True:
            content = driver.page_source
            content_list.append(content)
            driver.find_element_by_partial_link_text(rules_next_page).click()
            time.sleep(int(time_delay))
    except Exception as e:
        print(e)
    finally:
        driver.close()
    return content_list


def analysis_content(content_list, policy_spider_task_info):
    url_list = []
    url_head = policy_spider_task_info['url_head']
    rules_url = policy_spider_task_info['rules_url']
    for content in content_list:
        page = etree.HTML(content)
        url_list = url_list + page.xpath(rules_url)
    if url_head != "" or url_head is not None:
        for i in range(0, len(url_list)):
            url_list[i] = urllib.parse.urljoin(url_head, url_list[i])
    return url_list


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


if __name__ == '__main__':
    CORS(app, supports_credentials=True)
    app.run(host='0.0.0.0', port=5000)

# if __name__ =='__main__':
#     task_id = 75
#     policy_spider_task_info = PolicySpiderTaskInfo.query.filter_by(task_id=task_id)
#     content_list = get_all_content(policy_spider_task_info)
#     url_list = analysis_content(content_list=content_list, policy_spider_task_info=policy_spider_task_info)
#     insert_url(policy_spider_task_info=policy_spider_task_info,url_list=url_list)
