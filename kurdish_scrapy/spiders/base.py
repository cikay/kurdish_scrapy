import scrapy
from typing import Iterable, List, Optional

from extractor.text_extractor import ArticleExtractor
from extractor.protocol import ContentExtractorProtocol


class BaseSpider(scrapy.Spider):
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
        self.content_extractor = content_extractor or ArticleExtractor()
        self.start_urls = []

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
