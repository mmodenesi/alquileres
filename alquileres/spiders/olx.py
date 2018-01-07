# -*- coding: utf-8 -*-
import scrapy
import unicodedata
import logging
from alquileres.items import AlquileresItem
from datetime import datetime


logger = logging.getLogger(__name__)


class OlxSpider(scrapy.Spider):
    name = 'olx'
    allowed_domains = ['cordobacapital.olx.com.ar']
    start_urls = [
        'https://cordobacapital.olx.com.ar/nf/'
        'departamentos-casas-alquiler-cat-363/-bedrooms_2_-flo_houses_duplex',
    ]

    css_selectors = {
    }

    xpath_selectors = {
        'description': '//p[@class="item_partials_description_view"]/text()',
        'city': '//span[contains(@class, "location ")]/text()',
        'price': '//strong[contains(@class, "price")]/text()',
        'bedrooms': '//ul/li/strong[contains(text(), "Dormitorios")]/following-sibling::span/text()',
        'location': '//div[@class="map"]/a/@href',
    }

    def parse(self, response):
        for url in response.xpath('//ul[@class="items-list "]/li[contains(@class, "item ")]/a/@href').extract():
            item = AlquileresItem()
            item['url'] = 'https:' + url
            yield item

        next_url = response.xpath('//a[@rel="next"]/@href').extract_first()
        if next_url:
            yield scrapy.Request('https:' + next_url, callback=self.parse)

    def parse_alquiler(self, response):
        ended = False
        description = response.xpath(self.xpath_selectors['description']).extract_first()
        type_of_neighbourhood = None
        neighbourhood = ''
        city = response.xpath(self.xpath_selectors['city']).re('\s*(\w+), .*')[0]
        address = ''

        price = ''.join(response.xpath(self.xpath_selectors['price']).re('\$(\d+)*.(\d+)'))
        bedrooms = response.xpath(self.xpath_selectors['bedrooms']).extract_first()
        garage = ('cochera' in description.lower()) or ('garage' in description.lower())
        backyard = 'patio' in description.lower()

        lat, lng = response.xpath(self.xpath_selectors['location']).re('.*/place.*/(.*),(.*)')
        location = {'lat': float(lat), 'lng': float(lng)}

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
        item['location'] = location

        yield item
