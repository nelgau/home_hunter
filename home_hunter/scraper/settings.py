BOT_NAME = 'home_hunter'

SPIDER_MODULES = ['home_hunter.scraper.spiders']
NEWSPIDER_MODULE = 'home_hunter.scraper.spiders'

# USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'

ROBOTSTXT_OBEY = True

# CONNECTION_STRING = 'sqlite:///data/rentals.db'


HTTPCACHE_ENABLED = True
