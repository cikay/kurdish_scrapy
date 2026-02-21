from scrapy.spiders import SitemapSpider as BaseSitemapSpider

from extractor.url_extractor import UrlExtractor
from kurdish_scrapy.spiders.base import BaseSpider


class SitemapSpider(BaseSpider, BaseSitemapSpider):
    name = "sitemap_spider"
    sitemap_urls = ["https://www.nuhev.com/robots.txt"]

    def parse(self, response):
        print(f"[DEBUG] Processing: {response.url}")
        if not UrlExtractor.content_type(response):
            print(f"[DEBUG] Skipped (not HTML): {response.url}")
            return

        result = self.content_extractor.extract(response.text, response.url)
        if result:
            yield result
