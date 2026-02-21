import scrapy

from extractor.url_extractor import UrlExtractor
from kurdish_scrapy.spiders.base import BaseSpider


class RecursiveSpider(BaseSpider):
    name = "recursive_spider"

    def parse(self, response):
        print(f"[DEBUG] Processing: {response.url}")
        if not UrlExtractor.content_type(response):
            print(f"[DEBUG] Skipped (not HTML): {response.url}")
            return

        result = self.content_extractor.extract(response.text, response.url)
        if result:
            print(f"[DEBUG] Yielding article: {response.url}")
            yield result
        else:
            print(f"[DEBUG] Extraction returned None: {response.url}")

        # Follow internal links recursively when enabled.
        url_extractor = UrlExtractor()
        current_page_contained_urls = url_extractor.extract(response)
        for current_page_contained_url in current_page_contained_urls:
            yield scrapy.Request(
                current_page_contained_url,
                callback=self.parse,
                dont_filter=False,
            )
