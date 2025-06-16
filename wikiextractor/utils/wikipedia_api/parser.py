import requests
import json
from urllib.parse import urlparse, unquote


API_URL = "https://{lang}.wikipedia.org/w/api.php"


def parse_wiki_url(wiki_url):
    """
    Parse a Wikipedia URL to extract the title of the page.
    
    Args:
        url (str): The URL of the Wikipedia page.
    
    Returns:
        str: The title of the Wikipedia page.
    
    Example:
        >>> parse_wiki_url("https://ca.wikipedia.org/wiki/Imperi_Rom%C3%A0")
        'Imperi Romà'
    """

    # Step 1: Extract title from the URL
    path = urlparse(wiki_url).path              # /wiki/Imperi_Rom%C3%A0
    title = unquote(path.split("/wiki/")[1])    # Imperi Romà

    return title


def get_redirects(title, lang, session=requests.Session(), api_url=API_URL):
    """
    Get redirects for a given Wikipedia page title in a specific language.
    
    Args:
        title (str): The title of the Wikipedia page.
        lang (str): The language code for the Wikipedia page (e.g., 'en' for English).
        session (requests.Session): A requests session object.
        api_url (str): The URL of the Wikipedia API.
    Returns:
        str: The title of the redirected (original) Wikipedia page.
        int: The page ID of the redirected (original) Wikipedia page.
        bool: True if the page was redirected, False otherwise.
    Example:
        >>> get_redirects("Albert Einstein", "en")
        ('Albert Einstein', 736, False)
        
        >>> get_redirects("albert einstein", "en")
        ('Albert Einstein', 736, False) ==> Normalized title
        
        >>> get_redirects("Einstein", "en")
        ('Albert Einstein', 736, True)

    Documentation:
    >>> https://es.wikipedia.org/w/api.php?action=help&modules=query%2Bredirects
    >>> https://es.wikipedia.org/w/api.php?action=help&modules=query
    """
    
    
    params = {
        "action": "query",
        "format": "json",
        "titles": title,
        
        # Include the 'redirects' flag
        "redirects": ""  
    }   


    # api_url = "https://en.wikipedia.org/w/api.php"
    api_url = api_url.format(lang=lang)
    json_data = session.get(url=api_url, params=params).json()

    # print(json.dumps(json_data, indent=2, ensure_ascii=False))
    try:
        query_resp = json_data['query']
        # print(f"query_resp: {query_resp}")
    
        redirect = 'redirects' in query_resp    
        id_, pages = next(iter(json_data['query']['pages'].items()))

        if id_ == '-1':
            # print(f"Error: <{title}> not found in {lang}")
            return None, None, "not_found"

        return pages['title'], pages.get('pageid', None), redirect

    except Exception as e:


        print(json.dumps(json_data, indent=2, ensure_ascii=False))

        print(f"Error: {e}")
        print(f"json_data: {json_data}")
        return None, None, "error"


def get_wiki_lang_title(title, orig_lang, target_lang="", session=requests.Session(), api_url=API_URL):
    """
    Get the title of a Wikipedia page in a different language.

    Args:
        title (str): The title of the Wikipedia page in the original language.
        orig_lang (str): The language code for the original language (e.g., 'en' for Catalan).
        target_lang (str): The language code for the target language (e.g., 'ca' for Catalan).
        session (requests.Session): A requests session object.
        api_url (str): The URL of the Wikipedia API.
    
    Returns:
        str: The original title of the Wikipedia page in the original language.
        int: The page ID of the Wikipedia page in the original language.
        str: The title of the Wikipedia page in the target language.

    Example:
        
        >>> get_wiki_lang_title("Albert Einstein", "ca")
        ('Albert Einstein', 736)
        
        >>> get_wiki_lang_title('Lolita (1962 film)', "ca")
        ('Lolita (pel·lícula del 1962)', 1488066)

        >>> get_wiki_lang_title("Mathematics", "en")
        ('Mathematics', 736, 'Mathematics')
        
        >>> get_wiki_lang_title("Mathematics", "en", "ca")
        ('Mathematics', 18831, 'Mathématiques')

    Documentation:
        https://es.wikipedia.org/w/api.php?action=help&modules=query
    """
    
    if not target_lang:
        target_lang = orig_lang

    params = {
        "action": "query",
        "format": "json",
        "titles": title,
        "prop": "langlinks",
        # "prop": "info",
        "lllang": target_lang,
        "llprop": "url"
    }   

    api_url = api_url.format(lang=orig_lang)

    json_data = session.get(url=api_url, params=params).json()
    id_, value = next(iter(json_data['query']['pages'].items()))

    # ============================================================
    # Page not found
    # ============================================================
    if id_ == '-1':
        return None, None, None


    # No target language links found
    if 'langlinks' not in value:
        target_title = None
    else:
        target_title = value['langlinks'][0]['*']

    return value['title'], value.get('pageid', None), target_title
    