import argparse
import json
from pathlib import Path

from extractor.text_extractor import ArticleExtractor
from run_crawler import run_crawler


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run RecursiveSpider with output file."
    )
    parser.add_argument(
        "-o",
        "--output",
        required=True,
        help="Output file path (supported: .csv, .json, .jsonl)",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    urls_to_crawl = json.loads(Path("kurdish_domains.json").read_text(encoding="utf-8"))
    run_crawler(
        output_path=args.output,
        content_extractor=ArticleExtractor(),
        urls_to_crawl=urls_to_crawl,
    )


if __name__ == "__main__":
    main()
