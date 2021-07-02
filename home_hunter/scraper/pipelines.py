import scrapy


class StoreTruliaResultsPipeline(object):

    def __init__(self):
        # self.service = Service()
        # self.service.create_tables()
        pass

    def process_item(self, item, spider):
        # if self.service.store_search_result(item):
        #    spider.log('New rental detected ({url})'.format(url=item.get('url')))
        return item
