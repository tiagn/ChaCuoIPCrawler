#! /usr/bin/python
# -*- coding:utf-8 -*-

from bs4 import BeautifulSoup

from modules.base import BaseParser, ip_range_to_cidr


class Parser(BaseParser):

    def _parse(self, data):

        soup = BeautifulSoup(data, 'html.parser')
        results = []
        clicks = {}
        for p in soup('p'):
            res = []
            for li in p('li'):
                res.append(li)
            if not res:
                continue
            url = res[1].a['href']
            results.append({
                "sort": res[0].text,
                "name": res[1].text,
                "count": res[2].text,
                "url": url}
            )
            clicks[res[1].text] = url
        result = {
            "clickable": clicks,
            "info": results
        }
        return result


class ProvinceParser(BaseParser):

    def _parse(self, data):

        soup = BeautifulSoup(data, 'html.parser')
        results = []
        clicks = {}
        res = []
        for b in soup('b', class_="blue"):
            res.append(b.text)
        ip_range_res = []
        for dl in soup('dl', class_='list'):
            for dd in dl('dd'):
                tmp_res = []
                for span in dd('span'):
                    tmp_res.append(span.text)
                ip_range_res.extend(ip_range_to_cidr(tmp_res[0], tmp_res[1]))

        info = {
            "update_time": res[0],
            "count": res[1],
            "ip_range": ip_range_res
        }
        result = {
            "clickable": clicks,
            "info": info
        }
        return result
