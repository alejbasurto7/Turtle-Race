# Security Audit Report — Phase 1 (Snakes Racer Mode: Data + Tests + Assets)

**Verdict:** CLEAN
**Risk Level:** Low

Phase 1 adds pure static data (constants, a config dict, 9 tests, 3 PNG assets, and one PyInstaller spec line). There is no user input, no network surface, no authentication, and no runtime code paths changed. All scope checks are negative.

---

## Scope Checks

### OWASP Top 10

N/A for this phase. No web surface, no HTTP handlers, no input parsing, no database interaction, no session management. The only changed runtime artifact is `constants.py`, which contains only string/int literals and one dict-of-dicts. No injection vectors exist.

### Secrets Scanning

Clean. The diff introduces:

- Three racer name strings (`"Shadow"`, `"Ralph"`, `"Anaconda"`)
- Three color literals (`"black"`, `"#E89F4F"`, `"green"`)
- Three integer length values
- Three relative asset paths

No API keys, tokens, passwords, connection strings, or encoded credentials are present. The hex value `#E89F4F` is a CSS color, not a credential; its origin is documented inline (`# Ralph hex per CONTEXT-1.md`).

### Dependency Audit

`requirements.txt` is unchanged (`pillow`, `pygame-ce`). No new dependencies were introduced. Installed versions at time of audit: Pillow 12.2.0, pygame-ce 2.5.7. `pip-audit` is not installed in this environment; a manual CVE check against the NVD and PyPI advisory database for these two packages at these versions shows no known critical or high CVEs as of May 2026. Lock files are not used (no `requirements.lock` or `pip.lock`), which is an existing pattern outside this phase's scope.

### IaC / Container Security

N/A. No Terraform, Ansible, Docker, or other IaC files were modified.

### Configuration Security (`turtle_race.spec`)

The single change adds one entry to the `datas=` list:

```
('assets/snakes/*.png', 'assets/snakes')
```

This bundles the three snake PNG files into the frozen executable under the `assets/snakes/` subdirectory, mirroring how turtle assets are already bundled. The glob is scoped narrowly to `*.png` within `assets/snakes/` — it will not accidentally pull in credentials or config files unless a misnamed file is placed there in the future. No sensitive data is exposed. `debug=False` and `console=False` remain unchanged in the spec.

### Asset Safety (PNG files)

All three files carry valid PNG signatures (`\x89PNG\r\n\x1a\n`). File sizes are 2.3 MB, 2.4 MB, and 2.6 MB — consistent with photographic or illustrated source art. No executable content can be embedded in a PNG that Pillow or the `turtle` module would execute; these runtimes decode pixel data only. No metadata-extraction risk exists in a local desktop context.

### Cross-Task Coherence

No cross-task concerns. Phase 1 adds no runtime code paths, so there are no auth/authz interactions, trust boundaries, or data flows to trace.

---

## Findings

None.

---

## Analysis Coverage

| Area | Checked | Notes |
|---|---|---|
| Code Security (OWASP) | Yes | No application code changed; static data only |
| Secrets & Credentials | Yes | Diff scanned; clean |
| Dependencies | Yes | `requirements.txt` unchanged; no new packages |
| IaC / Container | N/A | No IaC files in scope |
| Configuration | Yes | `turtle_race.spec` change is minimal and correct |
| Asset integrity | Yes | PNG signatures verified; file sizes plausible |
