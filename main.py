import argparse

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
    run_crawler(output_path=args.output, content_extractor=ArticleExtractor())


if __name__ == "__main__":
    main()
