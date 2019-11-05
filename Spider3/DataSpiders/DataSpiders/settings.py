# -*- coding: utf-8 -*-

# Scrapy settings for DataSpiders project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html
from datetime import datetime
import scrapy_proxies

BOT_NAME = 'DataSpiders'

SPIDER_MODULES = ['DataSpiders.spiders']
NEWSPIDER_MODULE = 'DataSpiders.spiders'



# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 5


DOWNLOAD_DELAY = 0

DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': 90,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
    'DataSpiders.middlewares.DataspidersDownloaderMiddleware': 543,
    'DataSpiders.middlewares.RandomUserAgentMiddlware': 600,
    'DataSpiders.middlewares.ProxyMiddleware': 721,
    'DataSpiders.middlewares.ProcessAllExceptionMiddleware': 1000,
}


ITEM_PIPELINES = {
    #'DataSpiders.pipelines.DataspidersPipeline': 300,
    'DataSpiders.pipelines.DatabasePipeline': 290,
}



AUTOTHROTTLE_MAX_DELAY = 20 #高并发请求时最大延迟时间 默认60
DNS_TIMEOUT = 20 #它是用来设置超时DNS处理的查询。默认值：60
DOWNLOAD_TIMEOUT = 30 #它的总时间下载到之前等待超时。默认值：180
#HTTPERROR_ALLOWED_CODES = [301,302,403,404,503,504,0] #允许通过所有的http状态码：将错误的信息在spider中进行处理
HTTPERROR_ALLOWED_CODES = [301,302,
                           400,401,402,403,404,405,406,407,408,409,410,
                           411,412,413,414,415,416,417,418,419,420,421,
                           422,423,424,425,426,445,491,
                           500,501,502,503,504,505,506,507,508,509,510,0] #允许通过所有的http状态码：将错误的信息在spider中进行处理

RETRY_HTTP_CODES = [500, 503, 504, 400, 408,0]

REDIRECT_ENABLED = False #重定向
# MEDIA_ALLOW_REDIRECTS = True
RETRY_ENABLED = True
RETRY_TIMES =5




