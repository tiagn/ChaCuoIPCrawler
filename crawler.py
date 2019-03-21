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

        if sleep_time * 10 < 10:
            sleep_time = 10
        time.sleep(random.randint(1, sleep_time) * 0.1)  # 防止访问太频繁，强制休息 0.1 秒以上

        if headers:
            headers = dict(headers, **self.headers)

        try:
            async with aiohttp.ClientSession() as session:
                logging.info(f'获取: {url}')
                async with session.get(url, headers=headers) as resp:
                    response = await resp.text(errors='ignore')
                    if append_info:
                        append_info['response'] = response
                    return append_info
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
                sleep_time = url_info.get('sleep_time')
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
        if isinstance(data, str):
            if self._data:
                if 'clickable' in self._data:
                    if data in self._data['clickable']:
                        self._data = self._craw(self._data['clickable'][data])
            else:
                if data.startswith('http'):
                    self._data = self._craw(data)
        else:
            self._data = self._craw(data)
        return self._data

    def _craw(self, urls: Any):
        if isinstance(urls, str):
            url = urls.strip()
            parser = modules.find_parser(url)
            resp = self.downloader.download(url)
            if resp:
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
                    results[url] = dict(parser(resp['response']), **resp)
            return results

    @staticmethod
    def save(data: Any, filename: str) -> None:
        with open(filename, 'w', encoding='utf8') as fw:
            json.dump(data, fw)


def save_countrys_ip_ranges_by_country(dir_path='test/'):
    url = 'http://ipblock.chacuo.net/'
    crawler = Crawler()
    res = crawler.click(url)
    if not res:
        print('请检查网络')
        return
    clicks = []
    count = 0
    for key, value in res['clickable'].items():
        # if count > 50:
        #     count = 0
        #     break
        # count += 1
        clicks.append({
            "url": value,
            "country": key
        })
    res = crawler.click(clicks)
    if not res:
        print('请检查网络')
        return
    results = []
    for info in res.values():
        # if count > 50:
        #     count = 0
        #     break
        # count += 1
        url = info['info']['url']
        results.append({
            "url": url,
            "country": info['country']
        })
    res = crawler.click(results)
    for info in res.values():
        path = dir_path + info['country']
        try:
            with open(path, 'w') as fw:
                json.dump(info['info']['ip_range'], fw)
        except Exception:
            pass


if __name__ == '__main__':
    # a = Crawler()
    # from pprint import pprint
    #
    # pprint(a.click("http://ipblock.chacuo.net/"))
    save_countrys_ip_ranges_by_country()
