# Usage: Parse a Downloaded Dump

This guide shows how to parse a downloaded Wikipedia dump into plain text, Markdown, or JSONL with WikiExtractor V2.

## Quick start

Extract a dump to plain text chunks:

```bash
mkdir -p output/enwiki-text templates
python wikiextractor/WikiExtractor.py \
  dumps/enwiki/enwiki-latest-pages-articles.xml.bz2 \
  --output output/enwiki-text \
  --templates templates/enwiki-templates.txt \
  --txt
```

Extract Markdown-formatted article text as JSONL:

```bash
mkdir -p output/enwiki-markdown-jsonl templates
python wikiextractor/WikiExtractor.py \
  dumps/enwiki/enwiki-latest-pages-articles.xml.bz2 \
  --output output/enwiki-markdown-jsonl \
  --templates templates/enwiki-templates.txt \
  --json \
  --markdown
```

## Setup

Install the Python dependencies:

```bash
pip install -r requirements.txt
```

Use a downloaded XML dump as input. The input can be plain XML or compressed as
`.bz2` or `.gz`.

Example input:

```text
dumps/enwiki/enwiki-latest-pages-articles.xml.bz2
```

## Recommended Plain Text Extraction

Use `--txt` for plain text output and enable the cleanup options described in
the README:

```bash
mkdir -p output/enwiki-text templates

python wikiextractor/WikiExtractor.py \
  dumps/enwiki/enwiki-latest-pages-articles.xml.bz2 \
  --output output/enwiki-text \
  --bytes 10M \
  --templates templates/enwiki-templates.txt \
  --txt \
  --discard_sections \
  --discard_templates \
  --ignore_templates
```

This produces chunk files such as:

```text
output/enwiki-text/wiki_00.txt
output/enwiki-text/wiki_01.txt
```

Each extracted document starts with its title. Chunks contain multiple
documents, separated by newlines.

## Markdown Text Extraction

Use `--markdown` when section titles should become Markdown headings. Combine it
with `--txt` to produce Markdown-like text chunks:

```bash
mkdir -p output/enwiki-markdown templates

python wikiextractor/WikiExtractor.py \
  dumps/enwiki/enwiki-latest-pages-articles.xml.bz2 \
  --output output/enwiki-markdown \
  --bytes 10M \
  --templates templates/enwiki-templates.txt \
  --txt \
  --markdown \
  --discard_sections \
  --discard_templates \
  --ignore_templates
```

The page title is written as a level-one heading:

```markdown
# Article title
## Section
### Subsection
```

## Markdown in JSONL

Use `--json --markdown` when each article should be represented as one JSON
object with Markdown-formatted text:

```bash
mkdir -p output/enwiki-markdown-jsonl templates

python wikiextractor/WikiExtractor.py \
  dumps/enwiki/enwiki-latest-pages-articles.xml.bz2 \
  --output output/enwiki-markdown-jsonl \
  --bytes 10M \
  --templates templates/enwiki-templates.txt \
  --json \
  --markdown \
  --discard_sections \
  --discard_templates \
  --ignore_templates
```

This produces `.jsonl` chunks such as:

```text
output/enwiki-markdown-jsonl/wiki_00.jsonl
output/enwiki-markdown-jsonl/wiki_01.jsonl
```

Each JSON object includes:

- `document_id`
- `title`
- `url`
- `language`
- `text`

## Compressed Output

Add `--compress` to write bzip2-compressed output chunks:

```bash
python wikiextractor/WikiExtractor.py \
  dumps/enwiki/enwiki-latest-pages-articles.xml.bz2 \
  --output output/enwiki-text-bz2 \
  --bytes 10M \
  --templates templates/enwiki-templates.txt \
  --txt \
  --compress \
  --discard_sections \
  --discard_templates \
  --ignore_templates
```

Example output:

```text
output/enwiki-text-bz2/wiki_00.txt.bz2
```

## Template Cache

The `--templates` option is strongly recommended. On the first run, WikiExtractor V2 scans the dump and writes template definitions to the selected cache file. Later runs can reuse that cache:

```bash
--templates templates/enwiki-templates.txt
```

Use a separate template cache per dump language and snapshot if template definitions may differ.

## Cleanup Configuration

The cleanup options use configuration files under `wikiextractor/config/`:

- `--discard_sections`: Drops sections such as references or bibliography when their section titles match `discard_sections.txt`.
- `--discard_templates`: Drops entire documents containing templates listed in `discard_templates.txt`. This option only applies when `--templates` is used.
- `--ignore_templates`: Skips expansion for templates listed in `ignore_templates.txt`. This option only applies when `--templates` is used.

Review or extend those files when processing a new language.

## Parse Specific Namespaces

By default, WikiExtractor V2 focuses on normal article pages. To include additional namespaces, pass a comma-separated list:

```bash
python wikiextractor/WikiExtractor.py \
  dumps/enwiki/enwiki-latest-pages-articles.xml.bz2 \
  --output output/enwiki-categories \
  --templates templates/enwiki-templates.txt \
  --txt \
  --namespaces Category
```

## Stream to Standard Output

Use `--output -` for small tests or shell pipelines:

```bash
python wikiextractor/WikiExtractor.py \
  dumps/sample.xml \
  --output - \
  --templates templates/sample-templates.txt \
  --txt \
  --quiet
```

## Troubleshooting

- If extracted text contains many missing words or unresolved templates, rerun with `--templates`.
- If extraction is slow on the first run, wait for template preprocessing to finish. Later runs with the same template cache should be faster.
- If output contains too much reference material, use `--discard_sections` and review `wikiextractor/config/discard_sections.txt`.
- If disambiguation or maintenance pages appear in the corpus, use `--discard_templates` and review `wikiextractor/config/discard_templates.txt`.
- If a `.bz2` file downloaded with the helper script cannot be extracted by bzip2, try parsing it directly with WikiExtractor V2 or follow the README note to remove the `.bz2` extension when the file is actually plain XML.

## Other Possible Use Cases

- Build language-specific plain text corpora for NLP pretraining or evaluation.
- Generate Markdown corpora for retrieval-augmented generation pipelines.
- Export JSONL records for search indexing in Elasticsearch, OpenSearch, Solr, or vector databases.
- Extract article titles, URLs, language codes, and text for metadata catalogs.
- Produce smaller per-language corpora for classroom or benchmark datasets.
- Compare extraction quality across languages by tuning discard and ignore configuration files.
- Embed WikiExtractor V2 in a larger multiprocessing or ETL pipeline after validating the current `--generator` code path for the target version.
