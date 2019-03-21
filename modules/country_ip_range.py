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


class CountryParser(BaseParser):

    def _parse(self, data):
        soup = BeautifulSoup(data, 'html.parser')
        div = soup.find('div', class_='section_content ip_block_list')
        res = []

        for b in div('b'):
            res.append(b.text)

        text_url = div('a')[2]['href']
        info = {
            "update_time": res[0],
            "global_count": res[1],
            "count": res[2],
            "percent": res[3],
            "global_list": res[4],
            "url": text_url
        }
        result = {
            "clickable": {
                "ip_range": text_url
            },
            "info": info
        }
        return result


class CountryIPRangeParser(BaseParser):

    def _parse(self, data):
        soup = BeautifulSoup(data, 'html.parser')
        pre = soup.find('pre')
        ip_range_raw = pre.text.split(r'\r\n')
        results = []
        for ip_range in ip_range_raw:
            if not ip_range:
                continue
            res = ip_range.split(r'\t')
            results.append('-'.join([res[0], res[1]]))

        result = {
            "clickable": {},
            "info": {
                "ip_range":results
            }
        }
        return result
