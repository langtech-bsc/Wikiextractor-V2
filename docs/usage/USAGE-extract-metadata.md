# Usage: Extract Page Metadata

This guide shows how to extract metadata from a Wikipedia pages dump using `wikiextractor/utils/metadata/metadata.py`.

The metadata extractor reads a pages XML dump and writes one row per page with fields such as page ID, title, namespace, redirect target, revision ID, timestamp, and text byte count.

## Quick start

Extract metadata from the first 100 pages of a compressed Simple English Wikipedia dump:

```bash
mkdir -p data/metadata/simplewiki

python wikiextractor/utils/metadata/metadata.py \
  -f data/dumps/simplewiki/simplewiki-20261001-pages-articles.xml.bz2 \
  -o data/metadata/simplewiki/simplewiki-metadata-100.csv \
  -n 100 \
  --url-base 'https://simple.wikipedia.org/wiki?curid={id}' \
  --format csv


mkdir -p data/metadata/samples
python wikiextractor/utils/metadata/metadata.py \
  -f data/dumps/samples/enwiki-20261001-sample-1000-pages.xml \
  -o data/metadata/samples/enwiki-20261001-sample-100.csv \
  -n 100 \
  --url-base 'https://simple.wikipedia.org/wiki?curid={id}' \
  --format csv
```


data/dumps/samples/enwiki-20261001-sample-1000-pages.xml
Extract metadata from the full dump in the background:

```bash
mkdir -p data/metadata/simplewiki logs

nohup python wikiextractor/utils/metadata/metadata.py \
  -f data/dumps/simplewiki/simplewiki-20261001-pages-articles.xml.bz2 \
  -o data/metadata/simplewiki/simplewiki-metadata.csv \
  --url-base 'https://simple.wikipedia.org/wiki?curid={id}' \
  --format csv \
  > logs/extract-simplewiki-metadata.log 2>&1 &
```

Follow progress:

```bash
tail -f logs/extract-simplewiki-metadata.log
```

## Input

The input can be:

- Plain XML: `.xml`
- Gzip-compressed XML: `.xml.gz`
- Bzip2-compressed XML: `.xml.bz2`

Use a pages dump such as:

```text
data/dumps/simplewiki/simplewiki-20261001-pages-articles.xml.bz2
data/dumps/enwiki/enwiki-20261001-pages-articles.xml.bz2
```

## Output Fields

The extractor writes:

- `id`: Page ID.
- `title`: Page title.
- `ns`: Namespace ID.
- `url`: URL generated from `--url-base`.
- `redirect`: Redirect target title, when the page is a redirect.
- `revision_id`: Latest revision ID in the dump.
- `timestamp`: Latest revision timestamp.
- `text_bytes`: Byte count from the revision text element.

## Output Formats

CSV output:

```bash
python wikiextractor/utils/metadata/metadata.py \
  -f data/dumps/simplewiki/simplewiki-20261001-pages-articles.xml.bz2 \
  -o data/metadata/simplewiki/simplewiki-metadata.csv \
  --format csv
```

JSON Lines output:

```bash
python wikiextractor/utils/metadata/metadata.py \
  -f data/dumps/simplewiki/simplewiki-20261001-pages-articles.xml.bz2 \
  -o data/metadata/simplewiki/simplewiki-metadata.jsonl \
  --format jsonl
```

JSON array output:

```bash
python wikiextractor/utils/metadata/metadata.py \
  -f data/dumps/simplewiki/simplewiki-20261001-pages-articles.xml.bz2 \
  -o data/metadata/simplewiki/simplewiki-metadata.json \
  --format json
```

Use `jsonl` or `csv` for large dumps. The `json` format keeps all rows in memory before writing.

## Process a Fixed Number of Pages

Use `-n` or `--number` to process only the first N pages:

```bash
python wikiextractor/utils/metadata/metadata.py \
  -f data/dumps/simplewiki/simplewiki-20261001-pages-articles.xml.bz2 \
  -o data/metadata/simplewiki/simplewiki-metadata-1000.csv \
  -n 1000 \
  --format csv
```

This is useful for quick checks before processing a full dump.

## URL Base

Use `--url-base` to control generated page URLs:

```bash
--url-base 'https://simple.wikipedia.org/wiki?curid={id}'
```

For English Wikipedia:

```bash
--url-base 'https://en.wikipedia.org/wiki?curid={id}'
```

The `{id}` placeholder is replaced by the page ID.

## Validate the Output

Check the first rows:

```bash
sed -n '1,10p' data/metadata/simplewiki/simplewiki-metadata-100.csv
```

Count rows in a CSV output:

```bash
wc -l data/metadata/simplewiki/simplewiki-metadata-100.csv
```

The CSV has one header row, so a 100-page extraction should have 101 lines.

## Use as a Python Module

```python
from wikiextractor.utils.metadata.metadata import extract_page_metadata

rows = extract_page_metadata(
    "data/dumps/simplewiki/simplewiki-20261001-pages-articles.xml.bz2",
    max_pages=100,
    url_base="https://simple.wikipedia.org/wiki?curid={id}",
)

rows[:3]
```

For streaming workflows, use `iter_page_metadata()` instead of collecting all rows into memory.
