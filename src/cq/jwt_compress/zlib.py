import sys
import zlib

from typing import Iterable

from .abstract import JWTScopesCompressor


class ZLibScopesCompressor(JWTScopesCompressor):
    """
    Compress roles and scopes using zlib
    """
    name: str = "zlib"

    def __init__(self, separator: str = "\0", level: int = 9, wbits: int = zlib.MAX_WBITS):
        """
        :param separator: Separator symbol which should not be present in any compressed item.
        :param level: ZLib compression level
        :param wbits: ZLib wbits. Available in python 3.11 only. In earlier versions would be ignored.
        """
        self.separator = separator
        self.level = level
        self.wbits = wbits

    def compress(self, data: Iterable[str]) -> Iterable[str]:
        data = sorted(data)
        kwargs = {"wbits": self.wbits} if sys.version_info >= (3, 11) else {}
        res = zlib.compress(self.separator.join(data).encode(), level=self.level, **kwargs)
        return [self.bytes_to_json_str(res)]

    def decompress(self, data: Iterable[str]) -> Iterable[str]:
        data = list(data)
        data_bytes = self.json_str_to_bytes(data[0])
        decompressed = zlib.decompress(data_bytes, wbits=self.wbits)
        for item in decompressed.decode().split(self.separator):
            yield item
