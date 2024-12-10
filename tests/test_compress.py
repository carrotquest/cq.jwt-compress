
from typing import Sequence

from unittest import TestCase

from cq.jwt_compress.abstract import JWTScopesCompressor
from cq.jwt_compress.template_int_var import ScopeTemplateIntegerVarCompressor
from cq.jwt_compress.template_var import ScopeTemplateVarCompressor
from cq.jwt_compress.zlib import ZLibScopesCompressor


class AbstractTestCompressMixin:
    compressor: JWTScopesCompressor = None

    def _assert_compress_decompress(self, data: Sequence[str]):
        compressed = self.compressor.compress(data)
        decompressed = self.compressor.decompress(compressed)

        self.assertSetEqual(set(data), set(decompressed))

    def test_single(self):
        self._assert_compress_decompress(("tools.all",))

    def test_multiple(self):
        self._assert_compress_decompress(("tools.all", "tools.read"))

    def test_many_roles_with_vars(self):
        self._assert_compress_decompress((
            "superadmin.$app:100.$django_user:1",
            "superadmin.$app:101.$django_user:1",
            "admin.$app:102.$django_user:1.$scope_flags:1",
            "admin.$app:103.$django_user:1.$scope_flags:0",
        ))

    def test_asterisk(self):
        self._assert_compress_decompress((
            "user.read.$app:100.user_id:*",
        ))


class TestZlibCompress(AbstractTestCompressMixin, TestCase):
    compressor = ZLibScopesCompressor()


class TestTemplateCompress(AbstractTestCompressMixin, TestCase):
    compressor = ScopeTemplateVarCompressor(except_vars={"django_user", "scope_flags"})


class TestIntegerTemplateCompress(AbstractTestCompressMixin, TestCase):
    compressor = ScopeTemplateIntegerVarCompressor(except_vars={"django_user", "scope_flags"})
