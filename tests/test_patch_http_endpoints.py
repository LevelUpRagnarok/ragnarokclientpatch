#!/usr/bin/env python3
# Dosya Yolu: REPO_ROOT/tests/test_patch_http_endpoints.py
# Amac: Gercek HTTP smoke araci icin izole hata ve SHA regresyonlari
# Modul - Python unittest
# Version: 1.1.0
# Aciklama: Yalnizca TEMP fixture ve taklit HTTP; network yok
# Bagimli Oldugu Katman: Testing
import importlib.util
import io
import tempfile
import unittest
import urllib.error
from pathlib import Path

SOURCE = Path(__file__).resolve().parent / "check_patch_http_endpoints.py"
SPEC = importlib.util.spec_from_file_location("patch_http_check", SOURCE)
TOOL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(TOOL)


class FakeResponse(io.BytesIO):
    def __init__(self, url, content, status=200):
        super().__init__(content)
        self.url = url
        self.status = status

    def geturl(self):
        return self.url


class PatchHTTPTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.expected = {}
        for relative in TOOL.PATHS:
            file = self.root / relative
            file.parent.mkdir(parents=True, exist_ok=True)
            data = ("TEST/" + relative).encode("ascii")
            file.write_bytes(data)
            self.expected[relative] = data

    def opener(self, req, timeout):
        self.assertEqual(timeout, 20)
        relative = req.full_url.split("/main/", 1)[1]
        return FakeResponse(req.full_url, self.expected[relative])

    def test_both_owners_match_is_success(self):
        result = TOOL.audit(self.root, opener=self.opener)
        self.assertTrue(result["canonical_ok"])
        self.assertTrue(result["legacy_all_verified"])
        self.assertEqual(len(result["checks"]), 6)

    def test_legacy_http_404_is_not_masked_as_compatible(self):
        def opener(req, timeout):
            if "/b1glord/" in req.full_url:
                raise urllib.error.HTTPError(req.full_url, 404, "Not Found", {}, None)
            return self.opener(req, timeout)
        result = TOOL.audit(self.root, opener=opener)
        self.assertTrue(result["canonical_ok"])
        self.assertFalse(result["legacy_all_verified"])
        self.assertEqual(len(result["legacy_warnings"]), 6)
        self.assertTrue(all(row["retired"]["status"] == 404 for row in result["checks"]))

    def test_canonical_sha_mismatch_blocks_success(self):
        def opener(req, timeout):
            if "/LevelUpRagnarok/" in req.full_url:
                return FakeResponse(req.full_url, b"WRONG")
            return self.opener(req, timeout)
        result = TOOL.audit(self.root, opener=opener)
        self.assertFalse(result["canonical_ok"])
        self.assertEqual(len(result["canonical_failures"]), 6)

    def test_response_larger_than_cap_is_rejected(self):
        result = TOOL.http_get(TOOL.NEW_BASE, "plist.txt", opener=lambda req, timeout:
                               FakeResponse(req.full_url, b"x" * (TOOL.MAX_RESPONSE + 1)))
        self.assertEqual(result["error"], "RESPONSE_TOO_LARGE")

    def test_no_source_file_must_be_rejected_before_http(self):
        (self.root / "plist.txt").unlink()
        result = TOOL.audit(self.root, opener=self.opener)
        self.assertFalse(result["canonical_ok"])
        self.assertTrue(any("LOCAL_SOURCE_MISSING" in e for e in result["canonical_failures"]))


if __name__ == "__main__":
    unittest.main()
