#! /usr/bin/python
# -*- coding:utf-8 -*-


from bs4 import BeautifulSoup
from modules.base import BaseParser


class Parser(BaseParser):
    """http://as.chacuo.net/list"""

    def _parse(self, data):

        soup = BeautifulSoup(data, 'html.parser')
        results = []
        click = {}
        tbody = soup.find('tbody')
        for tr in tbody('tr'):
            res = []
            for td in tr('td'):
                res.append(td)
            if 4 != len(res):
                continue
            results.append({
                "sort": res[0].text,
                "second_code": res[1].text.strip(),
                "country": res[2].text,
                "as_count": res[3].text,
                "url": res[1].a['href']
            })
            click[res[1].text.strip()] = res[1].a['href']

        result = {
            "clickable": click,
            "info": results
        }
        return result
