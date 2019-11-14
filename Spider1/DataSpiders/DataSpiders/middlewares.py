# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals

from twisted.internet import defer

from twisted.internet.error import TimeoutError, DNSLookupError, \
    ConnectionRefusedError, ConnectionDone, ConnectError, \
    ConnectionLost, TCPTimedOutError

from twisted.web.client import ResponseFailed

from scrapy.core.downloader.handlers.http11 import TunnelError

from scrapy.http import HtmlResponse




class DataspidersSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class DataspidersDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


# 异常处理中间件
class ProcessAllExceptionMiddleware(object):
    ALL_EXCEPTIONS = (defer.TimeoutError, TimeoutError, DNSLookupError,
                      ConnectionRefusedError, ConnectionDone, ConnectError,
                      ConnectionLost, TCPTimedOutError, ResponseFailed,
                      IOError, TunnelError)

    def process_response(self, request, response, spider):
        # 处理状态码不为200且没发生异常的情况
        if str(response.status) != '200' and str(response.status) != '0':
            # 封装response
            response = HtmlResponse(url=response.url, status = response.status, body=bytes(str("http_code_error"), encoding='utf-8'))
            print("###############")
            return response
        return response

    def process_exception(self, request, exception, spider):
        # 捕获几乎所有的异常
        if isinstance(exception, self.ALL_EXCEPTIONS):
            # 在日志中打印异常类型
            print('Got exception: %s' % (exception))
            # 封装response，并将response.status置0
            response = HtmlResponse(url=request.url, status=0, body=bytes(str(exception), encoding='utf-8'))
            print("*******************")
            return response
        # 打印出未捕获到的异常
        print('not contained exception: %s' % exception)



from selenium import  webdriver
class MytestDownloaderMiddleware(object):
    # 进程请求方法改成用selenium请求
    def process_request(self, request, spider):

        content = self.selenium_request(request.url)
        if content.strip() != '':
            return HtmlResponse(request.url, encoding='utf-8', body=content, request=request)
        return None
        # return None

        # selenium获取页面浏览器内容

    def selenium_request(self, url):
        import time
        chrome_options = webdriver.ChromeOptions()
        # headless无界面模式
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        # chrome_options.add_argument("--proxy-server=https://forward.xdaili.cn:80")
        driver = webdriver.Chrome(chrome_options=chrome_options)
        driver.get(url)
        # driver.maximize_window();# 窗口最大化
        # 执行js滚动浏览器窗口到底部
        # driver.execute_script(js)
        # time.sleep(5)  # 不加载图片的话，这个时间可以不要，等待JS执行
        # driver.get_screenshot_as_file("C:\\Users\\Administrator\\Desktop\\test.png")
        time.sleep(1)
        content = driver.page_source.encode('utf-8')
        # driver.quit()
        driver.close()
        # return None
        return content