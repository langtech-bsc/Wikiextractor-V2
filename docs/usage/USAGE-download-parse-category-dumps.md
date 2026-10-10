# Usage: Download and Parse Category Dumps

This guide shows how to download English Wikipedia category SQL dumps and create smaller samples for local testing.

These files are not article XML dumps, so they are not parsed with `wikiextractor/WikiExtractor.py`. They are SQL table dumps for MediaWiki category metadata and category membership relations.

## Quick start

Download the latest dated `category` and `categorylinks` SQL dumps:

```bash
mkdir -p data/dumps/enwiki-sql logs

for table in category categorylinks; do
  latest_url="https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-${table}.sql"
  rss_url="${latest_url}.gz-rss.xml"
  download_url=$(curl -Ls "$rss_url" | sed -n 's/.*href="\([^"]*\.sql\.gz\)".*/\1/p' | head -n 1)
  dump_file="data/dumps/enwiki-sql/$(basename "$download_url")"

  nohup curl -L \
    -o "$dump_file" \
    "$download_url" \
    > "logs/download-enwiki-${table}.log" 2>&1 &
done
```


Download only the latest Simple English Wikipedia `category` SQL dump:

```bash
mkdir -p data/dumps/simplewiki logs

latest_url="https://dumps.wikimedia.org/simplewiki/latest/simplewiki-latest-category.sql"
rss_url="${latest_url}.gz-rss.xml"
rss_url="https://dumps.wikimedia.org/simplewiki/latest/simplewiki-latest-category.sql.gz-rss.xml"

latest_url="https://dumps.wikimedia.org/simplewiki/latest/simplewiki-latest-categorylinks.sql.gz"
rss_url="${latest_url}-rss.xml"
rss_url="https://dumps.wikimedia.org/simplewiki/latest/simplewiki-latest-categorylinks.sql.gz-rss.xml"

download_url=$(curl -Ls "$rss_url" | sed -n 's/.*href="\([^"]*\.sql\.gz\)".*/\1/p' | head -n 1)
dump_file="data/dumps/simplewiki/$(basename "$download_url")"
nohup curl -L \
  -o "$dump_file" \
  "$download_url" \
  > logs/download-simplewiki-category.log 2>&1 &
```

Create SQL samples from the downloaded dumps:

```bash
mkdir -p data/dumps/enwiki-sql/samples

for table in category categorylinks; do
  dump_file=$(ls data/dumps/enwiki-sql/enwiki-*-${table}.sql.gz | head -n 1)
  sample_file="data/dumps/enwiki-sql/samples/$(basename "$dump_file" .gz)-sample.sql"

  gzip -dc "$dump_file" | LC_ALL=C awk '
    /^INSERT INTO/ { inserts += 1; print; if (inserts >= 5) exit; next }
    inserts == 0 { print }
  ' > "$sample_file"
done
```

## What These Dumps Contain

- `category.sql.gz`: One row per category, including the category title and category counts.
- `categorylinks.sql.gz`: Category membership links. `cl_from` is the page ID of the page, subcategory, or file; `cl_to` is the target category title; `cl_type` identifies whether the linked source is a `page`, `subcat`, or `file`.

Useful fields:

```text
category:
  cat_id, cat_title, cat_pages, cat_subcats, cat_files, cat_hidden

categorylinks:
  cl_from, cl_to, cl_sortkey, cl_sortkey_prefix, cl_timestamp, cl_collation, cl_type
```

To resolve `categorylinks.cl_from` page IDs into page titles, also download and load `page.sql.gz`.

## Resolve the Latest Snapshot

Use the RSS XML files to find the dated SQL dump URLs:

```bash
curl -L https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-category.sql.gz-rss.xml
curl -L https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-categorylinks.sql.gz-rss.xml
```

The RSS response contains a dated URL, for example:

```xml
<description>&lt;a href="http://download.wikimedia.org/enwiki/20261008/enwiki-20261008-categorylinks.sql.gz"&gt;enwiki-20261008-categorylinks.sql.gz&lt;/a&gt;</description>
```

Prefer downloading that dated file, rather than saving a permanent file named `latest`.

## Download in the Background

Download `category.sql.gz`:

```bash
mkdir -p data/dumps/enwiki-sql logs

latest_url="https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-category.sql"
rss_url="${latest_url}.gz-rss.xml"
download_url=$(curl -Ls "$rss_url" | sed -n 's/.*href="\([^"]*\.sql\.gz\)".*/\1/p' | head -n 1)
dump_file="data/dumps/enwiki/$(basename "$download_url")"

nohup curl -L \
  -o "$dump_file" \
  "$download_url" \
  > logs/download-enwiki-category.log 2>&1 &
```

Download Simple English Wikipedia `category.sql.gz`:

```bash
mkdir -p data/dumps/simplewiki logs

latest_url="https://dumps.wikimedia.org/simplewiki/latest/simplewiki-latest-category.sql"
rss_url="${latest_url}.gz-rss.xml"
download_url=$(curl -Ls "$rss_url" | sed -n 's/.*href="\([^"]*\.sql\.gz\)".*/\1/p' | head -n 1)
dump_file="data/dumps/simplewiki/$(basename "$download_url")"

nohup curl -L \
  -o "$dump_file" \
  "$download_url" \
  > logs/download-simplewiki-category.log 2>&1 &
```

