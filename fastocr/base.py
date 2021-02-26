from abc import ABCMeta, abstractmethod
from typing import List


class BaseOcr(metaclass=ABCMeta):
    @abstractmethod
    async def basic_general(self, image: bytes, lang: str = '') -> List[str]:
        pass
