# Handoff Log & State Preservation

<!-- Move completed entries to handoff-archive.md when starting a new block. Keep only the current active handoff here. -->

## Date: 2026-06-09 — Public Release Flow Guardrails
Commit: 24d6b09
Target Branch: dev
Status: stable

- Synced private `main`, `dev`, `origin/main`, and `origin/dev` to `5af4388`.
- Left `public/main` untouched at `e51de67`.
- Added the public release branch model in `docs/public-release.md`.
- Added `.publicignore` as the public export denylist.
- Added `scripts/check_public_release.py`, a read-only audit that compares a
  candidate ref against `public/main`.
- Added `tests/test_check_public_release.py`.
- Added `.github/workflows/public-release-audit.yml` with manual
  `workflow_dispatch`, `public-release/**` branch, and `public-v*` tag triggers.
  Manual runs fetch all `public` remote branches and can audit refs such as
  `public/public-release/YYYYMMDD`.
- Updated `scripts/README.md` with the public release audit command.

Conductor Mode: Patch
Context Budget: low
Context Loaded: `AGENTS.md`, `conductor/index.md`, active slice, `scripts/README.md`, public-related docs/workflows
Context Skipped: `output/`, `caches/`, `vendor/`, minified assets
Stage/DUOS: not used.
Ledger: not applicable.
Tag Posture: stable.

Gates:
- [x] `.venv/bin/python -m pytest` (101 passed)
- [x] `.venv/bin/strata validate` (PASS)
- [x] `.venv/bin/python scripts/check_public_release.py --base public/main --target HEAD` (EXPECTED FAIL: private HEAD includes `.publicignore` paths)
- [x] `git diff --check` (PASS)

Exact Next Steps: 
1. Push `dev` and create a private main-promotion branch via local merge-driver
   merge so `conductor/handoff-log.md` and `conductor/slice-*.md` do not enter
   `main`.
2. Open a PR from the promotion branch to `main`.
3. After merge to the default branch, use GitHub Actions → **Public release audit** → **Run workflow** with `target_ref=public/public-release/YYYYMMDD`.
