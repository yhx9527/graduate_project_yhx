# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request

class ShareSpider(scrapy.Spider):
    name = 'share'
    allowed_domains = ['http://www.iesdouyin.com/']
    search = 'http://www.iesdouyin.com/share/user/59365069100?u_code=13ab7a8dd&sec_uid=MS4wLjABAAAAiam11-fFqPaFjt9m5ZAZ4HzjqxRBM9rWnv2vtF8IUw8&utm_campaign=client_share&app=aweme&utm_medium=ios&tt_from=copy&utm_source=copy'

    def start_requests(self):
        yield Request(url=self.search, callback=self.parse)
        pass

    def parse(self, response):
        pass
