# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
import logging
import requests
from scrapy.exceptions import DropItem
import scrapy

MAPS_URL = 'http://maps.google.com/maps/api/geocode/json?address='

logger = logging.getLogger(__name__)



class MongoBasePipe(object):
    collection_name = 'alquileres_ofrecidos'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        ## pull in information from settings.py
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE')
        )

    def open_spider(self, spider):
        ## initializing spider
        ## opening db connection
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        ## clean up when spider is closed
        self.client.close()


class NoDepto(object):
    def process_item(self, item, spider):
        urlpath = item['url'].lstrip('http://www.vivavisos.com.ar/alquilar-departamento/')
        DEPTO = ('depto', 'departamento', 'dpto', 'dto', 'depart', 'dep')
        if 'vivavisos' in item['url'] and any(elem in urlpath for elem in DEPTO):
            raise DropItem('Item is not a house')
        return item


class MongoItemDoesNotExist(MongoBasePipe):
    def process_item(self, item, spider):
        if self.db[self.collection_name].find_one({'url': item['url']}):
            raise DropItem('Item already present on MongoDB')
        return item


class PopulateItem(object):
    def process_item(self, item, spider):
        if item['url'] not in spider.start_urls:
            # I want to get more fields
            if len(item.keys()) == 1:
                spider.crawler.engine.crawl(
                    scrapy.Request(url=item['url'], callback=spider.parse_alquiler),
                    spider
                )
                raise DropItem('Will populate this...')
            else:
                return item
        raise DropItem('Item is list view')


class NoCountry(object):
    def process_item(self, item, spider):
        if item['type_of_neighbourhood'] in ("Country", "Con Seguridad", "Cerrado"):
            item['discarded'] = True
        return item


class AlquileresMap(object):
    """
    Get the location id for this place
    """
    def process_item(self, item, spider):
        if 'vivavisos' in item['url']:
            place = item['address']
        elif 'olx' in item['url']:
            return item
        else:
            place = ', '.join([
                elem for elem in
                (item['address'], item['city'])
                if elem is not None])

        response = requests.get(MAPS_URL + place)
        if response.ok:
            data = response.json()
            if data['status'] == 'OK':
                place_id = data['results'][0]['place_id']
                item['maps_place_id'] = place_id
                item['location'] = data['results'][0]['geometry']['location']

        if not 'location' in item:
            item['location'] = {'lat': 0, 'lng': 0}
        return item


class InsertIntoMongoDB(MongoBasePipe):
    """
    Insert into mongo DB
    """

    def process_item(self, item, spider):
        self.db[self.collection_name].insert(dict(item))
        logger.debug("Alquiler added to MongoDB")
        return item
