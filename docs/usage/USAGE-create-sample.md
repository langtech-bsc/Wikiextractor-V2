# Usage: Create a Sample from a Dump

This guide shows how to create a smaller XML sample from an existing Wikimedia dump using `wikiextractor/utils/sampler/xml_sampler.py`.

The sampler copies the dump header and the first N `<page>` blocks into a new valid XML file. This is useful when the full dump is too large for quick tests.

## Quick start

Create a 100-page XML sample from a compressed dump without keeping a full decompressed copy:

```bash
mkdir -p data/dumps/samples
python wikiextractor/utils/sampler/xml_sampler.py \
  -f <(bzip2 -dc data/dumps/enwiki/enwiki-20261001-pages-articles.xml.bz2) \
  -o data/dumps/samples/enwiki-sample-100-pages.xml \
  -n 100
```

Parse the sample:

```bash
mkdir -p output/enwiki-sample-text templates
python wikiextractor/WikiExtractor.py \
  data/dumps/samples/enwiki-sample-100-pages.xml \
  --output output/enwiki-sample-text \
  --templates templates/enwiki-sample-templates.txt \
  --txt \
  --discard_sections \
  --discard_templates \
  --ignore_templates
```

## Sampler Script

The sampler is located at:

```text
wikiextractor/utils/sampler/xml_sampler.py
```

Command-line options:

- `-f`, `--file`: Input XML file path.
- `-o`, `--output`: Output XML sample path.
- `-n`, `--number`: Number of pages to sample.

The script expects XML text input. If the source dump is compressed as `.bz2`, either stream-decompress it with process substitution or create a decompressed `.xml` file first.

## Create a Sample with Process Substitution

This avoids writing a full decompressed dump to disk. It works in shells that support process substitution, such as `bash` and `zsh`:

```bash
mkdir -p data/dumps/samples
python wikiextractor/utils/sampler/xml_sampler.py \
  -f <(bzip2 -dc data/dumps/enwiki/enwiki-20261001-pages-articles.xml.bz2) \
  -o data/dumps/samples/enwiki-sample-1000-pages.xml \
  -n 1000
```

Run it in the background:

```bash
mkdir -p data/dumps/samples logs
nohup bash -lc 'python wikiextractor/utils/sampler/xml_sampler.py \
  -f <(bzip2 -dc data/dumps/enwiki/enwiki-20261001-pages-articles.xml.bz2) \
  -o data/dumps/samples/enwiki-sample-1000-pages.xml \
  -n 1000' \
  > logs/create-enwiki-sample.log 2>&1 &
```

Follow the log:

```bash
tail -f logs/create-enwiki-sample.log
```

## Create a Sample from a Decompressed XML File

If process substitution is not available, decompress the dump first. This can require a lot of disk space for large dumps:

```bash
bzip2 -dk data/dumps/enwiki/enwiki-20261001-pages-articles.xml.bz2
```

Then create the sample:

```bash
mkdir -p data/dumps/samples
python wikiextractor/utils/sampler/xml_sampler.py \
  -f data/dumps/enwiki/enwiki-20261001-pages-articles.xml \
  -o data/dumps/samples/enwiki-sample-1000-pages.xml \
  -n 1000
```

## Validate the Sample

Check the generated file:

```bash
ls -lh data/dumps/samples/enwiki-sample-1000-pages.xml
```

Confirm that it contains a closing root element:

```bash
tail -n 5 data/dumps/samples/enwiki-sample-1000-pages.xml
```

You should see:

```xml
</mediawiki>
```

## Parse the Sample as Markdown JSONL

```bash
mkdir -p output/enwiki-sample-markdown-jsonl templates
python wikiextractor/WikiExtractor.py \
  data/dumps/samples/enwiki-sample-1000-pages.xml \
  --output output/enwiki-sample-markdown-jsonl \
  --templates templates/enwiki-sample-templates.txt \
  --json \
  --markdown \
  --discard_sections \
  --discard_templates \
  --ignore_templates
```

## Notes

- The sampler takes the first N pages from the dump, not a random sample.
- Increase `-n` when you need more realistic coverage.
- Use a separate template cache for samples when you want fast local iteration.
- A small sample may not contain all template definitions, so template expansion quality can differ from full-dump extraction.
- For final production extraction, run WikiExtractor V2 against the full dump.
