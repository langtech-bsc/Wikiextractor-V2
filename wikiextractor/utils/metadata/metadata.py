import argparse
import bz2
import csv
import gzip
import json
import logging
import os
import xml.etree.ElementTree as ET
from pathlib import Path


FIELDNAMES = [
    "id",
    "title",
    "ns",
    "url",
    "redirect",
    "revision_id",
    "timestamp",
    "text_bytes",
]


def open_xml_dump(input_path):
    """Open XML dumps stored as plain XML, gzip, or bzip2."""
    input_path = str(input_path)
    if input_path == "-":
        return os.fdopen(os.dup(0), "rb")
    if input_path.endswith(".bz2"):
        return bz2.open(input_path, "rb")
    if input_path.endswith(".gz"):
        return gzip.open(input_path, "rb")
    return open(input_path, "rb")


def _text(elem, path):
    found = elem.find(path)
    return found.text if found is not None else None


def _extract_page_row(elem, url_base):
    page_id = _text(elem, "./{*}id")
    title = _text(elem, "./{*}title")
    ns = _text(elem, "./{*}ns")

    redirect = elem.find("./{*}redirect")
    redirect_title = redirect.get("title") if redirect is not None else None

    revision = elem.find("./{*}revision")
    revision_id = None
    timestamp = None
    text_bytes = None
    if revision is not None:
        revision_id = _text(revision, "./{*}id")
        timestamp = _text(revision, "./{*}timestamp")
        text = revision.find("./{*}text")
        if text is not None:
            text_bytes = text.get("bytes")

    return {
        "id": page_id,
        "title": title,
        "ns": ns,
        "url": url_base.format(id=page_id) if page_id else None,
        "redirect": redirect_title,
        "revision_id": revision_id,
        "timestamp": timestamp,
        "text_bytes": text_bytes,
    }


def iter_page_metadata(
    xml_file,
    max_pages=None,
    url_base="https://ca.wikipedia.org/wiki?curid={id}",
    print_every=100000,
):
    """Yield page metadata from a Wikipedia XML dump."""
    page_count = 0
    with open_xml_dump(xml_file) as handle:
        context = ET.iterparse(handle, events=("end",))
        for event, elem in context:
            if not elem.tag.endswith("page"):
                continue

            yield _extract_page_row(elem, url_base)
            page_count += 1

            if print_every and page_count % print_every == 0:
                logging.info("Processed %d pages", page_count)

            elem.clear()

            if max_pages and page_count >= max_pages:
                break


def extract_page_metadata(
    xml_file,
    max_pages=None,
    url_base="https://ca.wikipedia.org/wiki?curid={id}",
):
    """Extract page metadata from a Wikipedia XML dump into a list."""
    return list(iter_page_metadata(xml_file, max_pages=max_pages, url_base=url_base))


def write_metadata(rows, output_path, output_format="csv"):
    """Write metadata rows as csv, jsonl, or json."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if output_format == "csv":
        with output_path.open("w", encoding="utf-8", newline="") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=FIELDNAMES)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
    elif output_format == "jsonl":
        with output_path.open("w", encoding="utf-8") as outfile:
            for row in rows:
                outfile.write(json.dumps(row, ensure_ascii=False) + "\n")
    elif output_format == "json":
        with output_path.open("w", encoding="utf-8") as outfile:
            json.dump(list(rows), outfile, ensure_ascii=False, indent=2)
    else:
        raise ValueError(f"Unsupported output format: {output_format}")


def extract_metadata_to_file(
    input_path,
    output_path,
    n_pages=None,
    url_base="https://ca.wikipedia.org/wiki?curid={id}",
    output_format="csv",
    print_every=100000,
):
    """Extract metadata from a dump and write it to a file."""
    rows = iter_page_metadata(
        input_path,
        max_pages=n_pages,
        url_base=url_base,
        print_every=print_every,
    )
    write_metadata(rows, output_path, output_format=output_format)


def main():
    """Extract metadata from the first N pages of a Wikipedia XML dump."""
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s][%(filename)s][%(levelname)s] - %(message)s",
    )
    log = logging.getLogger(__name__)

    parser = argparse.ArgumentParser(
        description="Extract page metadata from a Wikipedia XML dump."
    )
    parser.add_argument(
        "-f",
        "--file",
        type=str,
        required=True,
        help="Path to the input XML dump. Supports .xml, .xml.gz, and .xml.bz2.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        required=True,
        help="Path to the output metadata file.",
    )
    parser.add_argument(
        "-n",
        "--number",
        type=int,
        default=None,
        help="Number of pages to process. Omit to process the full dump.",
    )
    parser.add_argument(
        "--url-base",
        type=str,
        default="https://ca.wikipedia.org/wiki?curid={id}",
        help="URL template used to build page URLs. Use {id} as the page id placeholder.",
    )
    parser.add_argument(
        "--format",
        choices=("csv", "jsonl", "json"),
        default="csv",
        help="Output format.",
    )
    parser.add_argument(
        "--print-every",
        type=int,
        default=100000,
        help="Log progress every N pages. Use 0 to disable progress logs.",
    )

    args = parser.parse_args()

    log.info("Input file: %s", args.file)
    log.info("Output file: %s", args.output)
    log.info("Number of pages: %s", args.number if args.number else "all")
    log.info("Output format: %s", args.format)

    extract_metadata_to_file(
        input_path=args.file,
        output_path=args.output,
        n_pages=args.number,
        url_base=args.url_base,
        output_format=args.format,
        print_every=args.print_every,
    )


if __name__ == "__main__":
    main()
