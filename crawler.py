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


class Downloader:

    def __init__(self):
        self.headers = {'User-Agent': fake_useragent.UserAgent().random}
        self.loop = asyncio.get_event_loop()

    async def _download(self, url: str) -> Dict:
        time.sleep(random.randint(1, 5) * 0.1)  # 防止访问太频繁，强制休息 0.1-0.5 秒
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as resp:
                return {"url": url, "response": await resp.text(errors='ignore')}

    def download(self, url: str) -> Tuple[Any]:
        resps = self.downloads([url])
        if resps:
            return resps[0]

    def downloads(self, urls: List[str]) -> Tuple[Any]:
        tasks = []
        for url in urls:
            tasks.append(self._download(url))
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

    def click(self, data: str) -> Any:
        if self._data:
            if 'clickable' in self._data:
                if data in self._data['clickable']:
                    self._data = self._craw(self._data['clickable'][data])
        else:
            if data.startswith('http'):
                self._data = self._craw(data)

    def _craw(self, urls: Any):
        if isinstance(urls, str):
            url = urls.strip()
            parser = modules.find_parser(url)
            resp = self.downloader.download(url)
            if resp:
                return parser(resp['response'])
        elif isinstance(urls, list):
            tmp_urls = []
            for url in urls:
                tmp_urls.append(url.strip())
            resps = self.downloader.downloads(tmp_urls)
            results = []
            for resp in resps:
                if resp:
                    url = resp['url']
                    parser = modules.find_parser(url)
                    results.append(parser(resp['response']))

    @staticmethod
    def save(data: Any, filename: str) -> None:
        with open(filename, 'wb') as fw:
            json.dump(data, fw)
