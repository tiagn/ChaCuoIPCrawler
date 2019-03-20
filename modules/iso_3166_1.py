#! /usr/bin/python
# -*- coding:utf-8 -*-
from modules.base import BaseParser
from bs4 import BeautifulSoup


class Parser(BaseParser):

    def _parse(self, data):

        soup = BeautifulSoup(data, 'html.parser')
        table = soup.find('table', class_="f14")
        results = []
        for tr in table('tr'):
            res = []
            for td in tr('td'):
                res.append(td.text)
            if not res:
                continue
            results.append(
                {
                    "second": res[0],
                    "three": res[1],
                    "number": res[2],
                    "code": res[3],
                    "country": res[4],
                    "china_name": res[5],
                    "taiwan_name": res[6],
                    "hongkong_name": res[7],
                    "desc": res[8] if 9 == len(res) else '',
                }
            )
        result = {
            "clickable": {},
            "info": results
        }
        return result
