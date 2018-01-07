# -*- coding: utf-8 -*-
import scrapy


class ZonapropSpider(scrapy.Spider):
    name = 'zonaprop'
    allowed_domains = ['www.zonaprop.com.ar']
    start_urls = [
        'http://www.zonaprop.com.ar/casas-casa-alquiler-cordoba-cb.html'
    ]

    def parse(self, response):

        response.xpath('//ul[@class="list-posts"]/li[contains(@class, "post")]/@data-href').extract()
        pass
