# fudge.py - Fudge Report helper functions.
import urllib2 as u2
import string
import re
import random


def get_titles (url):
    # Url is RSS feed.
    # Works for reddit, HN, Google.
    titles = [l[1:-2] for l in u2.urlopen (url).read().split ("title")]
    titles = [links[i] for i in range (1, len(links), 2)]
    # Returns all link titles.
    return titles

def get_lead_image (url):
    # Url is a news article.
    # Returns link to news articles' lead image. 
    # Readability info:
    # https://www.readability.com/api/content/v1/parser?url=http://www.abc.net.au/radionational/programs/bodysphere/traumatic-adaptations/4854182
    token = # "{{ Readability API key }}"
    call = "https://www.readability.com/api/content/v1/parser?url={url}&token={token}".format( 
        url=url, 
        token=token)
    JSON = u2.urlopen (call).read ()
    fields = JSON.split ("\n")
    l = None
    try:
        for f in fields:
            f = f.strip ().replace ("\"","")
            k = f.split (":")
            if "lead_image_url" in k:
                return ":".join(k[1:]).strip ().strip (",")
    except:
        return None

def get_links (url):
    # Takes RSS feed. 
    # Returns a (title, url) list.
    items = u2.urlopen (url).read().split("<item>")
    links = list ()
    for i in range (1, len (items)):
        try:
            item = items[i]
            l = re.findall ("<link>(.*?)</link>", item)
            t = re.findall ("<title>(.*?)</title>", item)
            if l is None or t is None:
                continue
            l = l[0]
            t = "".join(t[0].split (' - ')[:-1])
            token = "url="
            link = l[l.find(token) + len (token):]
            links.append ((t,link))
        except:
            continue
    return links


def get_context(query="intitle:fudge", title="fudge report"):
    # Grab all RSS links from Google News. 
    RSS = """
        https://news.google.com/news/feeds?hl=en&gl=us&authuser=0&q={query}&num=100&um=1&ie=UTF-8&output=rss
    """.format (query=query).strip()
    links = get_links (RSS)

    # Put all links in context dict for Django.
    urls = list()
    for link in links:
        print link
        urls.append ({
            'url': link[1],
            'title': link[0]
            })

    # Find a good main image.
    main = sorted (links, key=lambda f: len(f[0]))[0] # Shorter title is better
    x = 0
    s = main[0]
    img = get_lead_image (main[1])
    # A printable title is more likely to be in English.
    while img == "null" or sum ([c in string.printable for c in s]) != len (s):
        x += 1
        main = sorted (links, key=lambda f: len(f[0]))[x]
        s = main [0]
        img = get_lead_image (main[1])
    main = {
        'url': main[1],
        'title': main[0],
        'image': img } 

    # Get ready for Template/Context.
    d = dict()
    l = len (urls) / 3
    d["left"] = urls[:l]
    d["right"] = urls[l:2*l]
    d["middle"] = urls[2*l:]
    d["main"] = main
    d["title"] = title
    return d
