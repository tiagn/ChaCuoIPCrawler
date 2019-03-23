#! /usr/bin/python
# -*- coding:utf-8 -*-

import asyncio
import json

import aiohttp
import fake_useragent
import logging
import modules
import random
import time

from typing import Any, List, Dict, Tuple

logging.basicConfig(level=logging.DEBUG)


class Downloader:

    def __init__(self):
        self.headers = {'User-Agent': fake_useragent.UserAgent().random}
        self.loop = asyncio.get_event_loop()

    async def _download(self, url: str, sleep_time: int = 1, headers: Dict = None, append_info: Dict = None) -> Dict:
        sleep_time *= 10
        if sleep_time < 10:
            sleep_time = 10
        time.sleep(random.randint(1, sleep_time) * 0.1)  # 防止访问太频繁，强制休息 0.1 秒以上

        if headers:
            headers = dict(headers, **self.headers)
        for _ in range(3):
            try:
                async with aiohttp.ClientSession() as session:
                    logging.info(f'获取: {url}')
                    async with session.get(url, headers=headers) as resp:
                        response = await resp.text(errors='ignore')
                        if not append_info:
                            return {"response": response}
                        append_info['response'] = response
                        append_info['url'] = url
                        return append_info
            except TimeoutError:
                logging.warning(f'{url} 超时，重试中...')
                continue
            except Exception as e:
                logging.warning(f'请检查网络, 原因: {e}')

    def download(self, url: str) -> Tuple[Any]:
        resps = self.downloads([url])
        if resps:
            return resps[0]

    def downloads(self, url_infos: List, all_append: bool = True) -> Tuple[Any]:
        tasks = []
        for url_info in url_infos:
            if isinstance(url_info, str):
                tasks.append(self._download(url_info))
            else:
                url = url_info.get('url')
                sleep_time = url_info.get('sleep_time', 1)
                headers = url_info.get('headers')
                if all_append:
                    tasks.append(self._download(url, sleep_time=sleep_time, headers=headers, append_info=url_info))
                else:
                    if 'url' in url_info:
                        del url_info['url']
                    if 'sleep_time' in url_info:
                        del url_info['sleep_time']
                    if 'headers' in url_info:
                        del url_info['headers']
                    tasks.append(self._download(url, sleep_time=sleep_time, headers=headers, append_info=url_info))

        return self.loop.run_until_complete(asyncio.gather(*tasks))


class Crawler:

    def __init__(self):
        self.downloader = Downloader()
        self._data = None

    def get_info(self) -> Any:
        return self._data

    def click(self, data: Any) -> Any:
        pre_data = self._data
        self._data = None
        if isinstance(data, str):
            if pre_data:
                if 'clickable' in pre_data:
                    if data in pre_data['clickable']:
                        self._data = self._craw(pre_data['clickable'][data])
                    else:
                        if data.startswith('http'):
                            self._data = self._craw(data)
            else:
                if data.startswith('http'):
                    self._data = self._craw(data)
        else:
            self._data = self._craw(data)
        return self._data

    def _craw(self, urls: Any):
        """
        urls 为链接时是str， 返回字典，urls为list时，list包含的是一个字典，其中一定要有url字段，返回的是list，里面也是字典
        :param urls:
        :return:
        """
        if isinstance(urls, str):
            url = urls.strip()
            parser = modules.find_parser(url)
            resp = self.downloader.download(url)
            if resp:
                logging.info(f'解析: {url}')
                return parser(resp['response'])
        elif isinstance(urls, list):
            tmp_urls = []
            # {"url": url}
            for url_info in urls:
                tmp_urls.append(url_info)
            resps = self.downloader.downloads(tmp_urls)
            results = {}
            for resp in resps:
                if resp:
                    url = resp['url']
                    parser = modules.find_parser(url)
                    logging.info(f'解析: {url}')
                    results[url] = dict(parser(resp['response']), **resp)
            return results

    @staticmethod
    def save(data: Any, filename: str) -> None:
        with open(filename, 'w', encoding='utf8') as fw:
            json.dump(data, fw)


