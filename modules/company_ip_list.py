#! /usr/bin/python
# -*- coding:utf-8 -*-

from bs4 import BeautifulSoup

from modules.base import BaseParser, ip_range_to_cidr


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
        ip_ranges = []
        div = soup('div', class_="clearfix")[3]
        for ul in div('ul'):
            for li in ul('li'):
                res = []
                for span in li('span'):
                    res.append(span.text)
                ip_ranges.extend(ip_range_to_cidr(res[0], res[1]))
        result = {
            "clickable": click,
            "info": {
                "as_info": results,
                "ip_range": ip_ranges
            }
        }
        return result
