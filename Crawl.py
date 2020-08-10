import time
import requests
import re
import argparse
from bs4 import BeautifulSoup
import urllib



def find_original_url(paragraphs,article,typo):
    """
    This function is used when the regex removed a url letters those contain parentheses
    it gets the original url without removing any parentheses
    Args:
        paragraphs : [set of tags <p>] the parsed paragraph of the content of the body.
        article : [str] target article need to be corrected, its link distorted due to parentheses.
        typo : [int] index of the last correct letter in the article's url.

    Returns:
        article : [str] corrected article url.
    """
    article = article[:typo-1]
    for p in paragraphs:
        anchors = p.find(href = re.compile('^/wiki/'))
        if anchors:
            article_link = anchors.get('href')
            if(article_link.find(article) != -1):
                return article_link
    return article

def get_first_anchor(url):
    """
    This function is getting the first anchor at the body of the give article.
    Args:
        url : [str] hyperlink for the article which is being visited.
    Returns:
        first_anchor : [str] first anchor in the article which is to be visited next timestamp.
    """
    response = requests.get(url)
    inner_html = response.text
    soup = BeautifulSoup(inner_html, "html.parser")
    content = soup.find(id="mw-content-text").find(class_="mw-parser-output")
    paragraphs = content.find_all("p", recursive=False)
    article_anchor = None
    for p in paragraphs:
        p = str(p)
        p = re.sub(r'\([^}]*\)', '', p) 
        p = BeautifulSoup(p, "html.parser")
        anchors = p.find(href = re.compile('^/wiki/'))
        if anchors:
            article_anchor = anchors.get('href')
            typo = article_anchor.find(' ')
            if (typo != -1):
                article_anchor = find_original_url(paragraphs,article_anchor,typo)
            break
    if not article_anchor:
        return
    first_anchor = urllib.parse.urljoin('https://en.wikipedia.org/', article_anchor)
    return first_anchor


def check_anchor(visited_anchors, target_anchor, limit=100):
    """
    Scraping eac dose the core of the script (scraping/crawling loop)
    Args:
        None.
    Returns:
        None.
    """
    if len(visited_anchors) >= limit:
        print("Reached out the limit of search try another link :( !")
        return False
    if visited_anchors[-1] == target_anchor:
        print(f"\n {visited_anchors[-1]}")
        print("\n OOOO Congrats found it the Philosophy!")
        return False
    elif visited_anchors[-1] in visited_anchors[:-1]:
        print("Stuck in a loop cannot found it :( !")
        return False
    else:
        return True


def get_philosophy(entry_anchor):
    """
    This function dose the core of the script (scraping/crawling loop)
    Args:
        None.
    Returns:
        None.
    """
    anchors = [entry_anchor]
    anchor = entry_anchor
    target = "https://en.wikipedia.org/wiki/Philosophy"
    while check_anchor(anchors, target):
        print(f' {anchor}')
        anchor = get_first_anchor(anchors[-1])
        if not anchor:
            print("Article without links, cannot continue :( !")
            break
        anchors.append(anchor)
        time.sleep(0.5)
    return

if (__name__ == "__main__"):
    parser = argparse.ArgumentParser(description='Entry url from wikipedia to start scraping till Philosophy.')
    parser.add_argument('entry_url', metavar='url', type=str, default="https://en.wikipedia.org/wiki/Philosophy_of_science",
                    help='First url to start from it the scraping process till find Philosophy')
    args = parser.parse_args()
    entry = args.entry_url
    print(f" Entry url is : {entry} \n")
    get_philosophy(entry)
    print("\n GOOD BYE!")
