#! /usr/bin/python
# -*- coding:utf-8 -*-


from bs4 import BeautifulSoup
from modules.base import BaseParser, ip_range_to_cidr


class Parser(BaseParser):
    """http://as.chacuo.net/"""

    def _parse(self, data):

        soup = BeautifulSoup(data, 'html.parser')
        country_urls = {}
        div = soup.find('div', class_="section_content ip_block_list")
        res = []
        for b in div('b'):
            res.append(b.text)
        for ul in soup('ul', class_="list clearfix inline-block"):
            for li in ul('li'):
                country_urls[li.a.text] = li.a['href']

        result = {
            "clickable": country_urls,
            "info": {
                "update_time": res[0],
                "as_count": res[1],
                "country": country_urls
            }
        }
        return result


class CountryParser(BaseParser):
    """http://as.chacuo.net/US"""

    def _parse(self, data):

        soup = BeautifulSoup(data, 'lxml')
        results = []
        click = {}
        div = soup.find('div', class_="section_content ip_block_list_ph")
        p = div.find('p')
        info_res = []
        for b in p('b'):
            info_res.append(b.text)

        table = soup.find('tbody')
        for tr in table('tr'):
            res = []
            for td in tr('td'):
                res.append(td)
            if not res:
                continue
            if 5 != len(res):
                continue
            click[res[1].text.strip()] = res[1].a['href']
            results.append({
                "sort": res[0].text,
                "as_num": res[1].text.strip(),
                "register": res[2].text,
                "count": res[3].text.strip('个'),
                "register_time": res[4].text,
                'url': res[1].a['href']
            })
        result = {
            "clickable": click,
            "info": {
                "country": info_res[0],
                "update_time": info_res[1],
                "global_count": info_res[2],
                "as_count": info_res[3],
                "percent": info_res[4],
                "global_sort": info_res[5],
                "as": results
            }
        }
        return result


class ASParser(BaseParser):
    """http://as.chacuo.net/as7922"""

    def _parse(self, data):

        soup = BeautifulSoup(data, 'html.parser')
        click = {}
        div = soup('div', class_="m_b10")[1]
        res = []
        for li in div('li'):
            span = li.find('span')
            if not span:
                continue
            res.append(span.text)

        ip_ranges = []
        for ul in soup('ul', class_="l p_l10"):
            for li in ul('li'):
                ip_ranges_res = []
                for span in li('span'):
                    ip_ranges_res.append(span.text)
                ip_ranges.extend(ip_range_to_cidr(ip_ranges_res[0], ip_ranges_res[1]))
        results = {
            "as_num": res[0],
            "country": res[1],
            "isp": res[2],
            "ip_count": res[3],
            "desc": res[4],
            "ip_ranges": ip_ranges
        }
        result = {
            "clickable": click,
            "info": results
        }
        return result
