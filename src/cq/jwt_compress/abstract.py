import re
from collections import defaultdict
from typing import Iterable, Dict, List, Set


class JWTScopesCompressor:
    """
    Base abstract class for compressing JWT roles and scopes
    """
    def name(self) -> str:
        """
        Name for short string identification
        :return: String name
        """
        raise NotImplementedError()

    def compress(self, data: Iterable[str]) -> Iterable[str]:
        """
        Compress an iterable of strings to another iterable of strings
        :param data: Data to compress
        :return: Compressed data
        """
        raise NotImplementedError()

    def decompress(self, data: Iterable[str]) -> Iterable[str]:
        """
        Decompress an iterable of strings to another iterable of strings
        :param data: Data to decompress
        :return: Source (decompressed) data
        """
        raise NotImplementedError()



class AbstractVarCompressor(JWTScopesCompressor):
    # Regular expression to search variables in items
    SCOPE_VAR_REGEX = re.compile(r"\$(?P<name>[^.]+\b):(?P<value>[^*]*?)(?=\.|$)")

    def __init__(self, except_vars: Iterable[str] = ()):
        """
        :param except_vars: Variable names that should be ignored. Shouldn't contain leading `$` symbol.
        """
        self.except_vars: Set[str] = set(except_vars)

        # Attribute contains replace_template_var(...) method results
        self._current_item_values: List[str] = []

    def replace_template_var(self, match: re.Match) -> str:
        """
        re.sub function to find all variable usages, store their values to self._current_item_values
          and return string template to use in `template.format(*self._current_item_values)`
        :param match: re.Match object based on SCOPE_VAR_REGEX
        :return: A part of template to replace match with
        """
        var_name, value = match.group(1, 2)

        if var_name in self.except_vars:
            return match.group(0)

        self._current_item_values.append(value)
        return f"${var_name}:{{}}"

    def split_values_by_template(self, data: Iterable[str]) -> Dict[str, List[List[str]]]:
        """
        Splits incoming data to a dictionary {template: [values1, values2, ...]}.
        template is a string base to use as `template.format(*values)`
        valuesN is a list of variable values for template in key
        :param data: Original data to encode
        :return: A dictionary {template: [values1, values2, ...]}.
        """
        template_indices = defaultdict(list)
        for item in data:
            # Массив заполняется в self.replace_template_var
            self._current_item_values = []
            tpl = re.sub(self.SCOPE_VAR_REGEX, self.replace_template_var, item)
            template_indices[tpl].append(self._current_item_values)

        return template_indices