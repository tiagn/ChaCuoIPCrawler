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

    async def _download(self, url: str, **kwargs) -> Dict:
        time.sleep(random.randint(1, 50) * 0.1)  # 防止访问太频繁，强制休息 0.1-0.5 秒
        async with aiohttp.ClientSession() as session:
            logging.info(f'获取: {url}')
            if url.startswith('http://ipblock.chacuo.net/down'):
                self.headers['Referer'] = 'http://ipblock.chacuo.net/view/'+ url.split('=')[1]
            async with session.get(url, headers=self.headers) as resp:
                return dict({"url": url, "response": await resp.text(errors='ignore')}, **kwargs)

    def download(self, url: str) -> Tuple[Any]:
        resps = self.downloads([{"url": url}])
        if resps:
            return resps[0]

    def downloads(self, url_infos: List) -> Tuple[Any]:
        tasks = []
        for url_info in url_infos:
            url = url_info["url"]
            del url_info["url"]
            tasks.append(self._download(url, **url_info))
        try:
            return self.loop.run_until_complete(asyncio.gather(*tasks))
        except Exception as e:
            logging.warning(f'请检查网络状态，错误：{e}')


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
