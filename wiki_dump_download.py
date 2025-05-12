from wiki_data_dump import WikiDump, File
import re
import os
import argparse
from typing import List

WIKI_PATTERNS = {
    "wikipedia": "[a-z]{2,3}wiki$",
    "wikibooks": "[a-z]{2,3}wikibooks$",
    "wikinews": "[a-z]{2,3}wikinews$",
    "wikisource": "[a-z]{2,3}wikisource$",
    "wiktionary": "[a-z]{2,3}wiktionary$",
    "wikiquote": "[a-z]{2,3}wikiquote$",
    "wikimedia": "[a-z]{2,3}wikimedia$",
    "wikiversity": "[a-z]{2,3}wikiversity$",
    "wikivoyage": "[a-z]{2,3}wikivoyage$",
}

WIKI = WikiDump()


def filter_wikis(wikis: List[str], pattern: str, valid_langs: List[str] = None) -> List[str]:
    regex = re.compile(pattern)
    if valid_langs is not None:
        return [w for w in wikis if regex.match(w) and w.split("wik")[0] in valid_langs]
    else:
        return [w for w in wikis if regex.match(w)]


def check_lang_availability(langs: List[str]):
    for k in WIKI_PATTERNS:
        matched_wikis = filter_wikis(WIKI.wikis, WIKI_PATTERNS[k], langs)
        found_langs = {w.split("wik")[0] for w in matched_wikis}
        missing_langs = [l for l in langs if l not in found_langs]
        print(f"[INFO] {len(found_langs)} languages available for {k}. Missing languages: {missing_langs}")


def download(wiki_type: str, output_path: str, langs: List[str]):
    print(f"[INFO] Using mirror: {WIKI.mirror}")

    if langs:
        print(f"[INFO] Filtering languages: {langs}")
        filtered_wikis = filter_wikis(WIKI.wikis, WIKI_PATTERNS[wiki_type], langs)
    else:
        filtered_wikis = filter_wikis(WIKI.wikis, WIKI_PATTERNS[wiki_type])

    for w in filtered_wikis:
        xml_articles_dump_job = WIKI[w, "articlesdump"]
        orig_files = xml_articles_dump_job.get_files(re.compile(r'.*'))
        print(f"[INFO] Original files in job ({len(orig_files)}): {orig_files}")

        pages_articles: List[File] = xml_articles_dump_job.get_files(
            re.compile(r".*pages-articles[0-9]*\.xml.*\.bz2$")
        )
        print(f"[INFO] Downloading {len(pages_articles)} articles from {w}")

        for file in pages_articles:
            file_path = os.path.join(output_path, os.path.basename(file.url))
            WIKI.download(file, destination=file_path).join()
            print(f"[INFO] Downloaded {os.path.basename(file.url)} to {file_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download Wikimedia project dumps.")
    parser.add_argument("--check-langs", type=str, required=False, help="Comma-separated list of ISO 639-1 codes to check availability.")
    parser.add_argument("--download", type=str, choices=WIKI_PATTERNS.keys(), help="Download the articles dump for the specified wiki project type.")
    parser.add_argument("--output-path", type=str, help="Output path for dumps")

    args = parser.parse_args()
    lang_list = args.check_langs.split(",") if args.check_langs else []

    if args.check_langs and not args.download:
        check_lang_availability(lang_list)

    if args.download:
        download(args.download, args.output_path, lang_list)
