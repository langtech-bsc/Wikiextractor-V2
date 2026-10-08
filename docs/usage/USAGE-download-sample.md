# Usage: Download Sample Dumps

This guide shows how to download smaller Wikimedia dumps for testing WikiExtractor V2 workflows before running large jobs such as English Wikipedia.

## Quick start

Resolve and download the latest Test Wikipedia article snapshot. This is a small real dump, useful for smoke tests:

```bash
mkdir -p data/dumps/testwiki logs

latest_url="https://dumps.wikimedia.org/testwiki/latest/testwiki-latest-pages-articles.xml"
rss_url="${latest_url}.bz2-rss.xml"
download_url=$(curl -Ls "$rss_url" | sed -n 's/.*href="\([^"]*pages-articles\.xml\.bz2\)".*/\1/p' | head -n 1)
dump_file="data/dumps/testwiki/$(basename "$download_url")"

nohup curl -L \
  -o "$dump_file" \
  "$download_url" \
  > logs/download-testwiki.log 2>&1 &
```

Resolve and download the latest Simple English Wikipedia article snapshot. This is larger than `testwiki`, but still much smaller than `enwiki`:

```bash
mkdir -p data/dumps/simplewiki logs

latest_url="https://dumps.wikimedia.org/simplewiki/latest/simplewiki-latest-pages-articles.xml"
rss_url="${latest_url}.bz2-rss.xml"
download_url=$(curl -Ls "$rss_url" | sed -n 's/.*href="\([^"]*pages-articles\.xml\.bz2\)".*/\1/p' | head -n 1)
dump_file="data/dumps/simplewiki/$(basename "$download_url")"

nohup curl -L \
  -o "$dump_file" \
  "$download_url" \
  > logs/download-simplewiki.log 2>&1 &
```

Follow a background download:

```bash
tail -f logs/download-testwiki.log
```

## Why Use a Smaller Dump

English Wikipedia article dumps such as `enwiki-20261001-pages-articles.xml.bz2` are large. Use smaller dumps to validate:

- Download commands and directory layout.
- Dependency installation.
- WikiExtractor V2 parsing options.
- Template cache behavior.
- Markdown, plain text, and JSONL output formats.
- Background execution with `nohup`.

## Recommended Sample Dumps

Use article dumps when testing extraction, because they contain article text:

```text
https://dumps.wikimedia.org/testwiki/latest/testwiki-latest-pages-articles.xml.bz2-rss.xml
https://dumps.wikimedia.org/simplewiki/latest/simplewiki-latest-pages-articles.xml.bz2-rss.xml
```

Use the RSS XML to find the dated dump file, such as `testwiki-20260901-pages-articles.xml.bz2`, then download that versioned file.

Avoid relying on an `enwiki-latest-abstract.xml.gz` file for current workflows. The current `enwiki/latest` dump index may not provide that file. For WikiExtractor V2 tests, prefer a smaller `pages-articles.xml.bz2` dump or create a sample from an already downloaded dump.

## Check the Download

Confirm that the file exists:

```bash
ls -lh data/dumps/testwiki/testwiki-*-pages-articles.xml.bz2
```

Check whether bzip2 can read it:

```bash
bzip2 -tv data/dumps/testwiki/testwiki-*-pages-articles.xml.bz2
```

## Parse the Sample Dump

Run a small extraction test:

```bash
mkdir -p output/testwiki-text templates
dump_file=$(ls data/dumps/testwiki/testwiki-*-pages-articles.xml.bz2 | head -n 1)

python wikiextractor/WikiExtractor.py \
  "$dump_file" \
  --output output/testwiki-text \
  --templates templates/testwiki-templates.txt \
  --txt \
  --discard_sections \
  --discard_templates \
  --ignore_templates
```

For Markdown JSONL:

```bash
mkdir -p output/testwiki-markdown-jsonl templates
dump_file=$(ls data/dumps/testwiki/testwiki-*-pages-articles.xml.bz2 | head -n 1)

python wikiextractor/WikiExtractor.py \
  "$dump_file" \
  --output output/testwiki-markdown-jsonl \
  --templates templates/testwiki-templates.txt \
  --json \
  --markdown \
  --discard_sections \
  --discard_templates \
  --ignore_templates
```

## Next Step

If the small dump works, use the same command structure with a larger dump such as `simplewiki`, `cawiki`, `eswiki`, or `enwiki`.
