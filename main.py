import argparse
from pathlib import Path

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from kurdish_scrapy.spiders.recursive import RecursiveSpider
from extractor.text_extractor import ArticleExtractor


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


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run RecursiveSpider with output file.")
    parser.add_argument(
        "-o",
        "--output",
        required=True,
        help="Output file path (supported: .csv, .json, .jsonl)",
    )
    return parser.parse_args()


def main():
    args = _parse_args()
    feed_format = _infer_feed_format(args.output)

    settings = get_project_settings()
    settings.set(
        "FEEDS",
        {
            args.output: {
                "format": feed_format,
                "encoding": "utf-8",
                "overwrite": True,
            }
        },
        priority="cmdline",
    )

    process = CrawlerProcess(settings)
    process.crawl(RecursiveSpider, content_extractor=ArticleExtractor())
    process.start()


if __name__ == "__main__":
    main()