Download `categorylinks.sql.gz`:

```bash
mkdir -p data/dumps/enwiki-sql logs

latest_url="https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-categorylinks.sql"
rss_url="${latest_url}.gz-rss.xml"
download_url=$(curl -Ls "$rss_url" | sed -n 's/.*href="\([^"]*\.sql\.gz\)".*/\1/p' | head -n 1)
dump_file="data/dumps/enwiki/$(basename "$download_url")"

nohup curl -L \
  -o "$dump_file" \
  "$download_url" \
  > logs/download-enwiki-categorylinks.log 2>&1 &
```

Follow progress:

```bash
tail -f logs/download-enwiki-categorylinks.log
```

## Validate Downloads

```bash
ls -lh data/dumps/enwiki-sql/enwiki-*-category.sql.gz
ls -lh data/dumps/enwiki-sql/enwiki-*-categorylinks.sql.gz
```

Check that gzip can read the files:

```bash
gzip -t data/dumps/enwiki-sql/enwiki-*-category.sql.gz
gzip -t data/dumps/enwiki-sql/enwiki-*-categorylinks.sql.gz
```

Preview SQL without decompressing to disk:

```bash
gzip -dc data/dumps/enwiki-sql/enwiki-*-category.sql.gz | sed -n '1,80p'
```

## Create SQL Samples

The SQL dumps are plain text after decompression. A simple, valid sample can keep the table DDL and the first few `INSERT INTO` statements:

```bash
mkdir -p data/dumps/enwiki-sql/samples

dump_file=$(ls data/dumps/enwiki-sql/enwiki-*-category.sql.gz | head -n 1)
gzip -dc "$dump_file" | LC_ALL=C awk '
  /^INSERT INTO/ { inserts += 1; print; if (inserts >= 5) exit; next }
  inserts == 0 { print }
' > data/dumps/enwiki-sql/samples/enwiki-category-sample.sql
```

For category relations:

```bash
mkdir -p data/dumps/enwiki-sql/samples

dump_file=$(ls data/dumps/enwiki-sql/enwiki-*-categorylinks.sql.gz | head -n 1)
gzip -dc "$dump_file" | LC_ALL=C awk '
  /^INSERT INTO/ { inserts += 1; print; if (inserts >= 5) exit; next }
  inserts == 0 { print }
' > data/dumps/enwiki-sql/samples/enwiki-categorylinks-sample.sql
```

This samples SQL statements, not exact row counts. Wikimedia SQL dumps often place many rows in each `INSERT INTO` line.

For a Simple English Wikipedia category sample:

```bash
mkdir -p data/dumps/simplewiki-sql/samples

dump_file=$(ls data/dumps/simplewiki-sql/simplewiki-*-category.sql.gz | head -n 1)
gzip -dc "$dump_file" | LC_ALL=C awk '
  /^INSERT INTO/ { inserts += 1; print; if (inserts >= 5) exit; next }
  inserts == 0 { print }
' > data/dumps/simplewiki-sql/samples/simplewiki-category-sample.sql
```

## Load Samples into MySQL or MariaDB

Create a local database:

```bash
mysql -u root -p -e "CREATE DATABASE enwiki_sample CHARACTER SET binary;"
```

Load the samples:

```bash
mysql -u root -p enwiki_sample < data/dumps/enwiki-sql/samples/enwiki-category-sample.sql
mysql -u root -p enwiki_sample < data/dumps/enwiki-sql/samples/enwiki-categorylinks-sample.sql
```

Inspect category metadata:

```bash
mysql -u root -p enwiki_sample \
  -e "SELECT cat_id, cat_title, cat_pages, cat_subcats, cat_files FROM category LIMIT 20;"
```

Inspect category membership links:

```bash
mysql -u root -p enwiki_sample \
  -e "SELECT cl_from, cl_to, cl_type FROM categorylinks LIMIT 20;"
```

Find subcategory relations:

```bash
mysql -u root -p enwiki_sample \
  -e "SELECT cl_from, cl_to FROM categorylinks WHERE cl_type = 'subcat' LIMIT 20;"
```

## Export TSV Samples

After loading into MySQL or MariaDB, export smaller TSV files for downstream scripts:

```bash
mkdir -p data/processed/enwiki-sql

mysql -u root -p --batch --raw enwiki_sample \
  -e "SELECT cat_id, cat_title, cat_pages, cat_subcats, cat_files FROM category LIMIT 1000;" \
  > data/processed/enwiki-sql/category-sample.tsv

mysql -u root -p --batch --raw enwiki_sample \
  -e "SELECT cl_from, cl_to, cl_type FROM categorylinks LIMIT 1000;" \
  > data/processed/enwiki-sql/categorylinks-sample.tsv
```

## Notes

- `categorylinks.sql.gz` is much larger than `category.sql.gz`; use `nohup` for full downloads.
- The category dumps are relational data, not article text.
- `categorylinks.cl_from` stores page IDs. Join it with `page.page_id` from `page.sql.gz` when page titles are needed.
- `cl_type = 'subcat'` represents category-to-subcategory membership.
- Full imports can require significant disk space and database tuning.
