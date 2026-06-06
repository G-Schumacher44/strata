# Vendor — Frozen Dependencies

**Full governance:** `docs/GOVERNANCE.md`

---

## What is here

Vendored source for `lkml` (Josh Temple, MIT) pinned at a specific commit.
This replaces a `pip install lkml` runtime dependency so Strata has zero external
repo dependencies and full control over grammar patches.

## Hard constraints

- **Do not modify vendored source** for feature reasons or to work around bugs in
  your own code. If lkml is producing wrong output, the fix belongs in the caller,
  not here.
- **Cherry-pick only.** If an upstream lkml fix is needed, cherry-pick the specific
  commit. Reference the upstream PR/commit SHA in the commit message.
- **Never add new packages here.** Adding a vendored dependency requires a Conductor
  slice spec and explicit operator approval — it is an architecture decision, not a
  convenience.
- **Document the pin.** `src/vendor/lkml/VENDOR_PIN.md` must exist and contain the
  upstream repo URL, the pinned commit SHA, the pin date, and the reason for any
  local patches.

## How to vendor lkml (exact steps — do not deviate)

The goal is to copy source files only. No git history. No submodule. No second repo.

```bash
# 1. Clone to a temp path OUTSIDE the strata repo
git clone https://github.com/joshtemple/lkml /tmp/lkml-vendor-tmp

# 2. Record the commit SHA you are pinning
cd /tmp/lkml-vendor-tmp && git rev-parse HEAD

# 3. Copy the Python package source into vendor
#    Copy ONLY: lkml/*.py and lkml/grammar/ (if present)
cp -r /tmp/lkml-vendor-tmp/lkml /Volumes/t9/dev/tools/strata/src/vendor/lkml

# 4. Delete the clone — it must not remain
rm -rf /tmp/lkml-vendor-tmp

# 5. Write VENDOR_PIN.md (see template below)
# 6. Add src/vendor/lkml/ to the strata repo normally (git add)
```

**What NOT to do:**
- Do not `git clone` inside the strata repo directory
- Do not `git submodule add`
- Do not leave a `.git/` directory inside `src/vendor/lkml/`
- Do not `pip install lkml` and copy from site-packages

## VENDOR_PIN.md template

```markdown
# lkml Vendor Pin

Upstream: https://github.com/joshtemple/lkml
Pinned commit: <SHA from step 2>
Pin date: <YYYY-MM-DD>
License: MIT

## Local patches
None.

## Notes
<any legacy syntax issues encountered, upstream issue links>
```

## Current contents

| Package | Upstream | Pin |
|---|---|---|
| `lkml/` | github.com/joshtemple/lkml | (set when vendored — see lkml/VENDOR_PIN.md) |

## If you need to patch the grammar

1. Document the issue and the upstream PR status in `lkml/VENDOR_PIN.md`
2. Make the minimal change in the vendored source
3. Add a regression test in `tests/` that would fail without the patch
4. Commit with message: `fix(vendor/lkml): <description> [upstream: <issue-or-pr-url>]`
