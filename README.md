# Kurdish Text Data Collector

A Scrapy-based web scraper for collecting Kurdish text data from websites. The tool recursively crawls specified domains, extracts article content using [Trafilatura](https://trafilatura.readthedocs.io/), and filters results by language using Facebook's [FastText language identification model](https://huggingface.co/facebook/fasttext-language-identification).

## Features

- **Recursive crawling** - Crawls entire websites following internal links
- **Language detection** - Filters content by Kurdish language variants:
  - `kmr_Latn` - Kurmanji (Northern Kurdish, Latin script)
  - `ckb_Arab` - Sorani (Central Kurdish, Arabic script)
  - `diq_Latn` - Zazaki (Latin script)
- **Content extraction** - Extracts clean article text, title, and metadata using Trafilatura
- **Smart filtering** - Skips media files, non-HTML content, and short texts
- **Anti-bot protection** - Rotates user agents via ScrapeOps
- **Duplicate handling** - Built-in URL deduplication

## Prerequisites

- Python 3.10
- [Pipenv](https://pipenv.pypa.io/en/latest/)
- [ScrapeOps API key](https://scrapeops.io/app/headers) (free tier available)

## Installation

1. Clone the repository:
```bash
git clone git@github.com:cikay/kurdish_scrapy.git
cd kurdish_scrapy
```

2. Create and activate virtual environment:
```bash
pipenv --python 3.10
pipenv shell
```

3. Install dependencies:
```bash
pipenv install
```

4. Create a `.env` file with your configuration:
```bash
SCRAPEOPS_API_KEY="your_api_key_here"
ALLOWED_LANGS="kmr_Latn,ckb_Arab,diq_Latn"
TEXT_MIN_WORD_COUNT=100
```

## Configuration

| Variable | Description | Default |
|----------|-------------|--------|
| `SCRAPEOPS_API_KEY` | API key for ScrapeOps user agent rotation | Required |
| `ALLOWED_LANGS` | Comma-separated language codes to collect | `kmr_Latn,ckb_Arab,diq_Latn` |
| `TEXT_MIN_WORD_COUNT` | Minimum word count for collected texts | `100` |

## Usage

### Configure target domains

Edit `kurdish_scrapy/spiders/recursive.py` and add your target domains:

```python
CRAWLING_DOMAINS = [
    "example-kurdish-site.com",
    "another-site.org",
]
```

### Run the app

```bash
python main.py --output output.csv
```

Supported output formats: `.csv`, `.json`, `.jsonl`

### Check collected data statistics

```bash
python rows_count.py --file-name output.csv
```

This displays:
- Total row count
- Unique titles, URLs, and texts count

### Run benchmark mode

Use `bencmark.py` to benchmark one domain by running both spiders sequentially (`SitemapSpider` first, then `RecursiveSpider`) and writing timing logs.

Arguments:
- `--domain`: Required start URL/domain to crawl (use full URL, e.g. `https://www.nuhev.com`)
- `--sitemap`: Output file for sitemap crawl (`.csv`, `.json`, or `.jsonl`)
- `--recursive`: Output file for recursive crawl (`.csv`, `.json`, or `.jsonl`)
- `--benchmark-log` (optional): Log file path for timing details (default: `benchmark.log`)

Example with default log path:

```bash
python bencmark.py --domain https://www.nuhev.com --sitemap sitemap_output.csv --recursive recursive_output.csv
```

## Output Format

The spider outputs the following fields:

| Field | Description |
|-------|-------------|
| `text` | Extracted article content |
| `title` | Article title |
| `url` | Source URL |
| `publisher` | Website/publisher name |
| `word_count` | Word count (calculated by whitespace splitting) |
| `lang` | Detected language code |
| `lang_score` | Language detection confidence score |
| `source_type` | Content type (default: `news`) |

## Project Structure

```
├── kurdish_scrapy/
│   ├── spiders/
│   │   └── recursive.py      # Main recursive spider
│   ├── items.py              # Data item schema
│   ├── middlewares.py        # User agent rotation & URL filtering
│   ├── pipelines.py          # Language & length filtering
│   ├── settings.py           # Scrapy configuration
│   └── lang_model.py         # FastText language model loader
├── extractor/
│   ├── text_extractor.py     # Trafilatura-based content extraction
│   ├── url_extractor.py      # URL parsing and filtering
│   └── pipefile.py           # Main extraction pipeline
├── rows_count.py             # Utility for data statistics
├── Pipfile                   # Dependencies
└── .env                      # Environment variables (create this)
```