def save_countrys_ip_ranges_by_country(dir_path: str = 'test/', sleep_time: int = 1):
    """
    获取所有国家的IP段并保存为国家名称为单位的文件
    :param dir_path: 目录
    :param sleep_time: 每个链接休息时间，避免短时访问量大
    :return:
    """
    url = 'http://ipblock.chacuo.net/'
    crawler = Crawler()
    logging.info('获取所有国家')
    res = crawler.click(url)
    if not res:
        return
    clicks = []
    for key, value in res['clickable'].items():
        clicks.append({
            "url": value,
            "country": key,
            "sleep_time": sleep_time
        })
    logging.info('获取所有国家的IP段详情')
    res = crawler.click(clicks)
    if not res:
        return
    requests = []
    for info in res.values():
        url = info['info']['url']
        requests.append({
            "url": url,
            "country": info['country'],
            "headers": {"Referer": info['url']},
            "sleep_time": sleep_time
        })
    logging.info('获取所有国家的IP段')
    res = crawler.click(requests)
    if not res:
        return
    all_country = {}
    all_path = None
    for info in res.values():
        if not dir_path.endswith('/'):
            path = dir_path + "/" + info['country']
            all_path = dir_path + "/所有国家"
        else:
            path = dir_path + info['country']
            all_path = dir_path + "所有国家"
        with open(path, 'w', encoding='utf8') as fw:
            if 'info' in info and 'ip_range' in info['info']:
                all_country[info['country']] = info['info']['ip_range']
                json.dump(info['info']['ip_range'], fw, ensure_ascii=False)
            else:
                all_country[info['country']] = []
    if all_path:
        with open(all_path, 'w', encoding='utf8') as fw:
            json.dump(all_country, fw, ensure_ascii=False)


def save_domestic_operator_ip_ranges_by_operator(dir_path: str = 'test/', sleep_time: int = 1):
    """
    获取国内运营商的IP段并保存为运营商名称为单位的文件
    :param dir_path: 目录
    :param sleep_time: 每个链接休息时间，避免短时访问量大
    :return:
    """
    url = 'http://ipcn.chacuo.net/'
    crawler = Crawler()
    logging.info('获取所有运营商')
    res = crawler.click(url)
    if not res:
        return
    clicks = []
    for key, value in res['clickable'].items():
        clicks.append({
            "url": value,
            "operator": key,
            "sleep_time": sleep_time,
            "headers": {"Referer": url},
        })
    logging.info('获取所有运营商的IP段')
    res = crawler.click(clicks)
    if not res:
        return
    all_operator = {}
    all_path = None
    for info in res.values():
        if not dir_path.endswith('/'):
            path = dir_path + "/" + info['operator']
            all_path = dir_path + "/所有运营商"
        else:
            path = dir_path + info['operator']
            all_path = dir_path + "所有运营商"
        with open(path, 'w', encoding='utf8') as fw:
            if 'info' not in info:
                all_operator[info['operator']] = {}
                continue
            all_operator[info['operator']] = info['info']
            json.dump(info['info'], fw, ensure_ascii=False)
    if all_path:
        with open(all_path, 'w', encoding='utf8') as fw:
            json.dump(all_operator, fw, ensure_ascii=False)


def save_domestic_provinces_ip_range_by_provinces(dir_path: str = 'test/', sleep_time: int = 1):
    """
    获取国内省份IP段并保存为省份为单位的文件
    :param dir_path: 目录
    :param sleep_time: 每个链接休息时间，避免短时访问量大
    :return:
    """
    url = 'http://ips.chacuo.net/'
    crawler = Crawler()
    logging.info('获取国内省份IP段详情')
    res = crawler.click(url)
    if not res:
        return
    clicks = []
    for key, value in res['clickable'].items():
        clicks.append({
            "url": value,
            "province": key,
            "sleep_time": sleep_time,
            "headers": {"Referer": url},
        })
    logging.info('获取国内省份IP段')
    res = crawler.click(clicks)
    if not res:
        return
    all_provinces = {}
    all_path = None
    for info in res.values():
        if not dir_path.endswith('/'):
            path = dir_path + "/" + info['province']
            all_path = dir_path + "/所有省份"
        else:
            path = dir_path + info['province']
            all_path = dir_path + "所有省份"
        with open(path, 'w', encoding='utf8') as fw:
            if 'info' not in info or 'ip_range' not in info['info']:
                all_provinces[info['province']] = []
                continue
            all_provinces[info['province']] = info['info']['ip_range']
            json.dump(info['info']['ip_range'], fw, ensure_ascii=False)
    if all_path:
        with open(all_path, 'w', encoding='utf8') as fw:
            json.dump(all_provinces, fw, ensure_ascii=False)


