# -*- coding: utf-8 -*-
import scrapy
from alquileres.items import AlquileresItem
from datetime import datetime
import unicodedata
import logging


class VivavisosSpider(scrapy.Spider):
    name = 'vivavisos'
    allowed_domains = [
        'search.vivavisos.com.ar',
    ]
    start_urls = [
        'http://search.vivavisos.com.ar/alquilar-departamento/cordoba?'
        'lb=new&search=1&start_field=1&sp_housing_nb_bedrs%5Bstart%5D=2&'
        'sp_housing_nb_bedrs%5Bend%5D=&keywords=&cat_1=37&'
        'sp_housing_monthly_rent%5Bstart%5D=&sp_housing_monthly_rent%5Bend%5D=&'
        'offer_type=offer&searchGeoId=53&end_field=',

        'http://search.vivavisos.com.ar/alquilar-departamento/cordoba/t+2?'
        'lb=new&search=1&start_field=1&sp_housing_nb_bedrs%5Bstart%5D=2&'
        'sp_housing_nb_bedrs%5Bend%5D=&keywords=&cat_1=37&'
        'sp_housing_monthly_rent%5Bstart%5D=&sp_housing_monthly_rent%5Bend%5D=&'
        'offer_type=offer&searchGeoId=53&end_field=',

        'http://search.vivavisos.com.ar/alquilar-departamento/cordoba/t+3?'
        'lb=new&search=1&start_field=1&sp_housing_nb_bedrs%5Bstart%5D=2&'
        'sp_housing_nb_bedrs%5Bend%5D=&keywords=&cat_1=37&'
        'sp_housing_monthly_rent%5Bstart%5D=&sp_housing_monthly_rent%5Bend%5D=&'
        'offer_type=offer&searchGeoId=53&end_field=',

        'http://search.vivavisos.com.ar/alquilar-departamento/cordoba/t+4?'
        'lb=new&search=1&start_field=1&sp_housing_nb_bedrs%5Bstart%5D=2&'
        'sp_housing_nb_bedrs%5Bend%5D=&keywords=&cat_1=37&'
        'sp_housing_monthly_rent%5Bstart%5D=&sp_housing_monthly_rent%5Bend%5D=&'
        'offer_type=offer&searchGeoId=53&end_field=',

        'http://search.vivavisos.com.ar/alquilar-departamento/cordoba/t+5?'
        'lb=new&search=1&start_field=1&sp_housing_nb_bedrs%5Bstart%5D=2&'
        'sp_housing_nb_bedrs%5Bend%5D=&keywords=&cat_1=37&'
        'sp_housing_monthly_rent%5Bstart%5D=&sp_housing_monthly_rent%5Bend%5D=&'
        'offer_type=offer&searchGeoId=53&end_field=',

        'http://search.vivavisos.com.ar/alquilar-departamento/cordoba/t+6?'
        'lb=new&search=1&start_field=1&sp_housing_nb_bedrs%5Bstart%5D=2&'
        'sp_housing_nb_bedrs%5Bend%5D=&keywords=&cat_1=37&'
        'sp_housing_monthly_rent%5Bstart%5D=&sp_housing_monthly_rent%5Bend%5D=&'
        'offer_type=offer&searchGeoId=53&end_field=',

        'http://search.vivavisos.com.ar/alquilar-departamento/cordoba/t+7?'
        'lb=new&search=1&start_field=1&sp_housing_nb_bedrs%5Bstart%5D=2&'
        'sp_housing_nb_bedrs%5Bend%5D=&keywords=&cat_1=37&'
        'sp_housing_monthly_rent%5Bstart%5D=&sp_housing_monthly_rent%5Bend%5D=&'
        'offer_type=offer&searchGeoId=53&end_field=',
    ]

    xpath_selectors = {
        'next_url': '//a[contains(text(), "Siguiente")]',
        'price': '//table/tr[td[contains(text(), "Precio")]]/td[contains(text(), "$")]/text()',
        'city': '//table/tr[td[contains(text(), "Ubicación")]]/td[2]/div/text()',
        'address': '//a/span[@class="kiwii-icon kiwii-icon-map-pointer kiwii-icon-inline kiwii-padding-right-xxxsmall"]/../@href',
        'bedrooms': '//*/table/tr[td[contains(text(), "Dormitorios")]]/td[2]/text()',
    }

    def parse(self, response):
        for alquiler in response.css('tr.classified.kiwii-clad-row'):
            url = alquiler.css('td.photo>a::attr(href)').extract_first()
            item = AlquileresItem()
            item['url'] = url
            yield item

        # next_url = response.xpath(self.xpath_selectors['next_url']).extract_first()
        # if next_url:
            # yield scrapy.Request(response.urljoin(next_url), callback=self.parse)

    def parse_alquiler(self, response):
        ended = False
        description_raw = response.xpath('//div[@class="shortdescription"]/text()').extract()
        description = '\n'.join([elem.strip()
                                 for elem in description_raw
                                 if elem.strip()])
        type_of_neighbourhood = None
        neighbourhood = None
        city = ', '.join(response.xpath(self.xpath_selectors['city']).extract())
        address = response.xpath(self.xpath_selectors['address']).extract_first().split('/')[-1]

        price = ''.join(response.xpath(self.xpath_selectors['price']).re('\s*AR\$\s*(\d+)\.?(\d+)'))
        bedrooms = response.xpath(self.xpath_selectors['bedrooms']).re('\s*(\d+)\s*')[0]
        garage = any(elem in description.lower() for elem in ('cochera', 'garage'))
        backyard = 'patio' in description.lower()

        item = AlquileresItem()
        item['date_scrapped'] = datetime.now()
        item['discarded'] = False
        item['interesting'] = False
        item['url'] = response.url
        item['price'] = price
        item['description'] = unicodedata.normalize('NFKD', description)
        item['address'] = address.replace('+', ' ')
        item['city'] = city
        item['neighbourhood'] = neighbourhood
        item['type_of_neighbourhood'] = type_of_neighbourhood
        item['garage'] = garage
        item['backyard'] = backyard
        item['bedrooms'] = bedrooms
        item['ended'] = ended

        yield item
