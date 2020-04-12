# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from scrapy.http import Response,TextResponse
from hyper import HTTPConnection
import json
import sys
import os
from urllib.parse import urlparse, urlunparse, urljoin, quote, urlencode
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scrapy.http import HtmlResponse
from logging import getLogger
import time

class SeleniumMiddleware():
    def __init__(self, timeout=None, service_args=[]):
        self.logger = getLogger(__name__)
        self.timeout = timeout
        self.browser = webdriver.PhantomJS(service_args=service_args)
        self.browser.set_window_size(1400, 700)
        self.browser.set_page_load_timeout(self.timeout)
        self.wait = WebDriverWait(self.browser, self.timeout)

    def __del__(self):
        self.browser.close()

    def process_request(self, request, spider):
        """
        用PhantomJS抓取页面
        :param request: Request对象
        :param spider: Spider对象
        :return: HtmlResponse
        """
        self.logger.debug('PhantomJS is Starting')
        index = request.meta.get('index', 1)
        try:
            self.browser.get(request.url)
            list = self.browser.find_elements_by_css_selector('.tiktok-right-type-list span')
            list[index].click()
            self.wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, '.tiktok-type-selected'), str(list[index].text)))
            print('出现了.................')
            time.sleep(1)
            return HtmlResponse(url=request.url, body=self.browser.page_source, request=request, encoding='utf-8',
                         status=200)
        except TimeoutException:
            return HtmlResponse(url=request.url, status=500, request=request)
        self.browser.get(request.url)
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.nickname')))
        self.browser.execute_script("var generate = window.__M.require('douyin_falcon:node_modules/byted-acrawler/dist/runtime');"
                                    "var signature = generate.sign('59365069100');"
                                    "var div = document.createElement('div');div.innerText = signature;div.setAttribute('id','only');document.body.appendChild(div)")
        only = self.browser.find_element_by_id('only')
        temp = self.browser.find_element_by_class_name('nickname')
        print('@@@@@@@@@@@@@@@@@@@',only, only.text)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(timeout=crawler.settings.get('SELENIUM_TIMEOUT'),
                   service_args=crawler.settings.get('PHANTOMJS_SERVICE_ARGS'))


class ScrapydouyinDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.
    def __init__(self):
        self.api_connection = HTTPConnection('api.amemv.com:443')
        temp_path = os.path.join(os.getcwd(), 'args.json')
        with open(temp_path, 'r') as f:
            self.args = json.loads(f.read())
        pass
    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        keyword = request.meta.get('keyword')
        args = self.args[request.url]
        query = args['query']
        query['keyword'] = keyword
        headers = args['headers']
        str = urlencode(query, safe='!*();:@&=+$,/?#[]') #设置安全字符以防止过多编码
        arr = urlparse(request.url)
        url = arr.path+'?'+str
        print('注意检查url编码',url)
        self.api_connection.request('GET', url, headers=headers)
        response = self.api_connection.get_response()
        result = response.read()
        return TextResponse(url=url, status=200, request=request, headers=headers, body=result, encoding='utf-8')

    def process_response(self, request, response, spider):
        return response

    def process_exception(self, request, exception, spider):
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class ScrapyApiDownloaderMiddleware(object):
    def __init__(self):
        self.api_connection = HTTPConnection('api.amemv.com:443')
        temp_path = os.path.join(os.getcwd(), 'args.json')
        with open(temp_path, 'r') as f:
            self.args = json.loads(f.read())
        pass
    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        user_id = request.meta.get('user_id')
        args = self.args[request.url]
        query = args['query']
        query['user_id'] = user_id
        headers = args['headers']
        str = urlencode(query, safe='!*();:@&=+$,/?#[]') #设置安全字符以防止过多编码
        arr = urlparse(request.url)
        url = arr.path+'?'+str
        print('注意检查url编码',url)
        url="/aweme/v1/aweme/post/?max_cursor=0&user_id=71912868448&count=20&retry_type=no_retry&mcc_mnc=46003&iid=104243110108&device_id=61908178454&ac=wifi&channel=wandoujia_aweme&aid=1128&app_name=aweme&version_code=400&version_name=4.0.0&device_platform=android&ssmix=a&device_type=EVA-AL10&device_brand=HUAWEI&language=zh&os_api=26&os_version=8.0.0&uuid=861533036745840&openudid=0f772e0fa9d36257&manifest_version_code=400&resolution=1080*1792&dpi=480&update_version_code=4002&_rticket=1582426486876&ts=1582426486&js_sdk_version=1.6.4&as=a1855ef5e6b7fea9c14922&cp=ee76ef556a155e99e1%5BwIa&mas=013ea13c774313309341e958c883be52094c4c9c2c8cc69c86a666"

        self.api_connection.request('GET', url, headers=headers)
        response = self.api_connection.get_response()
        result = response.read()
        return TextResponse(url=url, status=200, request=request, headers=headers, body=result, encoding='utf-8')

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

class ScrapydouyinSpiderMiddleware(object):
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

        # Should return either None or an iterable of Request, dict
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

