#!/usr/bin/env python3
# Dosya Yolu: REPO_ROOT/tests/check_patch_http_endpoints.py
# Amac: Public patch URL'lerini gercek HTTP GET ve SHA256 ile salt-okunur denetlemek
# Modul - Python CLI
# Version: 1.1.0
# Aciklama: Kanonik URL zorunlu; eski raw adresinin durumu ayrica raporlanir
# Bagimli Oldugu Katman: Testing
"""Read-only HTTP smoke for the actual 2015 patch feed and small THOR assets."""
import argparse
import hashlib
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

NEW_BASE = "https://raw.githubusercontent.com/LevelUpRagnarok/ragnarokclientpatch/main/"
OLD_BASE = "https://raw.githubusercontent.com/b1glord/ragnarokclientpatch/main/"
# Fixed 2015 assets only; one real 8.8-MB map patch exercises larger downloads.
# This tool downloads but never executes or applies any archive.
PATHS = (
    "plist.txt", "2015/plist.txt",
    "data/custom-cursor.thor", "2015/data/custom-cursor.thor",
    "data/custom-maps01.thor", "2015/data/custom-maps01.thor",
)
MAX_RESPONSE = 16 * 1024 * 1024


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def http_get(base, relative, opener=None):
    """Return observed status and hash; do not infer a redirect or fallback."""
    opener = urllib.request.urlopen if opener is None else opener
    url = base + relative
    request = urllib.request.Request(
        url, headers={"User-Agent": "RagnarokPublicPatchReadOnlySmoke/1.0"})
    try:
        with opener(request, timeout=20) as response:
            status = response.status
            effective = response.geturl()
            data = response.read(MAX_RESPONSE + 1)
            if len(data) > MAX_RESPONSE:
                return {"url": url, "effective_url": effective, "status": status,
                        "error": "RESPONSE_TOO_LARGE", "bytes": len(data), "sha256": None}
            return {"url": url, "effective_url": effective, "status": status,
                    "bytes": len(data), "sha256": sha256(data), "error": None}
    except urllib.error.HTTPError as error:
        return {"url": url, "effective_url": error.geturl(), "status": error.code,
                "bytes": None, "sha256": None, "error": "HTTP_ERROR"}
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        return {"url": url, "effective_url": None, "status": None,
                "bytes": None, "sha256": None, "error": type(error).__name__}


def audit(root, opener=None):
    report = []
    failures = []
    legacy_warnings = []
    for relative in PATHS:
        path = root / relative
        if not path.is_file() or path.is_symlink():
            failures.append(f"LOCAL_SOURCE_MISSING: {relative}")
            continue
        expected = path.read_bytes()
        if not expected or len(expected) > MAX_RESPONSE:
            failures.append(f"LOCAL_SOURCE_SIZE_INVALID: {relative}")
            continue
        local_sha = sha256(expected)
        current = http_get(NEW_BASE, relative, opener=opener)
        previous = http_get(OLD_BASE, relative, opener=opener)
        current_ok = (current["status"] == 200 and current["error"] is None
                      and current["bytes"] == len(expected) and current["sha256"] == local_sha)
        previous_ok = (previous["status"] == 200 and previous["error"] is None
                       and previous["bytes"] == len(expected) and previous["sha256"] == local_sha)
        if not current_ok:
            failures.append(f"CANONICAL_RAW_FAILED: {relative} status={current['status']} error={current['error']}")
        if not previous_ok:
            legacy_warnings.append(f"LEGACY_RAW_NOT_COMPATIBLE: {relative} status={previous['status']} error={previous['error']}")
        report.append({"path": relative, "expected_bytes": len(expected), "expected_sha256": local_sha,
                       "canonical": current, "canonical_verified": current_ok,
                       "retired": previous, "retired_verified": previous_ok})
    return {"checks": report, "canonical_failures": failures,
            "legacy_warnings": legacy_warnings, "canonical_ok": not failures,
            "legacy_all_verified": not legacy_warnings}


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)
    result = audit(args.root)
    print("PUBLIC_PATCH_RAW_HTTP_AUDIT " + json.dumps(result, sort_keys=True))
    for message in result["legacy_warnings"]:
        print("::warning title=Legacy patch URL not verified::" + message)
    for message in result["canonical_failures"]:
        print("::error title=Canonical public patch HTTP failure::" + message)
    if not result["canonical_ok"]:
        return 1
    if not result["legacy_all_verified"]:
        print("PUBLIC_PATCH_CANONICAL_OK_LEGACY_RISK_REQUIRES_CLIENT_MIGRATION")
    else:
        print("PUBLIC_PATCH_CANONICAL_AND_LEGACY_URLS_VERIFIED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
