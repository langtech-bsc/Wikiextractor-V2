# Usage: Download Wikipedia Dumps

This guide explains how to choose and download Wikimedia dump files for WikiExtractor V2.

## Quick start

Resolve the latest English Wikipedia article snapshot, then download the dated dump file:

> Warning dump size is ~25GB.

```bash
mkdir -p data/dumps/enwiki logs

latest_url="https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-pages-articles.xml"
rss_url="${latest_url}.bz2-rss.xml"
download_url=$(curl -Ls "$rss_url" | sed -n 's/.*href="\([^"]*pages-articles\.xml\.bz2\)".*/\1/p' | head -n 1)
dump_file="data/dumps/enwiki/$(basename "$download_url")"

curl -L -o "$dump_file" "$download_url"
```

Run the same download in the background:

```bash
mkdir -p data/dumps/enwiki logs

latest_url="https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-pages-articles.xml"
rss_url="${latest_url}.bz2-rss.xml"
download_url=$(curl -Ls "$rss_url" | sed -n 's/.*href="\([^"]*pages-articles\.xml\.bz2\)".*/\1/p' | head -n 1)
dump_file="data/dumps/enwiki/$(basename "$download_url")"

nohup curl -L \
  -o "$dump_file" \
  "$download_url" \
  > logs/download-wikipedia.log 2>&1 &
```

Download selected Wikipedia article dumps with the repository helper:

```bash
mkdir -p data/dumps
python wiki_dump_download.py \
  --download wikipedia \
  --check-langs en,ca \
  --output-path data/dumps/
```

Run a long download in the background with `nohup`:

```bash
mkdir -p data/dumps logs
nohup python wiki_dump_download.py \
  --download wikipedia \
  --check-langs en,ca \
  --output-path data/dumps/ \
  > logs/download-wikipedia.log 2>&1 &
```

Follow the log while it runs:

```bash
tail -f logs/download-wikipedia.log
```

WikiExtractor V2 parses XML dumps, including compressed `.bz2` and `.gz` files. For most article extraction workflows, start with a `pages-articles` dump for the target language.

## Choose a Dump Type

Common Wikimedia dump files:

- `pages-articles.xml.bz2`: Current article pages, excluding discussion and most non-content pages. This is the recommended input for most plain text, Markdown, and JSONL article extraction jobs.
- `pages-articles-multistream.xml.bz2`: Current article pages split into multiple compressed streams. Useful when a downstream workflow also needs the companion index file for random access.
- `pages-meta-current.xml.bz2`: Current revisions for all pages and namespaces. This is larger than `pages-articles` and usually includes content that is not needed for article-only corpora.
- `pages-meta-history.xml.*`: Full revision history. This is very large and is not recommended unless the use case needs historical versions.
- `stub-articles.xml.gz`: Page metadata and revision stubs. This can be useful for metadata tests, but it is not a replacement for full article text extraction.

For a language-specific Wikipedia dump, use the language code in the dump URL. For example, English Wikipedia uses `enwiki`, Catalan uses `cawiki`, and Spanish uses `eswiki`.

## Download Manually

The Wikimedia dump browser is available at:

```text
https://dumps.wikimedia.org/
```

The latest dump index for a project is available under:

```text
https://dumps.wikimedia.org/<project>/latest/
```

Examples:

```text
https://dumps.wikimedia.org/enwiki/latest/
https://dumps.wikimedia.org/cawiki/latest/
https://dumps.wikimedia.org/eswiki/latest/
```

## Resolve the Latest Snapshot

For reproducible downloads, first read the RSS metadata for the `latest` alias, then download the dated snapshot file from the RSS item.

Build the RSS URL by appending `-rss.xml` to the dump URL:

```bash
latest_url="https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-pages-articles.xml"
rss_url="${latest_url}.bz2-rss.xml"
curl -L "$rss_url"
```

The RSS XML contains a dated dump link, for example:

```xml
<link>http://download.wikimedia.org/enwiki/20261001</link>
<description>&lt;a href="http://download.wikimedia.org/enwiki/20261001/enwiki-20261001-pages-articles.xml.bz2"&gt;enwiki-20261001-pages-articles.xml.bz2&lt;/a&gt;</description>
```

Extract and download that dated file:

```bash
mkdir -p data/dumps/enwiki

latest_url="https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-pages-articles.xml"
rss_url="${latest_url}.bz2-rss.xml"
download_url=$(curl -Ls "$rss_url" | sed -n 's/.*href="\([^"]*pages-articles\.xml\.bz2\)".*/\1/p' | head -n 1)
dump_file="data/dumps/enwiki/$(basename "$download_url")"

curl -L -o "$dump_file" "$download_url"
```

For very large dumps, prefer a resumable downloader after resolving the dated URL:

```bash
mkdir -p data/dumps/enwiki

latest_url="https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-pages-articles.xml"
rss_url="${latest_url}.bz2-rss.xml"
download_url=$(curl -Ls "$rss_url" | sed -n 's/.*href="\([^"]*pages-articles\.xml\.bz2\)".*/\1/p' | head -n 1)
dump_file="data/dumps/enwiki/$(basename "$download_url")"

wget -c -O "$dump_file" "$download_url"
```

## Download with `wiki_dump_download.py`

The repository includes `wiki_dump_download.py`, a helper script based on the `wiki-data-dump` package.

Install the project requirements first:

```bash
pip install -r requirements.txt
```

If `wiki-data-dump` is not already available in your environment, install it too:

```bash
pip install wiki-data-dump
```

Check whether selected languages are available across Wikimedia projects:

```bash
python wiki_dump_download.py --check-langs en,ca,es
```

Download Wikipedia article dumps for selected languages:

```bash
mkdir -p data/dumps/
python wiki_dump_download.py \
  --download wikipedia \
  --check-langs en,ca,es \
  --output-path data/dumps/
```

Download all available Wikipedia article dumps:

```bash
mkdir -p data/dumps/
python wiki_dump_download.py \
  --download wikipedia \
  --output-path data/dumps/
```

For unattended downloads, run the command with `nohup` and redirect output to a log file:

```bash
mkdir -p data/dumps logs
nohup python wiki_dump_download.py \
  --download wikipedia \
  --output-path data/dumps/ \
  > logs/download-all-wikipedia.log 2>&1 &
```

The `--download` option accepts these project types:

- `wikipedia`
- `wikibooks`
- `wikinews`
- `wikisource`
- `wiktionary`
- `wikiquote`
- `wikimedia`
- `wikiversity`
- `wikivoyage`

## Validate the Download

Check that the file exists and has a non-zero size:

```bash
ls -lh data/dumps/enwiki/enwiki-*-pages-articles.xml.bz2
```

Optionally test that bzip2 can read the file:

```bash
bzip2 -tv data/dumps/enwiki/enwiki-*-pages-articles.xml.bz2
```

Some dumps downloaded through `wiki-data-dump` may appear with a `.bz2` extension even when local extraction tools cannot read them as bzip2 streams.
The README notes that, in that case, removing the `.bz2` extension can expose a plain XML file that WikiExtractor V2 can parse.

## Recommended Layout

Keep raw dumps, templates, and extracted output separate:

```text
data/dumps/
  enwiki/
    enwiki-20261001-pages-articles.xml.bz2
  templates/
    enwiki-templates.txt
  output/
    enwiki-text/
    enwiki-markdown-jsonl/
```

This keeps expensive downloads reusable and lets repeated extraction jobs share the same template cache.
