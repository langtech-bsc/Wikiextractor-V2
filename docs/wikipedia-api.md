# Wikipedia API Utilities

This module provides utility functions to work with Wikipedia's API. It allows parsing Wikipedia URLs, resolving redirects, and retrieving titles in different languages.

## Functions

* [`parse_wiki_url(wiki_url)`](#parse_wiki_url)
* [`get_redirects`](#get_redirects)
* [`get_wiki_lang_title`](#get_wiki_lang_title)


### `parse_wiki_url`

`parse_wiki_url(wiki_url)`

Extracts the page title from a Wikipedia URL.

#### Parameters
- `wiki_url` (str): A full Wikipedia URL.

#### Returns
- `str`: Decoded title from the URL.

#### Example

```python
parse_wiki_url("https://ca.wikipedia.org/wiki/Imperi_Rom%C3%A0")
# Output: 'Imperi Romà'
```


### `get_redirects`

`get_redirects(title, lang, session=requests.Session(), api_url=API_URL)`

Resolves a Wikipedia page title, handling redirects and normalization.

#### Parameters

* `title` (str): The Wikipedia page title.
* `lang` (str): Wikipedia language code (e.g., "en", "ca").
* `session` (requests.Session, optional): Custom session for requests.
* `api_url` (str): Template URL for Wikipedia API.

#### Returns

* `str`: Canonical page title.
* `int`: Page ID.
* `bool`/`str`: Redirect status (`True`, `False`, or `'not_found'`/`'error'`).

#### Examples

```python
get_redirects("Albert Einstein", "en")
# Output: ('Albert Einstein', 736, False)

get_redirects("Einstein", "en")
# Output: ('Albert Einstein', 736, True)
```

---

### `get_wiki_lang_title`


`get_wiki_lang_title(title, orig_lang, target_lang="", session=requests.Session(), api_url=API_URL)`

Fetches the equivalent title of a Wikipedia page in another language.

#### Parameters

* `title` (str): Original Wikipedia page title.
* `orig_lang` (str): Language code of the original title.
* `target_lang` (str): Desired language code for translation (defaults to original).
* `session` (requests.Session, optional): Custom session.
* `api_url` (str): Wikipedia API URL template.

#### Returns

* `str`: Title in the original language.
* `int`: Page ID.
* `str`: Title in the target language (or `None` if not found).

#### Examples

```python
get_wiki_lang_title("Mathematics", "en", "fr")
# >>> Output: ('Mathematics', 18831, 'Mathématiques')

get_wiki_lang_title("Albert Einstein", "ca")
# >>> Output: ('Albert Einstein', 736, None)
```


## Notes

* Requires internet access and Wikipedia's API availability.
* Default session uses `requests.Session()` for better performance in repeated calls.

## API Reference

* [Wikipedia API Docs (query)](https://es.wikipedia.org/w/api.php?action=help&modules=query)
* [Wikipedia API Docs (redirects)](https://es.wikipedia.org/w/api.php?action=help&modules=query%2Bredirects)

