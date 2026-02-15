"""Main pipeline for Kurdish content extraction."""

import scrapy

from extractor.text_extractor import ArticleExtractor
from extractor.url_extractor import UrlExtractor


class Pipeline:
    """Pipeline for extracting Kurdish content from websites."""

    def process_response(self, response):
        print(f"[DEBUG] Processing: {response.url}")
        if not UrlExtractor.content_type(response):
            print(f"[DEBUG] Skipped (not HTML): {response.url}")
            return

        extractor = ArticleExtractor()
        result = extractor.extract(response.url, response.text)
        if result:
            print(f"[DEBUG] Yielding article: {response.url}")
            yield result
        else:
            print(f"[DEBUG] Extraction returned None: {response.url}")

        # follow links recursively
        url_extractor = UrlExtractor()
        current_page_contained_urls = url_extractor.extract(response)
        for current_page_contained_url in current_page_contained_urls:
            yield scrapy.Request(
                current_page_contained_url,
                callback=self.process_response,
                dont_filter=False,
            )
