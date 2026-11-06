# Dosya Yolu: tests/test_public_installer_contract.py
# Amac: Public Ragnar setup kaynak pin ve 2015/2022 yayin sinirlarini kilitlemek
# Modul - Python unittest
# Version: 1.0.1
# Aciklama: Read-only repository QA workflow contract, NO game file I/O
# Bagimli Oldugu Katman: Test | Public Artifact Delivery
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/public-ragnar-installer-qa.yml"
PIN = re.compile(r"^[0-9a-f]{40}$")


class PublicInstallerContract(unittest.TestCase):
    def test_pinned_public_reusable_workflow_is_same_source(self):
        content = WORKFLOW.read_text(encoding="utf-8")
        match = re.search(
            r"uses: LevelUpRagnarok/beam-patcher/\.github/workflows/"
            r"ragnar-turkuaz-installer-qa\.yml@([0-9a-f]{40})", content
        )
        self.assertIsNotNone(match, "PUBLIC_REUSABLE_WORKFLOW_PIN_REQUIRED")
        self.assertTrue(PIN.fullmatch(match.group(1)))
        self.assertNotIn("LevelUpGT/beam-patcher", content)
        self.assertNotIn("b1glord/ragnarokclientpatch", content)
        docs = (ROOT / "installer/qa/README.md").read_text(encoding="utf-8")
        self.assertIn(match.group(1), docs)
        self.assertIn("source_ref: " + match.group(1), content)

    def test_no_private_source_checkout_or_distribution(self):
        content = WORKFLOW.read_text(encoding="utf-8")
        self.assertNotIn("LevelUpRagnarok/RagnarokClient", content)
        self.assertNotIn("secrets.", content)
        self.assertIn("contents: read", content)
        self.assertNotIn("actions/create-release", content)
        self.assertNotIn("gh release create", content)
        self.assertNotIn("release:", content)
        self.assertIn("2022/beam/check_reserved_channel.py", content)

    def test_public_product_name_private_client_identity(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        readme = (ROOT / "installer/qa/README.md").read_text(encoding="utf-8")
        self.assertIn("Turkuaz-Ragnarok-Online-Setup.exe", readme)
        self.assertIn("client-identity.json", readme)
        self.assertIn("preview-qa", readme)
        self.assertIn("classic-2015", readme)
        self.assertIn("renewal-2022", readme)
        self.assertIn("packetver", readme)
        self.assertIn("production_publish_allowed=false", readme)
        self.assertIn("source_ref: ", workflow)

    def test_channel_docs_preserve_public_private_split(self):
        readme = (ROOT / "installer/qa/README.md").read_text(encoding="utf-8")
        self.assertIn("ready: false", readme)
        self.assertIn("publish_allowed: false", readme)
        self.assertIn("LevelUpRagnarok/ragnarokclientpatch", readme)
        self.assertIn("not a production release", readme.lower())


if __name__ == "__main__":
    unittest.main()
