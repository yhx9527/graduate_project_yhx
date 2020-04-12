# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from scrapydouyin.items import StarItem

class NewrankSpider(scrapy.Spider):
    name = 'newrank'
    allowed_domains = ['www.newrank.cn']
    # start_urls = ['http://www.newrank.cn/']
    url = 'https://www.newrank.cn/public/info/list.html?period=tiktok_week&type=data'

    def parse(self, response):
        stars = response.selector.xpath('//a[@class="tt-name-a"]/text()').extract()
        area = response.selector.xpath('//span[@class="tiktok-type-selected"]/text()').extract_first()
        for star in stars:
            item = StarItem()
            item['name'] = star
            item['area'] = area
            yield item


    def start_requests(self):
        for index in [x for x in range(self.settings.get('AREA_KINDS'))]:
            yield Request(url=self.url, callback=self.parse, meta={'index': index}, dont_filter=True)