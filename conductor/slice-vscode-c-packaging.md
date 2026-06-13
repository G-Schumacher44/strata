# Slice vscode-c: VS Code Extension — Packaging Scaffold (MVP)

Date: 2026-06-13
Status: stable (scaffold only — NOT published)
Phase: vscode-tier1
Depends: slice-vscode-b
Branch: feature/vscode-extension

```yaml
conductor_mode: slice
context_budget: low
handoff_required: true
stable_tag_required: false
```

## Objective

Scaffold the minimum packaging artefacts so the extension can be bundled with `vsce package`
and installed locally (`code --install-extension strata-vscode-*.vsix`) for internal testing.
This slice does **NOT** publish to the VS Code Marketplace — that gate is blocked on operator
sign-off for publisher identity, icon, and marketplace metadata.

## Scope

- `vscode-ext/README.md` — user-facing extension README (install, config, commands)
- `vscode-ext/.vscodeignore` — exclude dev artifacts from .vsix bundle
- `vscode-ext/package.json` updates — `vsce package` script, icon path, categories
- `vscode-ext/media/icon.svg` — placeholder SVG icon (designer asset TBD)
- `vscode-ext/package.json` — publisher set to placeholder `g-schumacher` (FLAGGED)

## Open Questions — NEEDS OPERATOR DECISION

| # | Question | Default used |
|---|---|---|
| 1 | **Publisher identity** — VS Code Marketplace publisher account? | Placeholder `g-schumacher` |
| 2 | **Distribution mode** — marketplace public, marketplace private, VSIX-only? | VSIX-only for now |
| 3 | **Icon** — placeholder SVG only; final design asset required before listing | `media/icon.svg` placeholder |
| 4 | **Extension name** — `strata-vscode` or `strata-lookml`? | `strata-vscode` |
| 5 | **Engine floor** — VS Code 1.85.0+? | `^1.85.0` |

## Implementation Order

1. `README.md` — requirements, installation, commands, config reference
2. `.vscodeignore` — exclude `src/`, `node_modules/`, `*.ts`, `.eslintrc*`, `tsconfig*`, `esbuild.js`
3. `media/icon.svg` — placeholder (simple SVG with "S" glyph)
4. `package.json` — `"package": "vsce package"` script, `"icon": "media/icon.svg"`, categories
5. Verify `npm run compile` still exits 0

## Acceptance Criteria

- [x] `vscode-ext/README.md` written with installation, commands, and configuration reference
- [x] `vscode-ext/.vscodeignore` excludes `src/`, `node_modules/`, dev tool configs
- [x] `package.json` has `"package": "vsce package"` script
- [x] `media/icon.svg` placeholder present
- [x] Publisher `g-schumacher` flagged as placeholder in both README and this spec
- [x] Open questions table documented above and mirrored in handoff
- [x] `npm run compile` exits 0 after packaging scaffold added
- [x] `conductor/handoff-log.md` — STABLE entry with Commit hash
