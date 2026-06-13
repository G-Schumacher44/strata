# Slice vscode-a: VS Code Extension — Scaffold + CLI Bridge

Date: 2026-06-13
Status: stable
Phase: vscode-tier1
Depends: none
Branch: feature/vscode-extension

```yaml
conductor_mode: slice
context_budget: medium
handoff_required: true
stable_tag_required: false
```

## Objective

Bootstrap a TypeScript VS Code extension under `vscode-ext/` that detects the `strata`
CLI on PATH and exposes three commands: **Build Graph**, **Impact Analysis on Current File**,
and **Navigate Field Under Cursor**. Each command shells out to the `strata` CLI with JSON
output, parses the result, and renders it in an output channel or webview panel. This is
a **presentation layer only** — no Python runtime bundled, no parallel backend. If `strata`
is not on PATH, the user is prompted to install via `pipx install strata`.

## Scope

- New directory: `vscode-ext/` (fully isolated from all Python source)
- TypeScript / VS Code Extension API (VS Code engine ≥1.85.0)
- Toolchain: esbuild bundler, TypeScript 5.x, ESLint @typescript-eslint
- `src/clibridge.ts` — `detectStrata()`, `runStrataJSON()`, command-specific wrappers
- `src/extension.ts` — activate/deactivate, command registration, output channel
- Activation: `onLanguage:lookml`, `workspaceContains:**/*.lkml` globs
- LookML detection: language id `lookml`; globs `**/*.lkml`, `**/*.view.lkml`, `**/*.model.lkml`

## Commands Registered

| Command ID | Title | CLI invocation |
|---|---|---|
| `strata.buildGraph` | Strata: Build Graph | `strata build --repo <workspace> --json` |
| `strata.impactAnalysis` | Strata: Impact Analysis on Current File | `strata query scope <current_file>` |
| `strata.navigateField` | Strata: Navigate Field Under Cursor | `strata query navigate <word> --json` |
| `strata.refreshDiagnostics` | Strata: Refresh Governance Diagnostics | (see Slice B) |

## Implementation Order

1. `package.json` — extension manifest, activationEvents, contributes.commands
2. `tsconfig.json`, `.eslintrc.json`, `esbuild.js` — toolchain wiring
3. `src/clibridge.ts` — `detectStrata()`, `runStrataJSON()`, command wrappers
4. `src/extension.ts` — activation, command registration, output channel renderer
5. `npm install && npm run compile` — must exit 0
6. `npm run lint` — must exit 0

## Hard Constraint

`strata` is **never bundled**. The extension detects it on PATH via `spawnSync('strata', ['--version'])`.
If not found: show actionable error with `pipx install strata` copy-to-clipboard option.

## Acceptance Criteria

- [x] `vscode-ext/package.json` present and valid JSON
- [x] `npm install` exits 0
- [x] `npm run compile` (esbuild → `dist/extension.js`) exits 0
- [x] `npm run lint` (ESLint) exits 0
- [x] Extension declares `strata.buildGraph`, `strata.impactAnalysis`, `strata.navigateField`
- [x] `detectStrata()` checks PATH; missing strata prompts `pipx install strata`
- [x] All three commands shell out via `clibridge.ts` using `spawnSync`
- [x] Results render in a named output channel ("Strata") or webview
- [x] `conductor/handoff-log.md` — STABLE entry with Commit hash
