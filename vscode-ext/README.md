# Strata LookML Governance — VS Code Extension

Brings Strata's LookML governance, impact analysis, and field navigation directly into
VS Code. The extension is a **thin presentation layer** that shells out to the `strata`
CLI — no Python runtime is bundled.

> **Publisher placeholder:** publisher is currently set to `g-schumacher`. This must be
> confirmed/updated before any Marketplace listing. See `conductor/slice-vscode-c-packaging.md`.

---

## Requirements

- VS Code ≥ 1.85.0
- [`strata` CLI](https://github.com/g-schumacher44/strata) installed and on PATH
  - Quick install: `pipx install strata`
- A LookML repo with `STRATA_REPO_PATH` set, or configure `strata.repoPath` in settings

---

## Commands

Open the Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`) and type **Strata**:

| Command | Description |
|---|---|
| **Strata: Build Graph** | Parse the LookML repo and build the IR cache. Shows node/edge counts on completion. |
| **Strata: Impact Analysis on Current File** | Shows which explores are impacted by the currently open `.lkml` file. |
| **Strata: Navigate Field Under Cursor** | Looks up the word under the cursor in the LookML graph and opens a brief in a side panel. |
| **Strata: Refresh Governance Diagnostics** | Re-runs orphan detection and populates the Problems panel with governance findings. |

---

## Configuration

| Setting | Default | Description |
|---|---|---|
| `strata.repoPath` | `""` | Path to the LookML repo root. Falls back to the first workspace folder. |

Example `.vscode/settings.json`:
```json
{
  "strata.repoPath": "/path/to/your/lookml-repo"
}
```

---

## Governance Diagnostics (Problems Panel)

When you save a `.lkml` file (or run **Strata: Refresh Governance Diagnostics**), the
extension runs `strata query orphans` and surfaces findings in the VS Code Problems panel:

- **Warning**: Orphaned views — views that are never used as explore base or join target
- Source: `Strata Governance`

Diagnostics are debounced 1500ms on save so rapid edits don't trigger repeated CLI calls.

---

## Activation

The extension activates automatically when:
- A file with language id `lookml` is opened
- The workspace contains any `*.lkml` file

---

## Installation (local VSIX)

```bash
cd vscode-ext
npm install
npm run compile
npm run package   # produces strata-vscode-0.1.0.vsix
code --install-extension strata-vscode-0.1.0.vsix
```

---

## Development

```bash
cd vscode-ext
npm install
npm run compile   # esbuild → dist/extension.js
npm run watch     # incremental rebuild on change
npm run lint      # ESLint check
```

---

## Open Questions (NEEDS OPERATOR)

1. **Publisher identity** — `g-schumacher` is a placeholder. Confirm the VS Code Marketplace publisher account before any public listing.
2. **Distribution mode** — Marketplace public, Marketplace private, or VSIX-only?
3. **Icon** — `media/icon.svg` is a placeholder. A designer asset is required before Marketplace listing.
