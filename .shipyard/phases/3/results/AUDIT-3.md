# Security Audit Report — Phase 3 (Snakes Racer Mode: Species Dialog + Wire-up)

**Date:** 2026-05-15
**Auditor:** Security & Compliance Auditor (Claude)
**Phase commits:** ded3720, b65bbc2, 07e4183, c4f1271, 75a62a2, 9f56ace
**Verdict:** CLEAN

---

## Executive Summary

**Overall verdict:** CLEAN
**Risk Level:** Low

Phase 3 is a pure UI refactor and new modal dialog addition to a local desktop game. No external interfaces, no network I/O, no new dependencies, and no user-controlled data flows into file-system or process operations. The composite image builder reads asset files at paths derived entirely from compile-time constants; the species selector can only return one of two hard-coded string literals. There are no findings that block shipping.

---

## STRIDE Threat Model (abbreviated — local desktop app)

| Threat | Surface in this phase | Assessment |
|--------|----------------------|------------|
| Spoofing | N/A — no auth, single-user local app | Not applicable |
| Tampering | Tk dialog state; `selected[0]` closure | Benign — only reachable via button callbacks that set a known literal |
| Repudiation | No audit logging — acceptable for a game | Not applicable |
| Information Disclosure | PIL opens local asset files; no network | No risk |
| Denial of Service | `Image.open` + resize on fixed-size PNGs/JPGs | Negligible; files are bundled assets |
| Elevation of Privilege | N/A — no privilege model | Not applicable |

---

## Scope Check Results

### 1. Secrets Scanning

Scanned all changed files (`constants.py`, `dialogs.py`, `main.py`, `race.py`, `tests/test_constants.py`, both `.shipyard/` SUMMARY files) for API keys, tokens, passwords, connection strings, and base64-encoded credentials.

**Result: No secrets found.** The diff contains only UI layout constants, PIL image operations, and tkinter widget wiring. The `.shipyard` SUMMARY files contain only commit SHAs and test-run metadata.

### 2. Dependency Audit

`requirements.txt` is **unchanged** (pillow, pygame-ce — no version pins, same as pre-Phase-3). `turtle_race.spec` is **unchanged**.

Advisory (carry-forward, not new): neither dependency is version-pinned. This is a pre-existing condition, not introduced in Phase 3.

**Result: No new dependency risk introduced.**

### 3. Asset-Loading Code (PIL)

`get_user_species()` builds two composite images from paths sourced exclusively from `SPECIES["turtles"]["images"]` and `SPECIES["snakes"]["images"]` — both are module-level dicts populated from compile-time string literals in `constants.py`. No user input touches these paths.

`get_user_bet(species)` similarly reads from `species_images[name]` where `species` can only be `"turtles"` or `"snakes"` (enforced by the dialog's button-only dismissal and WM_DELETE_WINDOW no-op).

Worst-case failure mode: `FileNotFoundError` or `KeyError` if an asset file is missing — an application crash, not an exploitable condition.

**Result: Clean.**

### 4. `get_user_species()` Return Value Trust Boundary

The function returns `"turtles"` or `"snakes"` via `make_cb(value)` closures bound to button `command=` handlers. The window cannot be closed by any other means (`WM_DELETE_WINDOW` is a no-op). The return value flows into `create_racers(species)` and `get_user_bet(species)`.

- `create_racers` raises `KeyError` on an unrecognised species (documented, acceptable).
- `get_user_bet` raises `ValueError` on an unrecognised `bet_layout` value (explicit `else: raise ValueError`).

Both failure paths are crash-only — no privilege escalation, no data exfiltration.

**Result: Clean.**

### 5. IaC / Container Security

Not applicable. No Dockerfile, Terraform, or Ansible files changed.

### 6. Configuration Security

No configuration files changed. `turtle_race.spec` unchanged.

**Result: N/A.**

---

## Detailed Findings

None. No Critical, Important, or Advisory findings are raised for this phase.

---

## Cross-Component Analysis

The species string produced by `get_user_species()` flows through three consumers: `create_racers(species)`, `get_user_bet(species)`, and implicitly the race win/lose message (via `user_bet` index arithmetic). All three consumers treat the string as a dict key into `SPECIES`, which is a module-level constant. The trust boundary is well-contained: only the two hard-coded button callbacks can populate `selected[0]`, and both values are valid `SPECIES` keys.

No coherence gaps were found between the new dialog layer and the downstream consumers.

---

## Analysis Coverage

| Area | Checked | Notes |
|------|---------|-------|
| Code Security (OWASP) | Yes | No injection surfaces; all input is button-driven |
| Secrets & Credentials | Yes | Full diff scanned; nothing found |
| Dependencies | Yes | requirements.txt unchanged; no new packages |
| IaC / Container | N/A | No IaC files in scope |
| Configuration | Yes | turtle_race.spec unchanged |
