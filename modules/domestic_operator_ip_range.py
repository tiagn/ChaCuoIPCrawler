#! /usr/bin/python
# -*- coding:utf-8 -*-

from bs4 import BeautifulSoup, NavigableString

from modules.base import BaseParser, ip_range_to_cidr


class Parser(BaseParser):

    def _parse(self, data):

        soup = BeautifulSoup(data, 'html.parser')
        results = []
        clicks = {}
        for ul in soup('ul', class_='list'):
            res = []
            for li in ul('li'):
                res.append(li)
            clicks[res[1].text] = res[1].a['href']
            results.append({
                "sort": res[0].text,
                "name": res[1].text,
                "count": res[2].text,
                "url": res[1].a['href']
            })
        result = {
            "clickable": clicks,
            "info": results
        }
        return result


class OperatorParser(BaseParser):

    def _parse(self, data):
        soup = BeautifulSoup(data, 'html.parser')
        results = {}
        dl = soup.find('dl', class_='list')
        next_tag = dl.find('dt')
        res = []
        title = None
        while next_tag:
            if isinstance(next_tag, NavigableString):
                next_tag = next_tag.next_sibling
                continue
            if next_tag.name == 'dt':
                if title and res:
                    results[title] = res
                    res = []
                title = next_tag.text
            if next_tag.name == 'dd':
                ip_range = []
                for span in next_tag("span"):
                    ip_range.append(span.text)
                res.extend(ip_range_to_cidr(ip_range[0], ip_range[1]))
            next_tag = next_tag.next_sibling
        result = {
            "clickable": {},
            "info": results
        }
        return result
