# /usr/bin/python
# coding:utf8
from typing import Any, Dict


class BaseParser:

    def _parse(self, data) -> Any:
        raise NotImplementedError

    def parse(self, data) -> Dict:
        result = self._parse(data)
        if 'clickable' not in result:
            return {}
        if 'info' not in result:
            return {}
        return result
