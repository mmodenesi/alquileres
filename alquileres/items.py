# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class AlquileresItem(scrapy.Item):
    date_scrapped = scrapy.Field()
    ended = scrapy.Field()
    discarded = scrapy.Field()
    interesting = scrapy.Field()
    url = scrapy.Field()
    maps_place_id = scrapy.Field()
    location = scrapy.Field()

    price = scrapy.Field()
    description = scrapy.Field()
    address = scrapy.Field()
    neighbourhood = scrapy.Field()
    city = scrapy.Field()
    type_of_neighbourhood = scrapy.Field()
    garage = scrapy.Field()
    backyard = scrapy.Field()
    bedrooms = scrapy.Field()
