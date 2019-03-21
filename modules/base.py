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
            logging.warning(f'解析失败，原因: {e}, \n{traceback.format_exc()}')
            return {}
        if 'clickable' not in result:
            return {}
        if 'info' not in result:
            return {}

        return result
