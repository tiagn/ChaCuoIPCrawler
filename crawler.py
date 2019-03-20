#! /usr/bin/python
# -*- coding:utf-8 -*-

import asyncio
import aiohttp
import fake_useragent
import logging
import random
import time

from typing import Any, List, Dict, Tuple


class Downloader:

    def __init__(self):
        self.headers = {'User-Agent': fake_useragent.UserAgent().random}
        self.loop = asyncio.get_event_loop()

    async def _download(self, url: str) -> Dict:
        time.sleep(random.randint(2, 5))  # 防止访问太频繁，强制休息 2-5 秒
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as resp:
                return {"url": url, "response": await resp.text(errors='ignore')}

    def download(self, url: str) -> Tuple[Any]:
        return self.downloads([url])

    def downloads(self, urls: List[str]) -> Tuple[Any]:
        tasks = []
        for url in urls:
            tasks.append(self._download(url))
        try:
            return self.loop.run_until_complete(asyncio.gather(*tasks))
        except Exception as e:
            logging.warning(f'请检查网络状态，错误：{e}')
