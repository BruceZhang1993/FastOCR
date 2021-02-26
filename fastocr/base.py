from abc import ABCMeta, abstractmethod


class BaseOcr(metaclass=ABCMeta):
    @abstractmethod
    async def basic_general(self, image: bytes, lang: str = ''):
        pass
