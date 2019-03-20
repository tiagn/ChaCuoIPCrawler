#! /usr/bin/python
# -*- coding:utf-8 -*-
from bs4 import BeautifulSoup

from modules.base import BaseParser


class Parser(BaseParser):

    def _parse(self, data):

        soup = BeautifulSoup(data, 'html.parser')
        country_urls = {}
        for ul in soup('ul', class_="list clearfix inline-block"):
            for li in ul('li'):
                country_urls[li.a.text] = li.a['href']

        result = {
            "clickable": country_urls,
            "info": list(country_urls.keys())
        }
        return result
