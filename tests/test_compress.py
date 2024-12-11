
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

    def test_get_instance_by_name(self):
        compressor = JWTScopesCompressor.get_instance_by_name(self.compressor.name)
        self.assertIsInstance(compressor, self.compressor.__class__)


class TestZlibCompress(AbstractTestCompressMixin, TestCase):
    compressor = ZLibScopesCompressor()

    def test_get_instance_by_name_kwargs(self):
        compressor = JWTScopesCompressor.get_instance_by_name(self.compressor.name, kwargs={"level": 6})

        self.assertIsInstance(compressor, self.compressor.__class__)
        self.assertEqual(6, compressor.level)


class TestTemplateCompress(AbstractTestCompressMixin, TestCase):
    compressor = ScopeTemplateVarCompressor(except_vars={"django_user", "scope_flags"})

    def test_get_class_by_name(self):
        compressor_cls = JWTScopesCompressor.get_class_by_name(self.compressor.name)

        self.assertEqual(self.compressor.__class__, compressor_cls)

    def test_get_instance_by_name_kwargs(self):
        compressor = JWTScopesCompressor.get_instance_by_name(self.compressor.name, kwargs={"except_vars": ("test",)})

        self.assertIsInstance(compressor, self.compressor.__class__)
        self.assertSetEqual({"test"}, compressor.except_vars)


class TestIntegerTemplateCompress(AbstractTestCompressMixin, TestCase):
    compressor = ScopeTemplateIntegerVarCompressor(except_vars={"django_user", "scope_flags"})

    def test_get_instance_by_name_kwargs(self):
        compressor = JWTScopesCompressor.get_instance_by_name(self.compressor.name, kwargs={"except_vars": ("test",)})

        self.assertIsInstance(compressor, self.compressor.__class__)
        self.assertSetEqual({"test"}, compressor.except_vars)
