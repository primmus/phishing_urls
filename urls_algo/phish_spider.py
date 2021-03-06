import scrapy
from scrapy.utils.project import get_project_settings


def round_robin(arr):
    to_yield_idx = 0
    length = len(arr)
    while True:
        yield arr[to_yield_idx % length]
        to_yield_idx += 1


class PhishSpider(scrapy.Spider):
    name = "phish"
    handle_httpstatus_list = [200, 302]

    def __init__(self, *args, **kwargs):
        super(PhishSpider, self).__init__(*args, **kwargs)
        self.settings = get_project_settings()
        print(kwargs)
        self.urls = kwargs['urls_objects']
        self.redirect_counter = 0
        self.url_number = 0
        if self.settings['PROXY_LIST']:
            self.proxy_iter = round_robin(self.settings['PROXY_LIST'])

    def start_requests(self):
        for url in self.urls:
            request = scrapy.Request(url=url.url, callback=self.parse)
            if self.settings['PROXY_LIST']:
                request.meta['proxy'] = next(self.proxy_iter)
            yield request

    def parse(self, response):
        if response.status == 200:
            self.url_number += 1
            yield {
                'response': response,
                'url_number': self.url_number,
                'redirect_count': self.redirect_counter
            }
            self.redirect_counter = 0
        if response.status == 302:
            self.redirect_counter += 1
