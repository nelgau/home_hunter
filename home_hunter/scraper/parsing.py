import re

from six.moves.urllib.parse import urljoin
from w3lib.html import strip_html5_whitespace

from scrapy.utils.response import get_base_url

def core_property_url(url):
    # /p/ca/los-angeles/1043-s-hayworth-ave-los-angeles-ca-90035--1031447862
    m = re.match(r'/./[^/]+/[^/]+/[^/]+', url)
    return m[0] if m else None

def urljoin_to_context(url, loader_context):
    response = loader_context.get('response')
    response_url = get_base_url(response)
    return get_absolute_url(url, response_url)

def get_absolute_url(relative_url, base_url):
    try:                
        url = strip_html5_whitespace(relative_url)
        return urljoin(base_url, url)
    except ValueError:
        return None
