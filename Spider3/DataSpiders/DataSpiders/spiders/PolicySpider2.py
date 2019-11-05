import scrapy, time, configparser, os, redis, json, random
from ..items import SpiderLogItem, SpiderDataItem, SpiderUrlMysqlItem
from scrapy import Spider, Request
from scrapy_splash import SplashRequest

# D:\programming\PycharmProjects\DataSpiders\DataSpiders
# D:\programming\PycharmProjects\DataSpiders\DataSpiders\DatabaseConfig.ini
class PolicySpider2(scrapy.Spider):
    name = "PolicySpider2"


    # configparser用以读写配置文件
    cf = configparser.ConfigParser()
    cf.read(os.path.join(os.path.dirname(__file__), 'config.ini',), encoding='utf-8')
    # 读取任务信息
    cf_id = '1'
    taskid = cf.get(cf_id, 'task_id')

    # 从配置文件中读取redis的配置
    cf_database = configparser.ConfigParser()
    pwd = os.getcwd()
    path = os.path.join(os.path.abspath(os.path.dirname(pwd)+os.path.sep+".."),"DataSpiders","DataSpiders","DatabaseConfig.ini")
    cf_database.read(path, encoding='utf-8')
    print(path)
    #cf_database.read('D:\programming\PycharmProjects\DataSpiders\DataSpiders\DatabaseConfig.ini', encoding='utf-8')
    # cf_database.read(os.path.join(os.path.dirname(__file__), 'DatabaseConfig.ini',),encoding='utf-8')
    cf_name = "REDIS_TEST"
    redis_host = cf_database.get(cf_name,"redis_host")
    redis_port = cf_database.get(cf_name,"redis_port")
    redis_db = cf_database.get(cf_name,"redis_db")
    redis_password = cf_database.get(cf_name,"redis_passwd")
    r = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db, password=redis_password)

    # 每次从redis中提取的二级url任务的条数
    url_count = 100
    #url_list_len = r.llen()
    script = """
    function main(splash, args)
        splash.images_enabled = false
        local scroll_to = splash:jsfunc("window.scrollTo")
        scroll_to(0, 2800)
    end
    """


    def start_requests(self):
        while(self.r.llen(str(self.taskid))>0):
            for i in range(self.url_count):
                c = self.r.lpop(str(self.taskid))
                if c:
                    c = bytes.decode(c)
                    c = json.loads(c)
                    for url,info in c.items():
                        task_id = info["task_id"]
                        type1 = info["type1"]
                        type2 = info["type2"]
                        type3 = info["type3"]
                        type4 = info["type4"]
                        type5 = info["type5"]
                        yield Request(url=url,dont_filter=True,callback=self.parse,meta={
                                                                        'url': url,
                                                                        'task_id': task_id,
                                                                        'type1': type1,
                                                                        'type2': type2,
                                                                        'type3': type3,
                                                                        'type4': type4,
                                                                        'type5': type5,

                                                                        })

    def parse(self, response):
        #print(response.request.headers)
        spider_log_item = SpiderLogItem()
        spider_log_item["url"] = response.meta["url"]
        spider_log_item["spider_stage"] = 2
        spider_log_item["task_id"] = response.meta["task_id"]
        spider_log_item["type1"] = response.meta["type1"]
        spider_log_item["type2"] = response.meta["type2"]
        spider_log_item["type3"] = response.meta["type3"]
        spider_log_item["type4"] = response.meta["type4"]
        spider_log_item["type5"] = response.meta["type5"]
        spider_log_item["proxy"] = ""
        spider_log_item["insert_time"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

        spider_data_item = SpiderDataItem()
        spider_data_item["task_id"] = response.meta["task_id"]
        spider_data_item["url"] = response.meta["url"]
        spider_data_item["type1"] = response.meta["type1"]
        spider_data_item["type2"] = response.meta["type2"]
        spider_data_item["type3"] = response.meta["type3"]
        spider_data_item["type4"] = response.meta["type4"]
        spider_data_item["type5"] = response.meta["type5"]
        spider_data_item["insert_time"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        print("response status:", response.status)

        if response.status == 200:
            spider_log_item["state"] = 1
            spider_log_item["http_code"] = str(response.status)
            spider_log_item["msg"] = "SUCCESS"
            yield spider_log_item
            spider_data_item["html"] = response.text
            yield spider_data_item
        else:
            spider_log_item["state"] = 0
            spider_log_item["http_code"] = str(response.status)
            spider_log_item["msg"] = response.body.decode('utf-8', 'ignore')
            yield spider_log_item
