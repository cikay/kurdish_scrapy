from pathlib import Path

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from kurdish_scrapy.spiders.recursive import RecursiveSpider
from kurdish_scrapy.spiders.sitemap import SitemapSpider
from extractor.protocol import ContentExtractorProtocol


SUPPORTED_FEED_FORMATS = {
    ".csv": "csv",
    ".json": "json",
    ".jsonl": "jsonlines",
}


def _infer_feed_format(output_path: str) -> str:
    ext = Path(output_path).suffix.lower()
    feed_format = SUPPORTED_FEED_FORMATS.get(ext)
    if not feed_format:
        supported = ", ".join(SUPPORTED_FEED_FORMATS.keys())
        raise ValueError(
            f"Unsupported output extension '{ext}'. Use one of: {supported}"
        )
    return feed_format


def run_crawler(
    output_path: str,
    content_extractor: ContentExtractorProtocol,
    urls_to_crawl: list[str],
) -> None:
    feed_format = _infer_feed_format(output_path)
    settings = get_project_settings()
    settings.set(
        "FEEDS",
        {
            output_path: {
                "format": feed_format,
                "encoding": "utf-8",
                "overwrite": False,
            }
        },
        priority="cmdline",
    )
    crawler_process = CrawlerProcess(settings)

    for url_to_crawl in urls_to_crawl:
        sitemap_urls = SitemapSpider.get_sitemap_urls(url_to_crawl)
        if sitemap_urls:
            crawler_process.crawl(
                SitemapSpider,
                content_extractor=content_extractor,
                sitemap_urls=sitemap_urls,
            )
        else:
            crawler_process.crawl(
                RecursiveSpider,
                url=url_to_crawl,
                content_extractor=content_extractor,
            )

    crawler_process.start()
