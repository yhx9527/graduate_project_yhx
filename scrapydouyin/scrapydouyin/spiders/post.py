# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request

class PostSpider(scrapy.Spider):
    name = 'post'
    allowed_domains = ['api.amemv.com']
    # start_urls = ['http://api.amemv.com/']

    post_url = 'https://api.amemv.com/aweme/v1/aweme/post/'

    def start_requests(self):
        yield Request(url=self.post_url, callback=self.parse, meta={'user_id': '71912868448'})
        pass

    def parse(self, response):
        print('post作品', response.text)
