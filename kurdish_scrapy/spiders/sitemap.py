from scrapy.spiders import SitemapSpider as BaseSitemapSpider

from extractor.url_extractor import UrlExtractor
from kurdish_scrapy.spiders.base import BaseSpider


class SitemapSpider(BaseSpider, BaseSitemapSpider):
    name = "sitemap_spider"

    def parse(self, response):
        print(f"[DEBUG] Processing: {response.url}")
        if not UrlExtractor.content_type(response):
            print(f"[DEBUG] Skipped (not HTML): {response.url}")
            return

        result = self.content_extractor.extract(response.text, response.url)
        if result:
            yield result

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        spider.sitemap_urls = [
            f"https://{domain}/robots.txt" for domain in spider.allowed_domains
        ]
        return spider
