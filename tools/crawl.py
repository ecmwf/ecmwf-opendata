#!/usr/bin/env python3
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from ecmwf.opendata import Client

url = urlparse(Client().url)
top = url.scheme + "://" + url.netloc


def crawl(url):
    print(f"{top}{url}")
    r = requests.get(f"{top}{url}")
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    for link in soup.find_all("a"):
        href = link.get("href")
        if href is not None and not url.startswith(href):
            if href.startswith("javascript:"):
                continue
            if href.endswith("/"):
                crawl(href)
            else:
                if href.endswith(".index"):
                    print(f"{top}{href}")


crawl(url.path + ("" if url.path.endswith("/") else "/"))
