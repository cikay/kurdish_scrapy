import re
import requests
from requests import Response
from requests.exceptions import RequestException
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
        self.logger.debug("Processing %s", response.url)
        if not UrlExtractor.content_type(response):
            self.logger.debug("Skipped non-HTML response: %s", response.url)
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
    def get_sitemap_urls_from_robots(cls, url: str) -> set[str]:
        parsed_url = urlparse(url)
        robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
        try:
            response = requests.get(url=robots_url, timeout=10)
        except RequestException:
            response = None

        if not response:
            return set()

        if response.status_code != 200:
            return set()

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
            except Exception:
                continue

        return sitemap_urls

    @staticmethod
    def _is_sitemap_response(response: Response) -> bool:
        content_type = response.headers.get("Content-Type", "").lower()
        body_preview = response.text[:4096].lstrip().lower()
        has_sitemap_root_tag = "<urlset" in body_preview or "<sitemapindex" in body_preview

        has_sitemap_xml_root = (
            body_preview.startswith("<?xml")
            and has_sitemap_root_tag
        )
        has_xml_content_type = "xml" in content_type

        return has_sitemap_xml_root or (has_xml_content_type and has_sitemap_root_tag)
