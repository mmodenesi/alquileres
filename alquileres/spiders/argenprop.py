# -*- coding: utf-8 -*-
import scrapy
from alquileres.items import AlquileresItem
from datetime import datetime
import unicodedata
import logging


class ArgenpropSpider(scrapy.Spider):
    name = 'argenprop'
    allowed_domains = ['www.argenprop.com']
    start_urls = [
        'https://www.argenprop.com/Casas-Alquiler-2-Dormitorios'
        '-Pdo-de-Cordoba-Capital/rbQ11KpQ1Kaf_817Kaf_100000001'
        'Kaf_300000011Kaf_802Kaf_1052Kaf_600000193Kaf_48'
        'KvnQVistaResultadosKvncQVistaGrilla',
    ]
    css_selectors = {
        'next_url': 'li.paginado-next>a::attr(href)',
    }
    xpath_selectors = {
        'description_div': '//div[@class="section additionalInfo"]',
        'neighbourhood_and_city': '//h2[@class="title-description"]/span/text()',
        'address': '//h2[@class="address"]/span/text()',
        'price': '//div[@class="price"]/p/text()',
        'bedrooms': '//div[@class="field"][contains(text(), "dormitorios")]/following-sibling::div',
    }


    def parse(self, response):
        for selector in response.css('ul.box-avisos-listado>li.avisoitem>div>a::attr(href)'):
            url = selector.extract()
            item = AlquileresItem()
            item['url'] = response.urljoin(url)
            yield item

        next_url = response.css(self.css_selectors['next_url']).extract_first()
        if next_url:
            yield scrapy.Request(response.urljoin(next_url), callback=self.parse)

    def parse_alquiler(self, response):
        ended = False
        description_div = response.xpath(self.xpath_selectors['description_div'])
        description_raw = description_div.xpath('.//*//text()').extract()
        description = '\n'.join([elem.strip()
                                 for elem in description_raw
                                 if elem.strip()])
        type_of_neighbourhood = None
        neighbourhood, city = response.xpath(self.xpath_selectors['neighbourhood_and_city']).re('.*alquiler en (.*) - (\w+)')
        address = response.xpath(self.xpath_selectors['address']).extract_first()

        price = ''.join(response.xpath(self.xpath_selectors['price']).re('\$ (\d+).(\d+)'))
        bedrooms = response.xpath(self.xpath_selectors['bedrooms']).re('\s+(\d+)\s+')[0]
        garage = ('cochera' in description.lower()) or ('garage' in description.lower())
        backyard = 'patio' in description.lower()

        item = AlquileresItem()
        item['date_scrapped'] = datetime.now()
        item['discarded'] = False
        item['interesting'] = False
        item['url'] = response.url
        item['price'] = price
        item['description'] = unicodedata.normalize('NFKD', description)
        item['address'] = address
        item['city'] = city
        item['neighbourhood'] = neighbourhood
        item['type_of_neighbourhood'] = type_of_neighbourhood
        item['garage'] = garage
        item['backyard'] = backyard
        item['bedrooms'] = bedrooms
        item['ended'] = ended

        yield item