def save_companys_ip_range_by_companys(dir_path: str = 'test/', sleep_time: int = 1):
    """
    获取全球网络公司IP段并保存为网络公司为单位的文件
    :param dir_path: 目录
    :param sleep_time: 每个链接休息时间，避免短时访问量大
    :return:
    """
    url = 'http://as.chacuo.net/company'
    crawler = Crawler()
    logging.info('获取全球网络公司IP段详情')
    res = crawler.click(url)
    if not res:
        return
    clicks = []
    for key, value in res['clickable'].items():
        clicks.append({
            "url": value,
            "company": key,
            "sleep_time": sleep_time,
            "headers": {"Referer": url},
        })
    logging.info('获取全球网络公司IP段')
    res = crawler.click(clicks)
    if not res:
        return
    all_provinces = {}
    all_path = None
    for info in res.values():
        if not dir_path.endswith('/'):
            path = dir_path + "/" + info['company']
            all_path = dir_path + "/所有网络公司"
        else:
            path = dir_path + info['company']
            all_path = dir_path + "所有网络公司"
        with open(path, 'w', encoding='utf8') as fw:
            if 'info' not in info or 'ip_range' not in info['info']:
                all_provinces[info['company']] = []
                continue
            all_provinces[info['company']] = info['info']['ip_range']
            json.dump(info['info']['ip_range'], fw, ensure_ascii=False)
    if all_path:
        with open(all_path, 'w', encoding='utf8') as fw:
            json.dump(all_provinces, fw, ensure_ascii=False)


def save_companys_as_by_companys(dir_path: str = 'test/', sleep_time: int = 1):
    """
    获取全球网络公司 as 并保存为网络公司为单位的文件
    :param dir_path: 目录
    :param sleep_time: 每个链接休息时间，避免短时访问量大
    :return:
    """
    url = 'http://as.chacuo.net/company'
    crawler = Crawler()
    logging.info('获取全球网络公司as详情')
    res = crawler.click(url)
    if not res:
        return
    clicks = []
    for key, value in res['clickable'].items():
        clicks.append({
            "url": value,
            "company": key,
            "sleep_time": sleep_time,
            "headers": {"Referer": url},
        })
    logging.info('获取全球网络公司as')
    res = crawler.click(clicks)
    if not res:
        return
    all_as = {}
    all_path = None
    for info in res.values():
        if not dir_path.endswith('/'):
            path = dir_path + "/" + info['company']
            all_path = dir_path + "/所有网络公司"
        else:
            path = dir_path + info['company']
            all_path = dir_path + "所有网络公司"
        with open(path, 'w', encoding='utf8') as fw:
            if 'info' not in info or 'as_info' not in info['info']:
                all_as[info['company']] = []
                continue
            all_as[info['company']] = info['info']['as_info']
            json.dump(info['info']['as_info'], fw, ensure_ascii=False)
    if all_path:
        with open(all_path, 'w', encoding='utf8') as fw:
            json.dump(all_as, fw, ensure_ascii=False)


