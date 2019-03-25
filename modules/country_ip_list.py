#! /usr/bin/python
# -*- coding:utf-8 -*-
from bs4 import BeautifulSoup

from modules.base import BaseParser


class Parser(BaseParser):
    """http://ipblock.chacuo.net/list"""

    def _parse(self, data):

        soup = BeautifulSoup(data, 'html.parser')
        results = []
        table = soup.find('table')
        clicks = {}
        for tr in table('tr'):
            res = []
            for td in tr('td'):
                res.append(td)
            if len(res) != 5:
                continue
            if not res[2].text:
                continue
            results.append({
                "sort": res[0].text,
                "second_code": res[1].text,
                "country": res[2].text,
                "ip_count": res[3].text,
                "ip_range": res[4].a['href'],

            })
            clicks[res[2].text] = res[4].a['href']
        result = {
            "clickable": clicks,
            "info": results
        }
        return result
