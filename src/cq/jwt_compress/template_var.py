from typing import Iterable, List

from .abstract import AbstractVarCompressor


class ScopeTemplateVarCompressor(AbstractVarCompressor):
    """
    Compress roles and scopes by finding repeating templates and its string values and removing unnecessary text
    """
    name: str = "tpl"

    def __init__(self, except_vars: Iterable[str] = (), value_separator: str = "\0", item_separator: str = "\t"):
        """
        :param except_vars: Variable names that should be ignored. Shouldn't contain leading `$` symbol.
        :param value_separator: Separator symbol which is used to split values in compressed format.
          Shouldn't be used in source strings.
        :param item_separator: Separator symbol which is used to split templates in compressed format.
          Shouldn't be used in source strings.
        """
        super().__init__(except_vars=except_vars)

        self.value_separator = value_separator
        self.item_separator = item_separator

    def compress_values(self,  values: List[str]) -> str:
        """
        Compresses values to single string
        :param values: Value to compress
        :return: String
        """
        return self.value_separator.join(values)

    def decompress_values(self, values_str: str) -> List[str]:
        """
        Decompresses values string to original values list
        :param values_str: Compressed value string
        :return: List of string values as they were passed to compress_values
        """
        return values_str.split(self.value_separator)

    def compress(self, data: Iterable[str]) -> Iterable[str]:
        template_vals = self.split_values_by_template(data)

        for tpl, tpl_values in template_vals.items():
            yield self.item_separator.join([tpl, *(self.compress_values(vals) for vals in tpl_values)])

    def decompress(self, data: Iterable[str]) -> Iterable[str]:
        for item in data:
            item_parts = item.split(self.item_separator)
            for values_item in item_parts[1:]:
                yield item_parts[0].format(
                    *self.decompress_values(values_item)
                )
