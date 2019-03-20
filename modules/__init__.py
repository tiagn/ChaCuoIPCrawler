#! /usr/bin/python
# -*- coding:utf-8 -*-
import re
from typing import Any
from modules import iso_3166_1
from modules import country_ip_range
from modules import domestic_operator_ip_range

full_url_parser = {
    "http://ipblock.chacuo.net/": country_ip_range.Parser().parse,
    "http://ipcn.chacuo.net/": domestic_operator_ip_range.Parser().parse,
    "http://ips.chacuo.net/": lambda x: x,
    "http://ipblock.chacuo.net/list": lambda x: x,
    "http://as.chacuo.net/": lambda x: x,
    "http://as.chacuo.net/company": lambda x: x,
    "http://as.chacuo.net/list": lambda x: x,
    "http://doc.chacuo.net/iso-3166-1": iso_3166_1.Parser().parse
}

start_url_parser = {
    "http://ipcn.chacuo.net/view/i_": domestic_operator_ip_range.OperatorParser().parse,
    "http://ipblock.chacuo.net/view/c_": country_ip_range.CountryParser().parse,
    "http://as.chacuo.net/companyview/s_": lambda x: x,
    "http://as.chacuo.net/as": lambda x: x
}

regex_url_parser = {
    r"http://as.chacuo.net/[A-Z]{2}": lambda x: x
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
