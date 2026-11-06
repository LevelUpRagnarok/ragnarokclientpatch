#!/usr/bin/env python3
# Dosya Yolu: REPO_ROOT/2022/beam/tests/test_reserved_workflow_policy.py
# Amac: 2022 BEAM yayin kilidi kontrolunu tum PR'larda calistirmak
# Modul - Python unittest
# Version: 1.0.0
# Aciklama: Salt-okunur workflow izinlerini ve required-check tetigini korur
# Bagimli Oldugu Katman: Testing

"""Fail-closed regression tests for the public 2022 BEAM workflow gate."""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
WORKFLOW = ROOT / ".github" / "workflows" / "2022-beam-reserved.yml"


# @dev-id RAG-BEAM-CI-021
# @purpose Keep the reserved 2022 channel guard available on every PR.
# @reason A path-filtered check cannot reliably be required by main protection.
# @contract Read-only CI; no release, upload, or gameplay changes.
def validate_guard_workflow(source: str) -> None:
    if "\non:\n" not in source or "\npermissions:\n" not in source:
        raise ValueError("GUARD_WORKFLOW_MISSING_EVENT_OR_PERMISSIONS")
    events = source.split("\non:\n", 1)[1].split("\npermissions:\n", 1)[0]
    if "  pull_request: {}\n" not in events:
        raise ValueError("GUARD_NOT_TRIGGERED_ON_EVERY_PR")
    if "  push:\n    branches: [main]\n" not in events:
        raise ValueError("MAIN_PUSH_GUARD_MISSING")

    permissions = source.split("\npermissions:\n", 1)[1].split("\njobs:\n", 1)[0]
    if permissions.strip() != "contents: read":
        raise ValueError("GUARD_WORKFLOW_PERMISSIONS_TOO_BROAD")

    jobs = source.split("\njobs:\n", 1)[1]
    if ("  reserved-feed:\n" not in jobs or
            "    runs-on: ubuntu-latest\n" not in jobs or
            "          persist-credentials: false\n" not in jobs):
        raise ValueError("GUARD_HOSTED_READONLY_JOB_MISSING")
    for required in (
        "python3 -B 2022/beam/check_reserved_channel.py --root .",
        "-p 'test_reserved_channel.py' -v",
        "-p 'test_reserved_workflow_policy.py' -v",
    ):
        if required not in jobs:
            raise ValueError("GUARD_REQUIRED_TEST_MISSING")

    for forbidden in ("actions/upload-artifact", "gh release", "git push", "issues: write",
                      "contents: write", "secrets.", "RAGNAROKSERVER_DISPATCH_TOKEN"):
        if forbidden in jobs:
            raise ValueError("GUARD_UNSAFE_WRITE_OR_SECRET_REFERENCE")


class ReservedWorkflowPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = WORKFLOW.read_text(encoding="utf-8")

    def test_current_guard_is_always_on_and_read_only(self):
        validate_guard_workflow(self.source)

    def test_reintroducing_pr_path_filter_is_rejected(self):
        changed = self.source.replace(
            "  pull_request: {}\n",
            '  pull_request:\n    paths:\n      - "2022/**"\n',
            1,
        )
        with self.assertRaisesRegex(ValueError, "GUARD_NOT_TRIGGERED_ON_EVERY_PR"):
            validate_guard_workflow(changed)

    def test_broadening_workflow_write_permission_is_rejected(self):
        changed = self.source.replace(
            "permissions:\n  contents: read\n",
            "permissions:\n  contents: write\n",
            1,
        )
        with self.assertRaisesRegex(ValueError, "PERMISSIONS_TOO_BROAD"):
            validate_guard_workflow(changed)

    def test_removing_reserved_channel_audit_is_rejected(self):
        changed = self.source.replace(
            "python3 -B 2022/beam/check_reserved_channel.py --root .",
            "echo unsafe",
            1,
        )
        with self.assertRaisesRegex(ValueError, "GUARD_REQUIRED_TEST_MISSING"):
            validate_guard_workflow(changed)


if __name__ == "__main__":
    unittest.main()
