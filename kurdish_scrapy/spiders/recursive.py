import scrapy
from typing import Iterable, List, Optional

from extractor.url_extractor import UrlExtractor
from extractor.protocol import ContentExtractorProtocol


class RecursiveSpider(scrapy.Spider):
    name = "recursive_spider"

    custom_settings = {
        "DEPTH_LIMIT": 0,  # 0 = no depth limit (crawl entire site)
        "DUPEFILTER_CLASS": "scrapy.dupefilters.RFPDupeFilter",  # default, filters duplicates
    }

    def __init__(
        self,
        content_extractor: Optional[ContentExtractorProtocol] = None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.allowed_domains = []
        self.content_extractor = content_extractor
        self.start_urls = []

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

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        spider.allowed_domains = spider._resolve_allowed_domains(
            allowed_domains=spider.allowed_domains,
            settings=crawler.settings,
        )
        if spider.allowed_domains:
            spider.start_urls = [
                f"http://{domain}" for domain in spider.allowed_domains
            ]
        return spider

    @classmethod
    def _resolve_allowed_domains(
        cls,
        allowed_domains: Optional[Iterable[str]],
        settings=None,
    ) -> List[str]:
        explicit_domains = cls._normalize_domains(allowed_domains)
        if explicit_domains:
            return explicit_domains

        if settings is None:
            return []

        return cls._normalize_domains(settings.get("ALLOWED_DOMAINS"))

    @staticmethod
    def _normalize_domains(domains: Optional[Iterable[str]]) -> List[str]:
        normalized = []
        for domain in domains or []:
            clean = domain.strip()
            if clean:
                normalized.append(clean)
        return normalized
