#! /usr/bin/python
# -*- coding:utf-8 -*-

from bs4 import BeautifulSoup

from modules.base import BaseParser


class Parser(BaseParser):
    """http://as.chacuo.net/company"""
    def _parse(self, data):

        soup = BeautifulSoup(data, 'html.parser')
        results = {}
        for ul in soup('ul', class_='list'):
            for a in ul('a'):
                strong = a.find('strong')
                results[strong.text] = a['href']
        result = {
            "clickable": results,
            "info": results
        }
        return result


class CompanyParser(BaseParser):
    """http://as.chacuo.net/companyview/s_google"""
    def _parse(self, data):

        soup = BeautifulSoup(data, 'html.parser')
        results = []
        click = {}
        tbody = soup.find('tbody')

        for tr in tbody('tr'):
            res = []
            for td in tr('td'):
                res.append(td)
            results.append({
                "sort": res[0].text,
                "as_num": res[1].text.strip(),
                "register": res[2].text,
                "ip_count": res[3].text,
                "register_time": res[4].text,
            })
            click[res[1].text.strip()] = res[1].a['href']
        result = {
            "clickable": click,
            "info": results
        }
        return result
