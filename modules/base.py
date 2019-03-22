# /usr/bin/python
# coding:utf8
import logging
import traceback
from typing import Any, Dict


class BaseParser:

    def _parse(self, data) -> Any:
        raise NotImplementedError

    def parse(self, data) -> Dict:
        try:
            result = self._parse(data)
        except Exception as e:
            logging.warning(f'解析失败，请检查网站或联系作者，原因: {e}')
            return {}
        if 'clickable' not in result:
            return {}
        if 'info' not in result:
            return {}

        return result
