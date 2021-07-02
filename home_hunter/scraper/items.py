import re

import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose, Identity, Compose

from home_hunter.scraper.parsing import urljoin_to_context


class SearchResultItem(scrapy.Item):
    crawl_timestamp = scrapy.Field()    # YES
    parse_timestamp = scrapy.Field()    # YES

    url = scrapy.Field()                # YES
    thumbnail_url = scrapy.Field()      # YES
    referrer_url = scrapy.Field()       # YES

    neighborhood_id = scrapy.Field()    
    neighborhood = scrapy.Field()
    
    address = scrapy.Field()            # YES
    city = scrapy.Field()               # YES
    state = scrapy.Field()              # YES
    zipcode = scrapy.Field()            # YES
    latitude = scrapy.Field()           # YES
    longitude = scrapy.Field()          # YES

    price = scrapy.Field()
    sqft = scrapy.Field()
    bedrooms = scrapy.Field()
    bathrooms = scrapy.Field()

    pet_friendly = scrapy.Field()
    furnished = scrapy.Field()

    def is_basic_rental(self):
        return re.match(r'^https://www.trulia.com/p/', self.get('url'))

class SearchResultItemLoader(ItemLoader):
    default_item_class = SearchResultItem

    default_input_processor = MapCompose(str.strip)
    default_output_processor = TakeFirst()

    crawl_timestamp_in = Identity()
    parse_timestamp_in = Identity()

    neighborhood_id_in = Identity()    
    url_in = MapCompose(urljoin_to_context)

    latitude_in = Compose(TakeFirst(), float)
    longitude_in = Compose(TakeFirst(), float)

    price_out = Compose(TakeFirst(), lambda s: int(s.replace(',', '')))
    sqft_out = Compose(TakeFirst(), lambda s: int(s.replace(',', '')))
    bedrooms_out = Compose(TakeFirst(), int)
    bathrooms_out = Compose(TakeFirst(), int)

    pet_friendly_in = Identity()
    furnished_in = Identity()
