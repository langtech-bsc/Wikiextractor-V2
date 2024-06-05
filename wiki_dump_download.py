"""
This script downloads the "pages-articles.xml.bz2" dumps from various Wikimedia projects.
These dumps include current revisions only, excluding talk or user pages.
See https://en.wikipedia.org/wiki/Wikipedia:Database_download for more details.

The script filters wikis based on available language codes and project types, and downloads
the relevant XML dump files for processing by WikiExtractor.

Usage:
    - The script first checks the availability of languages for each project type.
    - Then it downloads the Wikipedia articles dumps for available languages.

Dependencies:
    - wiki_data_dump: A module to interact with Wikimedia dump files.
    - re: For regular expression matching.
    - typing.List: For type hinting lists.
"""

from wiki_data_dump import WikiDump, File
import re
import argparse
from typing import List

ALIA_LANGS = {
    "bg": "Bulgarian",
    "cs": "Czech",
    "da": "Danish",
    "el": "Greek",
    "et": "Estonian",
    "fi": "Finnish",
    #"ga": "Irish",
    "hr": "Croatian",
    "hu": "Hungarian",
    "lt": "Lithuanian",
    "lv": "Latvian",
    "mt": "Maltese",
    "nl": "Dutch",
    "pl": "Polish",
    "pt": "Portuguese",
    "ro": "Romanian",
    "sk": "Slovak",
    "sl": "Slovenian",
    "sv": "Swedish",
    "uk": "Ukrainian",
    "sr": "Serbian",
    #"sh": "Serbo-Croatian",
    #"nn": "Norwegian Nynorsk",
    "no": "Norwegian Bokmål",
    "eu": "Basque",
    "ca": "Catalan",
    "gl": "Galician",
    #"cy": "Welsh",
    #"oc": "Occitan",
    "ru": "Russian",
    "en": "English",
    "de": "German",
    "fr": "French",
    "es": "Spanish",
    "it": "Italian"
}

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
    """
    Filter wikis based on a regular expression pattern and optional valid languages.

    Args:
        wikis (List[str]): List of wiki URLs.
        pattern (str): Regular expression pattern to match wiki URLs.
        valid_langs (List[str], optional): List of valid language codes to filter the wikis. Defaults to None.

    Returns:
        List[str]: List of filtered wiki URLs.
    """
    regex = re.compile(pattern)
    if valid_langs is not None:
        return [w for w in wikis if regex.match(w) and w.split("wik")[0] in valid_langs]
    else:
        return [w for w in wikis if regex.match(w)]


def check_lang_availability():
    """
    Check the availability of languages for each project type and print missing languages.

    This function iterates over the defined WIKI_PATTERNS, filters the wikis,
    and identifies any missing languages from the ALIA_LANGS.
    """
    for k in WIKI_PATTERNS:
        filter_w = filter_wikis(WIKI.wikis, WIKI_PATTERNS[k], ALIA_LANGS.keys())
        miss = [l for l in ALIA_LANGS.keys() if not any(l == w.split("wik")[0] for w in filter_w)]
        print(f"[INFO] {len(filter_w)} languages available for {k}. Missing languages: {miss}")


def download(wiki_type: str, output_path: str):
    """
    Download the articles dump files for a specific wiki project type.

    Args:
        wiki_type (str): The type of wiki project to download (e.g., "wikipedia", "wikibooks").
    """
    print(f"[INFO] Using mirror: {WIKI.mirror}")
    # Get all Wikis without language filtering
    filter_w = filter_wikis(WIKI.wikis, WIKI_PATTERNS[wiki_type], None)
    # Download wikis for each language
    for w in filter_w:
        # Uncomment the following line to see all files for a given language
        # print(WIKI.get_wiki(w).jobs.keys())
        xml_articles_dump_job = WIKI[w, "articlesdump"]
        orig_files = xml_articles_dump_job.get_files(re.compile(r'.*'))
        print(f"[INFO] Original files in job ({len(orig_files)}): {orig_files}")
        # Filter only necessary files
        pages_articles: List[File] = xml_articles_dump_job.get_files(
            re.compile(r".*pages-articles[0-9]*\.xml.*\.bz2$")
        )
        print(f"[INFO] Downloading {len(pages_articles)} articles from {w}")
        # Download
        for file in pages_articles:
            WIKI.download(file, destination=output_path).join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download Wikimedia project dumps.")
    parser.add_argument("--check-langs", action="store_true", help="Check the availability of languages for each project type.")
    parser.add_argument("--download", type=str, choices=WIKI_PATTERNS.keys(), help="Download the articles dump for the specified wiki project type.")
    parser.add_argument("--output-path", type=str, action="store_true", help="Output path for dumps")

    args = parser.parse_args()

    if args.check_langs:
        check_lang_availability()

    if args.download:
        download(args.download, args.output_path)
