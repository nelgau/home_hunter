import datetime
import json
import re
from pprint import pprint

import js2xml
import scrapy
from scrapy.http import Request
from scrapy.spiders import Spider
from scrapy.linkextractors import LinkExtractor
from scrapy.utils.python import flatten

from home_hunter.scraper.parsing import core_property_url
from home_hunter.scraper.items import SearchResultItemLoader

class TruliaSpider(Spider):

    name = 'trulia'
    allowed_domains = ['trulia.com']

    custom_settings = {
        'DOWNLOAD_DELAY': 30,
        'CONCURRENT_REQUESTS': 1,
        'ITEM_PIPELINES': {
            'home_hunter.scraper.pipelines.StoreTruliaResultsPipeline': 400
        }
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.crawl_timestamp = datetime.datetime.utcnow()
        self.le = LinkExtractor(allow=r'^https://www.trulia.com/for_rent/.+/[\d]+_p/')

    def start_requests(self):        
        # for nh in Neighborhood.all():
        #     url = self.build_search_url(nh.nh_id)
        #     yield Request(url, meta={'nh_id': nh.nh_id}, dont_filter=True)

        url = self.build_search_url()
        yield Request(url, dont_filter=True)

    def build_search_url(self):
        url = 'https://www.trulia.com/for_rent'
        url += '/06037_c'
        url += '/3p_beds'
        url += '/2p_baths'
        url += '/3500-10500_price'
        url += '/1800p_sqft'
        url += '/SINGLE-FAMILY_HOME_type'
        url += '/'
        return url

    def parse(self, response):
        for link in self.le.extract_links(response):
            yield Request(url=link.url, callback=self.parse)

        app_data = self.load_app_data(response)
        home_index = self.build_home_index(app_data)

        container = response.xpath('//ul[@data-testid="search-result-list-container"]')
        results = container.xpath('//div[@data-testid="home-card-rent"]/ancestor::li')

        for selector in flatten(results):
            item = self.load_search_result_item(selector, response, home_index)
            if item: # and item.is_basic_rental():
                yield item

    def load_search_result_item(self, selector, response, home_index):
        loader = SearchResultItemLoader(selector=selector, response=response)

        loader.add_value('crawl_timestamp', self.crawl_timestamp)
        loader.add_value('parse_timestamp', datetime.datetime.utcnow())
        loader.add_value('referrer_url', response.url)

        # URL

        url = selector.css('a:first-child::attr(href)').get()
        core_url = core_property_url(url)
        if core_url is None:
            return None

        loader.add_value('url', core_url)

        # Home data

        home = home_index[url]

        # Thumbnail URL

        if home:
            thumbnail_url = self.get_photo_url(home)
            if thumbnail_url:
                loader.add_value('thumbnail_url', thumbnail_url)

        # Address and coordinates

        seo_json = selector.css('script[data-testid="srp-seo-breadcrumbs-list"]::text').get()
        seo_data = json.loads(seo_json)

        seo_type = seo_data['@type']
        seo_address = seo_data['address']
        seo_geo = seo_data['geo']

        if seo_address is None or seo_geo is None:
            return None

        loader.add_value('address', seo_address['streetAddress'])
        loader.add_value('city', seo_address['addressLocality'])
        loader.add_value('state', seo_address['addressRegion'])
        loader.add_value('zipcode', seo_address['postalCode'])

        loader.add_value('latitude', seo_geo['latitude'])
        loader.add_value('longitude', seo_geo['longitude'])

        # Measurements

        loader.add_css('price', 'div[data-testid="property-price"]::text', re=r'\$([\d,]+)')
        loader.add_css('sqft', 'div[data-testid="property-floorSpace"]::text', re=r'([\d,]+) sqft$')
        loader.add_css('bedrooms', 'div[data-testid="property-beds"]::text', re=r'(\d+)bd$')
        loader.add_css('bathrooms', 'div[data-testid="property-baths"]::text', re=r'(\d+)ba$')        

        # Tags

        tags = set(selector.css('div[data-testid="property-tags"] > span > span::text').getall())

        pprint(tags)

        loader.add_value('pet_friendly', 'Pet Friendly' in tags)
        loader.add_value('furnished', 'Furnished' in tags)        

        return loader.load_item()

    def load_app_data(self, response):
        text = response.css('script[id="__NEXT_DATA__"]::text').get()
        if text is None:
            self.logger.debug("Couldn't find app data script, continuing...")
            return {}

        try:        
            return json.loads(text)
        except (IndexError, ValueError, TypeError, AttributeError) as err:
          self.logger.debug("Error parsing app data script: %s", err)
          return {}

    def build_home_index(self, app_data):
        home_index = {}
        try:
            for home in app_data['props']['searchData']['homes']:
                url = home['url']
                home_index[url] = home
        except (IndexError, ValueError, TypeError, AttributeError) as err:
            self.logger.debug("Error buiding home index: %s", err)
        finally:
            return home_index                

    def get_photo_url(self, home):
        try:
            return home['media']['heroImage']['url']['small']
        except (IndexError, ValueError, TypeError, AttributeError) as err:
            self.logger.debug("Error accessing photo url: %s", err)
            return None
