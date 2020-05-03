import re

from bs4 import BeautifulSoup as bs

from lang.langs import Lang


# ----------------------------------------------------------------------------------------------------
def extract_added_words(lang: Lang, html_str: str):
    """
    extract words that added to the revision from string of html page

    if html not exists return empty string

    param lang: language

    param html_str: string of page of html (the change of the revision)

    return: string of words that added to the revision
    """

    try:
        soup = bs(html_str, 'html.parser')
        data_added = " "

        for tds in soup.find_all("td", { "class": "diff-addedline" }):
            for ins in tds.find_all("ins", { "class": "diffchange diffchange-inline" }):
                data_added += str(ins.text) + " "

        if lang.filter is not None:
            data_added = re.sub(lang.filter, repl="", string=data_added)  # remove filter

        # find all links and extract theirs hosts
        link_pattern = r'(?:(?:(?:https?|ftp)://(?:www\.)?)|(?:www\.))([\w\-?=%.]+)[\w/\-?=%.&|+]*'
        links_hosts = re.findall(link_pattern, data_added)
        data_added = re.sub(link_pattern, repl="", string=data_added)  # remove all links

        added_words = " ".join(re.findall(lang.extract_words_regex, data_added))
        added_words = added_words.lower()
        added_words += " " + " ".join(links_hosts) # add hosts to words
        return added_words.strip()
    except:
        return ""


# ----------------------------------------------------------------------------------------------------
def extract_rev_id(lang: Lang, comment: str):
    """
    extract rev id from comment of the revision in case of vandalism

    param lang: language (different regex for any language)

    param comment: the comment of the revision

    return rev id (int)
    """

    pattern = lang.extract_rev_regex
    result = re.search(pattern, comment)
    if result is None:
        return None
    return int(result.group(1))

