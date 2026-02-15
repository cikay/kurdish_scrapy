import scrapy

from extractor.pipefile import Pipeline

DOMAINS = [
    "nuhev.com",
]

class RecursiveSpider(scrapy.Spider):
    name = "recursive_spider"

    allowed_domains = [item for domain in DOMAINS for item in (domain, f"www.{domain}")]
    start_urls = [f"http://{domain}" for domain in allowed_domains]

    custom_settings = {
        "DEPTH_LIMIT": 0,  # 0 = no depth limit (crawl entire site)
        "DUPEFILTER_CLASS": "scrapy.dupefilters.RFPDupeFilter",  # default, filters duplicates
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pipeline = Pipeline()

    def parse(self, response):
        yield from self.pipeline.process_response(response)
