# Security Audit Report — Phase 2

**Verdict:** CLEAN
**Risk Level:** Low

Phase 2 is a pure internal refactor: `N_LANES` deleted from `constants.py`, all
geometry functions in `tracks.py` updated to accept an explicit `n` parameter,
`race.py` renamed to the racer-neutral API, and `main.py` wired to the new
signatures. No new external interfaces, I/O paths, network surfaces, or
dependencies were introduced. There are no security findings.

---

## STRIDE Threat Model (scoped to changes)

| Threat | Surface in this diff | Finding |
|--------|----------------------|---------|
| Spoofing | None — no auth touched | N/A |
| Tampering | `create_racers(species)` reads from a module-level dict | Input is hard-coded at the call site (`"turtles"`); no user data path |
| Repudiation | `print()` race log unchanged | No regression |
| Information Disclosure | Error messages unchanged | No regression |
| Denial of Service | Geometry functions now accept `n` | `n` is always `len(racers)`, derived from `SPECIES["turtles"]`, a compile-time constant — no user-controlled amplification |
| Elevation of Privilege | No auth/authz code touched | N/A |

---

## Scope Checks

### OWASP Top 10

Not applicable — this is a local desktop GUI application with no web surface,
no network listener, no user-supplied data reaching any dangerous sink. The
refactor introduces no injection points, no new deserialization, and no
authentication changes.

### Secrets Scanning

Grep over all changed `.py` files for API keys, tokens, passwords, and
connection strings returned no matches. `constants.py` contains only color
hex literals (`#E89F4F`) and local file paths — no credentials. No `.env`
file exists in the repository.

### Dependency Vulnerabilities

`requirements.txt` is unchanged (two entries: `pillow`, `pygame-ce`).
Installed versions are Pillow 12.2.0 and pygame-ce 2.5.7. No lock-file
regression. No new packages introduced in this phase.

### IaC / Container Security

Not applicable — no Dockerfile, Terraform, or Ansible files were touched.
`turtle_race.spec` is unchanged in this phase (confirmed via `git diff`).

### Configuration Security

No configuration files changed. Debug mode, logging verbosity, and CORS
settings are unaffected.

### Code-pattern Risk: `create_racers(species)` key lookup

`race.py:141` executes `SPECIES[species]` where `species` is the string
`"turtles"` hard-coded at `main.py:28`. There is no path from user input
(dialog choices, file reads, environment variables) to this argument. A
`KeyError` on a bad key would crash the process — consistent with Python's
normal behaviour for a logic error in a desktop app, and not an exploitable
condition given the fixed call site.

---

## Findings

None.

---

## Analysis Coverage

| Area | Checked | Notes |
|------|---------|-------|
| Code Security (OWASP) | Yes | No web surface; refactor only |
| Secrets & Credentials | Yes | Full grep over changed files — clean |
| Dependencies | Yes | `requirements.txt` unchanged; versions verified |
| IaC / Container | N/A | No IaC files touched |
| Configuration | Yes | No config files changed |
| Cross-component coherence | Yes | `main.py` -> `race.py` -> `tracks.py` data flow traced; `n` always derived from `len(racers)`, which is compile-time fixed |
