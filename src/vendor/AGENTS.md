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

## Current contents

| Package | Upstream | Pin |
|---|---|---|
| `lkml/` | github.com/joshtemple/lkml | (set when vendored — see VENDOR_PIN.md) |

## If you need to patch the grammar

1. Document the issue and the upstream PR status in `VENDOR_PIN.md`
2. Make the minimal change in the vendored source
3. Add a regression test in `tests/` that would fail without the patch
4. Commit with message: `fix(vendor/lkml): <description> [upstream: <issue-or-pr-url>]`
