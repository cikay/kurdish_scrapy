import re
import requests
from urllib.error import URLError
from urllib.parse import urlparse, urljoin


from scrapy.spiders import SitemapSpider as BaseSitemapSpider

from extractor.url_extractor import UrlExtractor
from kurdish_scrapy.settings import SITEMAP_PATTERNS


SITEMAP_REGEX = re.compile(r"Sitemap:\s([^\r\n#]*)", re.MULTILINE)


class SitemapSpider(BaseSitemapSpider):
    name = "sitemap_spider"

    def __init__(self, content_extractor, sitemap_urls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.content_extractor = content_extractor
        self.sitemap_urls = sitemap_urls

    def parse(self, response):
        print(f"[DEBUG] Processing: {response.url}")
        if not UrlExtractor.content_type(response):
            print(f"[DEBUG] Skipped (not HTML): {response.url}")
            return

        result = self.content_extractor.extract(response.text, response.url)
        if result:
            yield result

    @classmethod
    def get_sitemap_urls(cls, url):
        sitemap_urls_from_robots = cls.get_sitemap_urls_from_robots(url)
        if sitemap_urls_from_robots:
            return sitemap_urls_from_robots

        return cls.get_sitemap_url_from_patterns(url)

    @classmethod
    def get_sitemap_urls_from_robots(cls, url: str) -> list[str]:
        parsed_url = urlparse(url)
        robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
        try:
            response = requests.get(url=robots_url)
        except URLError:
            response = None

        if not response:
            return []

        if response.status_code != 200:
            return []

        robots_content = response.text
        sitemap_urls = set()
        for sitemap_url in SITEMAP_REGEX.findall(robots_content):
            normalized_sitemap_url = urljoin(robots_url, sitemap_url.strip())
            if cls._is_same_domain(url, normalized_sitemap_url):
                sitemap_urls.add(normalized_sitemap_url)

        return sitemap_urls

    @staticmethod
    def _is_same_domain(base_url: str, candidate_url: str) -> bool:
        base_host = (urlparse(base_url).hostname or "").lower().removeprefix("www.")
        candidate_host = (
            (urlparse(candidate_url).hostname or "").lower().removeprefix("www.")
        )
        return base_host == candidate_host

    @classmethod
    def get_sitemap_url_from_patterns(cls, url):
        sitemap_urls = set()
        for sitemap_path in SITEMAP_PATTERNS:
            url_sitemap = urljoin(url, sitemap_path)
            try:
                response = requests.get(url=url_sitemap)
                # Keep sitemaps that exist, including those resulting from redirections
                if response.status_code in [200, 301, 308]:
                    sitemap_urls.add(response.url)
            except URLError:
                continue

        return sitemap_urls
