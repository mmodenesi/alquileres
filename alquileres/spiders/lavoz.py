# -*- coding: utf-8 -*-
import scrapy
import unicodedata
import logging
from alquileres.items import AlquileresItem
from datetime import datetime

from scrapy.shell import inspect_response



logger = logging.getLogger(__name__)


class LavozSpider(scrapy.Spider):
    name = 'lavoz'

    css_selectors = {
        'description_div': 'div#aviso-descripcion',
        'price': 'div.ContentPrecio',
    }
    xpath_selectors = {
        'specs_div': '//div[@class="EspecificacionesA"]',
        'neighbourhood': '//ul/li/span[text() = "Barrio:"]/following-sibling::span/*/text()',
        'city': '//ul/li/span[text() = "Ciudad:"]/following-sibling::span/*/text()',
        'type_of_neighbourhood': '//ul/li/span[text() = "Tipo de Barrio:"]/following-sibling::span/*/text()',
        'address': '//ul/li/span[text() = "Calle:"]/following-sibling::span/text()',
        'bedrooms':'//span[text() ="Cantidad de Dormitorios:"]/following-sibling::span',
        'garage': '//li/span[text() = "Cochera"]',
        'backyard': '//li/span[text() = "Patio"]',
        'next_url': '//li[@class="pager-next"]/a/@href',
        'ended': '//div[@clas="finalizado"]',
    }


    allowed_domains = ['www.clasificadoslavoz.com.ar']
    start_urls = [
        'http://www.clasificadoslavoz.com.ar/search/apachesolr_search?'
        'f[0]=im_taxonomy_vid_34:6330&'
        'f[1]=im_taxonomy_vid_34:6331&'
        'f[2]=ss_operacion:Alquileres&'
        'f[3]=ss_cantidad_dormitorios:2 Dormitorios'
        'f[4]=im_taxonomy_vid_5:3173&'
        'f[5]=im_taxonomy_vid_5:3194',
        'http://www.clasificadoslavoz.com.ar/search/apachesolr_search?'
        'f[0]=im_taxonomy_vid_34:6330&'
        'f[1]=im_taxonomy_vid_34:6331&'
        'f[2]=ss_operacion:Alquileres&'
        'f[3]=ss_cantidad_dormitorios:3 Dormitorios'
        'f[4]=im_taxonomy_vid_5:3173&'
        'f[5]=im_taxonomy_vid_5:3194',
    ]

    def parse(self, response):
        for alquiler in response.css('div.BoxResultado'):
            url = alquiler.css('div.foto>a::attr(href)').extract_first()
            item = AlquileresItem()
            item['url'] = url
            yield item

        next_url = response.xpath(self.xpath_selectors['next_url']).extract_first()
        if next_url:
            yield scrapy.Request(response.urljoin(next_url), callback=self.parse)

    def parse_alquiler(self, response):
        ended = response.xpath(self.xpath_selectors['ended']) is not None
        description_div = response.css(self.css_selectors['description_div'])
        description_raw = description_div.xpath('.//*//text()').extract()
        description = '\n'.join([elem.strip()
                                 for elem in description_raw
                                 if elem.strip()])
        specs_div = response.xpath(self.xpath_selectors['specs_div'])
        type_of_neighbourhood = specs_div.xpath(self.xpath_selectors['type_of_neighbourhood']).extract_first()
        neighbourhood = specs_div.xpath(self.xpath_selectors['neighbourhood']).extract_first()
        city = specs_div.xpath(self.xpath_selectors['city']).extract_first()
        address = specs_div.xpath(self.xpath_selectors['address']).extract_first()

        price = ''.join(response.css(self.css_selectors['price']).re('\$(\d+)[\.,](\d+)'))
        bedrooms = response.xpath(self.xpath_selectors['bedrooms']).re('\d+')[0]
        garage = response.xpath(self.xpath_selectors['garage']) is not None
        backyard = response.xpath(self.xpath_selectors['backyard']) is not None

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
