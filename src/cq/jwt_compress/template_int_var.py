import base64
from itertools import chain

from math import ceil
from typing import Iterable, List, Dict

from .abstract import AbstractVarCompressor


class ScopeTemplateIntegerVarCompressor(AbstractVarCompressor):
    name: str = "int_tpl"

    def __init__(self, except_vars: Iterable[str] = (), value_separator: bytes = b"\0"):
        """
        :param except_vars: Variable names that should be ignored. Shouldn't contain leading `$` symbol.
        :param value_separator: Separator symbol which is used to split values in compressed format.
          Shouldn't be used in source strings.
        """
        super().__init__(except_vars=except_vars)

        self.value_separator = value_separator

    @classmethod
    def compress_values(cls, values: List[str], bytes_count: int = 8) -> bytes:
        """
        Compresses values to single string
        :param values: Values to compress. Value must be integer or "*" symbol.
        :param bytes_count: Number of bytes to encode each integer value as
        :return: bytes
        """
        return b"".join((
            b"\0" * bytes_count if val == "*" else int.to_bytes(int(val), bytes_count, 'big', signed=False)
            for val in values
        ))

    @classmethod
    def decompress_values(cls, values_str: bytes, bytes_count: int = 8) -> List[str]:
        """
        Decompresses values string to original values list
        :param values_str: byte string to decompress
        :param bytes_count: Number of bytes each integer value is encoded with
        :return: List of string values as they were passed to compress_values
        """
        return [
            "*" if values_str[i:i + bytes_count] == b"\0" * bytes_count
            else int.from_bytes(values_str[i:i + bytes_count], 'big', signed=False)
            for i in range(0, len(values_str), bytes_count)
        ]

    def compress(self, data: Iterable[str]) -> Iterable[str]:
        template_vals = self.split_values_by_template(data)

        for tpl, tpl_values in template_vals.items():
            if tpl_values[0]:
                max_value = max(int(item) for item in chain(*tpl_values))
                max_bytes = ceil(max_value.bit_length() / 8)
                encoded_bytes = b"".join(
                    self.compress_values(val, bytes_count=max_bytes)
                    for val in tpl_values
                )
            else:
                # В шаблоне нет переменных. Так бывает.
                max_value, max_bytes = 0, 0
                encoded_bytes = b""

            bytes_item =(
                int.to_bytes(max_bytes, 1, 'big', signed=False)
                + int.to_bytes(len(tpl_values[0]), 1, 'big', signed=False)
                + tpl.encode("ascii")
                + self.value_separator
                + encoded_bytes
            )
            yield base64.b64encode(bytes_item).decode("ascii")


    def decompress(self, data: Iterable[str]) -> Iterable[str]:
        for data_item in data:
            encoded_bytes = base64.b64decode(data_item.encode("ascii"))
            bytes_count = int.from_bytes(encoded_bytes[:1], 'big', signed=False)
            vars_count = int.from_bytes(encoded_bytes[1:2], 'big', signed=False)

            chunk_size = bytes_count * vars_count
            tpl_bytes, values_bytes = encoded_bytes[2:].split(self.value_separator, 1)
            tpl = tpl_bytes.decode("ascii")

            # Ситуация, когда в шаблоне нет переменных
            if chunk_size == 0:
                yield tpl
                continue

            for start_pos in range(0, len(values_bytes), chunk_size):
                item_vals = self.decompress_values(
                    values_bytes[start_pos:start_pos + chunk_size], bytes_count=bytes_count
                )
                yield tpl.format(*item_vals)
