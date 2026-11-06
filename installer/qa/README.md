<!--
Dosya Yolu: installer/qa/README.md
Amac: Public Ragnar test installerinin Beam build ve dagitim sinirini kaydetmek
Modul - Markdown
Version: 1.0.2-qa
Aciklama: Public source-only reusable workflow; no private repo fetch or gameplay publication
Bagimli Oldugu Katman: GitHub Actions | LevelUpRagnarok/beam-patcher | Turkuaz QA
-->

# Turkuaz Ragnarok Online - Public Windows Installer (QA)

The public installer artifact is **built and downloaded from the public
distribution repository**: `LevelUpRagnarok/ragnarokclientpatch`. The source
repository `LevelUpRagnarok/beam-patcher` remains the source of Rust/Windows
installer code. The private `LevelUpRagnarok/RagnarokClient` repository is not
contacted by this QA build or by the installed preview executable.

## Provenance and reproducible build

- Workflow: `.github/workflows/public-ragnar-installer-qa.yml`
- Pinned Beam source workflow and source commit:
  `536c155af23c0528edfdbe88ef1c54215ae74bdf`
- Turkuaz Installer Community upstream dependency is separately pinned
  within the Beam QA reusable workflow.
- GitHub Actions executes the reusable workflow **in the public
  distribution repository context**, so its temporary Windows EXE
  artifact appears on the run under `LevelUpRagnarok/ragnarokclientpatch`.
- Client downloads only the resulting `Turkuaz-Ragnarok-Online-Setup.exe`,
  not a source repo, PAT, development SDK, private git checkout, or
  embedded Turkuaz .NET/WinUI distribution.
- All upstream code inputs are readable public repos; the workflow
  requests `contents: read` only. No cross-repo write secret required.

## Download and publish boundaries

This initial integration intentionally creates **GitHub Actions QA
artifacts**, not a production release, tag, Pages deployment or active
patch feed. GitHub may require login to retrieve Actions artifacts.
A stable anonymous public `download_url` requires a separate,
explicitly approved production publication design (for example a
signed GitHub Release in this public repo) after client compatibility
and signing checks.

The private game content is not included. This is the read-only Beam
visual preview, **not** a working private Ragnarok game client. The
product installer may use a public HTTPS endpoint in production, but
must never attempt to clone a private repository at the player's PC.

The `2015` channel aliases (`/data`, `/beam`, `plist.txt`)
remain unchanged. The `2022` patch channel remains `ready: false`
and `publish_allowed: false`. No `2022/data` patch, active
`version.json`, or client runtime settings may be created by this
installer QA workflow.

## Upgrade path after explicit approval

1. Build and review **signed release candidates** from trusted commits.
2. Complete client loader, GRF/backups/rollback and network tests.
3. Publish final artifacts to a dedicated public distribution channel,
   using a narrowly scoped deploy identity under a separate release
   workflow. Never expose a private code-repo token to the player.
4. Publish a signed metadata file with HTTPS address, version, SHA-256
   and source commit for the launcher to verify before update/install.
5. Preserve the existing 2015 channel and do not change 2022 policy
   without explicit user approval and matching compatibility evidence.

Reference standard look:
https://github.com/TurkuazLabs/TurkuazInstaller/pull/60

## Tests

`python3 -B -m unittest discover -s tests -p test_public_installer_contract.py -v`
confirms repository ownership, immutability and the absence of an
unapproved deployment. The called Windows CI builds and exercises the
real QA installer (including TurkuazInstaller CLI install/uninstall).
A green Actions build is not a real Windows 10 GUI smoke.


## Canonical product name and internal profile identity (2026-10-24)

- User-visible app and standalone EXE: **Turkuaz Ragnarok Online**, `Turkuaz-Ragnarok-Online-Setup.exe`.
- Internal `client-identity.json` in the QA Actions artifact distinguishes
  `profile_id=preview-qa`, `installer_version=0.1.0`,
  immutable public Beam `source_commit`, `channel=qa` and
  `production_publish_allowed=false`; `client_year`, `client_build` and
  `packetver` are all null for this **visual preview**.
- Reserved future client profiles `classic-2015` and `renewal-2022`
  are *not* buildable by this QA workflow until real signed game-client
  provenance and separately tested patch channels exist. The existing
  `2015` patch aliases are not migrated and `2022 ready: false` /
  `publish_allowed: false` remain unchanged.
- The artifact name (internal) records `preview-qa` and the workflow
  source commit. The human-facing EXE filename does not leak protocol
  year or unrelated build identifiers.
- Concept C installer artwork is an **optional SHA-256-pinned file** at
  `tools/windows/ragnar-turkuaz-qa/branding/concept-c-background.png`
  in the pinned Beam commit, not a network download. Until that exact
  reviewed binary is committed, setup falls back to the earlier teal
  gradient. No unapproved remote image, AV bypass or production release.
