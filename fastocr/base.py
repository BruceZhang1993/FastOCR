from abc import ABCMeta, abstractmethod
from typing import List

from aiohttp import ClientSession, TraceConfig, TraceRequestStartParams, TraceRequestEndParams

from fastocr.log import AppLogger


class BaseOcr(metaclass=ABCMeta):
    def __init__(self):
        trace_config = TraceConfig()
        trace_config.on_request_start.append(self.on_request_start)
        trace_config.on_request_end.append(self.on_request_end)
        self.session = ClientSession(trace_configs=[trace_config])
        self.logger = AppLogger()

    async def on_request_start(self, _, __, params: TraceRequestStartParams):
        self.logger.debug(f'Requesting: [{params.method.upper().ljust(6, " ")}] {params.url}]')

    async def on_request_end(self, _, __, params: TraceRequestEndParams):
        self.logger.debug(f'Requested: [{params.method.upper().ljust(6, " ")}] {params.url} Response: {await params.response.read()}')

    @abstractmethod
    async def basic_general(self, image: bytes, lang: str = '') -> List[str]:
        pass
