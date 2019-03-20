#! /usr/bin/python
# -*- coding:utf-8 -*-
import re
from typing import Any

full_url_parser = {
    "http://ipblock.chacuo.net/": lambda x: x,
    "http://ipcn.chacuo.net/": None,
    "http://ips.chacuo.net/": None,
    "http://ipblock.chacuo.net/list": None,
    "http://as.chacuo.net/": None,
    "http://as.chacuo.net/company": None,
    "http://as.chacuo.net/list": None,
}

start_url_parser = {
    "http://ipcn.chacuo.net/view/i_": None,
    "http://ipblock.chacuo.net/view/c_": None,
    "http://as.chacuo.net/companyview/s_": None,
    "http://as.chacuo.net/as": None
}

regex_url_parser = {
    r"http://as.chacuo.net/[A-Z]{2}": None
}


def find_parser(url: str) -> Any:
    if url in full_url_parser.keys():
        return full_url_parser[url]

    for start_url in start_url_parser.keys():
        if url.startswith(start_url):
            return start_url_parser[start_url]

    for regex_url in regex_url_parser.keys():
        if re.match(regex_url, url):
            return regex_url_parser[regex_url]
