# Slice vscode-b: VS Code Extension — Governance Diagnostics

Date: 2026-06-13
Status: stable
Phase: vscode-tier1
Depends: slice-vscode-a
Branch: feature/vscode-extension

```yaml
conductor_mode: slice
context_budget: medium
handoff_required: true
stable_tag_required: false
```

## Objective

Surface Strata governance findings as native VS Code **Diagnostics** in the Problems panel.
A `DiagnosticCollection` named "Strata Governance" is populated by running
`strata query orphans` (JSON output), mapping each orphan record's `source_file` field to a
real workspace path, and creating a `vscode.Diagnostic` (Warning severity) at line 0 of
that file. Diagnostics refresh on the explicit `Strata: Refresh Governance Diagnostics`
command and are debounced 1500ms on LookML file save.

## Scope

- `src/govdiagnostics.ts` — `StrataGovernanceDiagnostics` class
- Debounced save listener registered in `extension.ts`
- VS Code `DiagnosticCollection` (Problems panel — not inline editor squiggles)
- LookML file detection: language id `lookml`; globs `**/*.lkml`, `**/*.view.lkml`, `**/*.model.lkml`
- Governance signals: orphaned views (dead explores, unused views) via `strata query orphans`
- Does NOT call any AI model — purely CLI shelling

## Orphan → Diagnostic Mapping

Orphan record schema (from `strata query orphans`):
```json
{ "id": "view:name", "kind": "view", "name": "name", "source_file": "views/name.view.lkml", "reason": "..." }
```

Mapping logic:
1. For each orphan, resolve `source_file` relative to `workspaceFolder.uri`
2. Create `vscode.Diagnostic` at `new vscode.Range(0, 0, 0, 0)` with message = `[Strata] Orphan <kind> '<name>': <reason>`
3. Severity = `vscode.DiagnosticSeverity.Warning`
4. Source = `"Strata Governance"`
5. Set `collection.set(uri, diagnostics)` grouped by file
6. Orphans with `source_file = null` are logged but not surfaced (no crash)

## Implementation Order

1. `src/govdiagnostics.ts` — class skeleton with `refresh()`, `scheduledRefresh()`, `dispose()`
2. Orphan fetch via `clibridge.queryOrphans(repoRoot)`
3. Mapping loop: orphan records → `vscode.Diagnostic` per URI
4. `extension.ts` integration: create collection, register save listener, wire refresh command
5. Debounce: store `NodeJS.Timeout` in class; clear on each save event

## Hard Constraint

If `strata` is not on PATH, `refresh()` is a no-op (no throw, no crash). The Problems panel
simply stays empty for Strata entries.

## Acceptance Criteria

- [x] `StrataGovernanceDiagnostics` class defined in `govdiagnostics.ts`
- [x] `refresh(repoRoot?)` fetches orphans, maps to `vscode.Diagnostic[]`, calls `collection.set()`
- [x] `scheduledRefresh(repoRoot?)` debounces 1500ms before calling `refresh()`
- [x] Orphan `source_file` mapped to workspace-relative URI
- [x] Orphans with null/missing `source_file` skipped gracefully
- [x] Falls back to no-op if `strata` not on PATH
- [x] `dispose()` calls `collection.dispose()` and clears debounce timer
- [x] Save listener registered in `extension.ts` for LookML file patterns
- [x] `Strata: Refresh Governance Diagnostics` command clears and repopulates
- [x] `npm run compile` still exits 0 after adding this module
- [x] `conductor/handoff-log.md` — STABLE entry with Commit hash
