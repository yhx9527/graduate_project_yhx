# -*- coding: utf-8 -*-
import scrapy
from urllib.parse import quote
from scrapy import Request

class AmemvSpider(scrapy.Spider):
    name = 'amemv'
    allowed_domains = ['api.amemv.com']
    # start_urls = ['https://api.amemv.com/aweme/v1/general/search/single/']
    seach_url = 'https://api.amemv.com/aweme/v1/general/search/single/'

    def start_requests(self):
        yield Request(url=self.seach_url, callback=self.parse, meta={'keyword': '邓紫'})
        pass
    def parse(self, response):
        print('ddddddddd',response.text)