def save_countrys_as_by_country(dir_path: str = 'test/', sleep_time: int = 1):
    """
    获取所有国家的as并保存为国家名称为单位的文件
    :param dir_path: 目录
    :param sleep_time: 每个链接休息时间，避免短时访问量大
    :return:
    """
    url = 'http://as.chacuo.net/'
    crawler = Crawler()
    logging.info('获取所有国家的as详情')
    res = crawler.click(url)
    if not res:
        return
    clicks = []
    for key, value in res['clickable'].items():
        clicks.append({
            "url": value,
            "country": key,
            "sleep_time": sleep_time
        })
    logging.info('获取所有国家的as')
    res = crawler.click(clicks)
    if not res:
        return
    all_as = {}
    all_path = None
    for info in res.values():
        if not dir_path.endswith('/'):
            path = dir_path + "/" + info['country']
            all_path = dir_path + "/所有国家"
        else:
            path = dir_path + info['country']
            all_path = dir_path + "所有国家"
        with open(path, 'w', encoding='utf8') as fw:
            if 'info' not in info or 'as' not in info['info']:
                all_as[info['country']] = []
                continue
            all_as[info['country']] = info['info']['as']
            json.dump(info['info']['as'], fw, ensure_ascii=False)
    if all_path:
        with open(all_path, 'w', encoding='utf8') as fw:
            json.dump(all_as, fw, ensure_ascii=False)


def save_as_ip_range_by_as(dir_path: str = 'test/', sleep_time: int = 1, countrys: list = None):
    """
    根据国家获取国家as的IP段并保存为as名称为单位的文件
    :param dir_path: 目录
    :param sleep_time: 每个链接休息时间，避免短时访问量大
    :param countrys: 由于as 数量过大，很难一次性下载，因此提供按国家as下载,默认下载中国as
    :return:
    """
    if not countrys:
        countrys = ["中国"]

    url = 'http://as.chacuo.net/'
    crawler = Crawler()
    logging.info('获取所有国家')
    res = crawler.click(url)
    if not res:
        return
    clicks = []
    for key, value in res['clickable'].items():
        if key not in countrys:
            continue
        clicks.append({
            "url": value,
            "as": key,
            "sleep_time": sleep_time
        })
    logging.info('获取所有国家的as详情')
    res = crawler.click(clicks)
    if not res:
        return
    clicks = []
    for info in res.values():
        as_info_list = info['info']["as"]
        for as_info in as_info_list:
            clicks.append({
                "url": as_info['url'],
                "as": as_info['as_num'],
                "sleep_time": sleep_time,
                "headers": {"Referer": info['url']},
            })
    res = crawler.click(clicks)
    if not res:
        return
    all_as = {}
    all_path = None
    for info in res.values():
        if not dir_path.endswith('/'):
            path = dir_path + "/" + info['as']
            all_path = dir_path + "/所有as"
        else:
            path = dir_path + info['as']
            all_path = dir_path + "所有as"
        with open(path, 'w', encoding='utf8') as fw:
            if 'info' not in info or 'ip_ranges' not in info['info']:
                all_as[info['as']] = []
                continue
            all_as[info['as']] = info['info']['ip_ranges']
            json.dump(info['info']['ip_ranges'], fw, ensure_ascii=False)
    if all_path:
        with open(all_path, 'w', encoding='utf8') as fw:
            json.dump(all_as, fw, ensure_ascii=False)


if __name__ == '__main__':
    # # 获取所有国家的IP段并保存为国家名称为单位的文件
    # save_countrys_ip_ranges_by_country(dir_path='data/countrys_ip_range/')

    # # 获取国内运营商的IP段并保存为运营商名称为单位的文件
    # save_domestic_operator_ip_ranges_by_operator(dir_path='data/operator_ip_range/')

    # # 获取国内省份IP段并保存为省份为单位的文件
    # save_domestic_provinces_ip_range_by_provinces(dir_path='data/provinces_ip_range/')

    # # 获取全球网络公司IP段并保存为网络公司为单位的文件
    # save_companys_ip_range_by_companys(dir_path='data/companys_ip_range/')

    # # 获取全球网络公司 as 并保存为网络公司为单位的文件
    # save_companys_as_by_companys(dir_path='data/companys_as/')

    # # 获取所有国家的as并保存为国家名称为单位的文件
    # save_countrys_as_by_country(dir_path='data/countrys_as/')

    # 根据国家获取国家as的IP段并保存为as名称为单位的文件, 如果下载美国这种大量as数据请检查系统是否支持
    save_as_ip_range_by_as(dir_path='data/as_ip_range/', countrys=["卢森堡"])
