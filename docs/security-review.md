# Strata — Security & Code-Review Report

**Date:** 2026-06-07
**Scope:** Full repository review of `strata` (offline-first LookML "repo brain" + stdio MCP server),
oriented toward **enterprise/work approval**.
**Reviewer focus (requested):** OAuth security, local trust boundaries, offline-only MCP
(official vendor SDKs such as Looker excepted), DRY/modular code, robust hardening.
**Companion doc:** see [`security-hardening.md`](./security-hardening.md) for deployment-time hardening guidance.

> This is a **findings report only** — no source code was changed in this pass. Each finding cites
> verified `file:line` evidence and a recommended remediation. Recommendations reflect the owner's
> chosen direction: **bundle JS assets locally** for air-gapped use, and **harden the existing token
> file** rather than add a keyring dependency.

---

## 1. Executive summary / approval readiness

Strata's architecture is **well-suited to enterprise approval**: the MCP server is stdio-only, the
default path is fully offline, there are no LLM/cloud SDK dependencies, and there is no use of
`eval`/`pickle`/`os.system`/unsafe YAML. The single external egress point (Looker System Activity) is
read-only and strictly opt-in.

The blocking work before sign-off is **input/trust-boundary hardening** and **offline artifact
integrity** — not architectural change. The items below are localized and low-risk to implement.

| Posture | Items |
|---|---|
| ✅ **Strengths (verifiable)** | stdio-only transport; offline-first default; no LLM/external SDKs; opt-in gated live adapter; no dynamic-code/unsafe-deserialization; in-house LookML parser (no vendored `lkml`) |
| ⛔ **Blocking for approval** | No HTTPS/scheme enforcement on Looker URL (H); MCP tools raise raw exceptions over stdio (H); generated artifacts depend on public CDNs / not air-gap-safe (H) |
| ⚠️ **Should-fix** | token-file perms unchecked on read; no refresh flow; unvalidated chart output path; unescaped HTML title; duplicated/unguarded config loading; corrupt-cache silently accepted |

**Severity legend:** `HIGH` approval-blocking · `MED` should-fix before broad rollout · `LOW` defense-in-depth ·
`PASS` verified-good (evidence for reviewers) · `REFUTED` flagged by scan but not a real risk.

---

## 2. Constraint-compliance evidence (the "approval wins")

These hold today and are worth presenting proactively to a reviewer:

| # | Constraint | Status | Evidence |
|---|---|---|---|
| C1 | MCP transport is stdio-only; no HTTP transport | **PASS** | `src/strata/mcp/server.py:120` → `create_server().run(transport="stdio")`; no Flask/FastAPI/uvicorn imported anywhere in `src/strata` |
| C2 | Offline-first default; network is opt-in | **PASS** | `src/strata/pipeline.py` `build_graph()` never imports `urllib`/Looker; live access only via `build_graph_from_looker()` + `--looker-url` + token; `DisabledLookerAdapter` (`src/strata/l1/looker.py:43`) makes live access deliberate, not accidental |
| C3 | L0/L1 never call an LLM or external API | **PASS** (with the sanctioned Looker exception) | No `anthropic`/`openai`/`google`/`langchain` imports; only egress is the opt-in Looker adapter using stdlib `urllib` |
| C4 | `lkml` not vendored / not pip-installed | **PASS** | In-house scanner at `src/strata/ir/parser.py`; `src/vendor/` empty per policy |
| C5 | No dynamic code execution / unsafe deserialization | **PASS** | No `eval`/`exec`/`os.system`/`subprocess`/`pickle`; `yaml.safe_load` used (`src/strata/mcp/tools.py:142`) |

> Note (C1): a **localhost-only** dev HTTP server exists in `src/strata/cli/dashboard.py` for serving
> pre-built artifacts. It binds `localhost` and is separate from the MCP server. Call it out to reviewers
> as developer tooling, not part of the MCP surface.

---

## 3. Findings — OAuth & secrets

### 3.1 [HIGH] No HTTPS/scheme enforcement on the Looker URL
`_normalize_url()` only strips a trailing slash:
```
src/strata/l1/looker.py:277
def _normalize_url(value: str) -> str:
    return value.rstrip("/")
```
The normalized URL is used for the OAuth `/auth` URL, the `/token` code exchange, and all bearer-token
API requests (`looker.py:104,128,140,167`). A user-supplied `--looker-url` / `LOOKER_URL` of
`http://…` or an arbitrary host means the **authorization code and access token are transmitted in the
clear / to an attacker-controlled endpoint**.
**Recommendation:** require an `https://` scheme (permit `http://localhost` only for the OAuth callback),
reject malformed URLs, and validate before any request or token save.

### 3.2 [MED] Refresh token stored but never used
`LookerToken.refresh_token` is persisted (`looker.py:61,75,127`) but there is no refresh-grant code path.
Once `expires_at` passes, calls fail with no recovery and the user must re-run `strata auth login`.
**Recommendation:** implement the refresh-token grant; refresh transparently when near expiry.

### 3.3 [MED] Token-file permissions set on write but not verified on read
Write hardens correctly:
```
src/strata/l1/looker.py:96-100  → mkdir(mode=0o700), chmod(0o600)
```
…but `load_token()` (`looker.py:89-93`) reads the file with no permission check. A token file made
world-readable out-of-band is used without warning.
**Recommendation (harden-the-file):** on read, warn or refuse if permissions are looser than `0600`.

### 3.4 [LOW] API error messages embed the full response body
```
src/strata/l1/looker.py:172-173
detail = exc.read().decode("utf-8", errors="replace")
raise LookerAPIError(f"Looker API request failed: HTTP {exc.code} {detail}")
```
If exceptions are logged, response bodies (potentially sensitive) propagate into logs.
**Recommendation:** truncate/redact the included detail.

### 3.5 [LOW] `~/.strata/config.json` written without explicit permissions
`src/strata/cli/bootstrap.py:143` writes the config (which can include `bq_project` and the repo path)
using the default umask, unlike the token file.
**Recommendation:** create the dir `0o700` and file `0o600` for consistency.

---

## 4. Findings — Trust boundaries & input validation

### 4.1 [HIGH] MCP tools raise raw exceptions over stdio
Tool functions assume well-formed input and raise unguarded exceptions, e.g.:
```
src/strata/mcp/tools.py:102   raise KeyError(f"physical_table not found in IR: {physical_table}")
src/strata/mcp/tools.py:14    graph.get_node(...) → KeyError on unknown field
src/strata/mcp/tools.py:184   raise KeyError(f"skill not found: {name}")
```
An unknown field/explore/table from the agent surfaces as an unstructured exception on the stdio
protocol, which can abort the session rather than return a clean error.
**Recommendation:** wrap tool dispatch to return a structured `{"error": "..."}` payload; add error-path tests.

### 4.2 [MED] Unvalidated chart output path
`strata_render_chart` passes the caller-supplied `out_path` straight through to `render_chart`, which
`mkdir`s the parent and writes the file:
```
src/strata/mcp/tools.py:148   path = render_chart(spec, rows, Path(out_path))
src/strata/viz/render.py:79-81  out_path.parent.mkdir(parents=True, exist_ok=True); out_path.write_text(...)
```
An agent-supplied absolute/`..` path writes HTML anywhere the process can write (e.g. clobbering files).
**Recommendation:** constrain output to a designated workspace/output directory; reject paths that escape it.

### 4.3 [MED] Unescaped HTML title injection in generated charts
```
src/strata/viz/render.py:77
html = _HTML.format(title=title, spec_json=json.dumps(spec, indent=2))
```
`title` (from the spec) is interpolated into `<title>{title}</title>` without escaping → HTML/JS
injection into the produced file.
**Recommendation:** `html.escape(title)` before formatting.

### 4.4 [LOW] Vega-Lite spec embedded verbatim
The full spec is embedded via `json.dumps` (`render.py:77`). Vega-Lite specs can reference remote data
loaders (`"url"`, `"datasets"`), so a hostile spec could trigger fetches when the file is opened. Risk
is low because specs are template/agent-sourced, but worth noting.
**Recommendation:** document the trust assumption; optionally strip `url`/`datasets` from inline specs.

### 4.5 [REFUTED — documented as checked] `strata_skill` path traversal
An automated scan flagged `strata_skill(name)` for traversal. **Not exploitable:**
```
src/strata/mcp/tools.py:181-184
for skill_file in skills_dir.rglob("SKILL.md"):
    if skill_file.parent.name == name:
        return skill_file.read_text(...)
```
It only matches files literally named `SKILL.md` whose **parent directory name** equals `name`, within
`skills_dir`. A value like `../../etc` cannot match a parent-dir name and cannot escape the tree.
Recorded as reviewed; no action needed.

---

## 5. Findings — Offline integrity

### 5.1 [HIGH for air-gap] Generated HTML depends on public CDNs
Both artifact renderers load JavaScript from public CDNs:
```
src/strata/viz/render.py:27-29        cdn.jsdelivr.net/npm/vega, vega-lite, vega-embed
src/strata/outputs/dashboard.py:131-134  cdnjs.cloudflare.com (cytoscape, dagre, chart.js), unpkg.com (cytoscape-dagre)
```
On an air-gapped or egress-restricted machine the charts/dashboard **do not render**, and on a normal
machine **opening an artifact reaches out to third-party CDNs** from the viewer's browser — both are
common enterprise-review objections.
**Recommendation (owner-chosen):** vendor these JS libraries into the package and reference them via
local/relative paths; declare them as packaged assets in `pyproject.toml`. This makes artifacts fully
self-contained and offline-safe.

### 5.2 [INFO] No static guard on the offline boundary
The "L0/L1 never touch the network" guarantee is **convention-only** — enforced by review, not by a
test. A future import could silently violate it.
**Recommendation:** add an import-guard test asserting that `urllib`/`socket` (and Looker modules) are
**not** imported on the default MCP/pipeline path. This converts the guarantee into something a reviewer
can see enforced in CI.

---

## 6. Findings — DRY & hardening

### 6.1 [MED] `_repo_path()` duplicated three times, each with unguarded JSON parse
Three identical implementations resolve the repo path (env → `~/.strata/config.json` → cwd):
```
src/strata/mcp/server.py:146
src/strata/cli/query.py:33
src/strata/cli/mcp.py:110
```
Each calls `json.loads(config.read_text())` with no error handling — a malformed `config.json` raises
an unhandled `JSONDecodeError`, and a missing `repo_path` key silently falls back to cwd (possibly the
wrong repo).
**Recommendation:** extract a single `src/strata/config.py` with `load_repo_path()` (safe parse +
validation), and consolidate the parallel skills/charts/conductor directory resolvers
(`server.py:123-143` vs `viz/render.py:12-19`).

### 6.2 [MED] Broad `except Exception` swallows failures
`src/strata/cli/mcp.py:66,75` catch all exceptions during directory checks, masking real errors
(permissions, disk).
**Recommendation:** narrow the exception types and surface/log the failure.

### 6.3 [MED] No cache-schema validation
`IRGraph.from_dict()` / `src/strata/ir/store.py:45` default missing keys silently, so a truncated or
corrupt SQLite cache yields a partial graph with no error — leading to silently incomplete analysis.
**Recommendation:** validate required keys (or version the cache and rebuild on mismatch).

### 6.4 [Test gaps] Security-relevant paths are untested
Current suite: **53 passing tests**. Not covered: config edge cases (missing/malformed `config.json`),
Looker URL validation, chart output-path handling, MCP tool error paths, and the offline import guard
(5.2). These are the paths a reviewer is most likely to probe.
**Recommendation:** add targeted tests as part of the remediation pass.

---

## 7. Prioritized remediation backlog

| Rank | Finding | Sev | Recommended fix | Effort |
|---|---|---|---|---|
| 1 | 3.1 Looker URL scheme | HIGH | Enforce `https://` (+ `http://localhost` callback only), validate URL | S |
| 2 | 4.1 MCP raw exceptions | HIGH | Structured `{"error": …}` dispatch wrapper + tests | M |
| 3 | 5.1 CDN assets | HIGH | Bundle JS locally, reference relative paths, package assets | M |
| 4 | 5.2 Offline import guard | INFO→ enables PASS | Import-guard test on default path | S |
| 5 | 3.3 Token perms on read | MED | Warn/refuse if perms > 0600 | S |
| 6 | 3.2 Refresh flow | MED | Implement refresh-token grant | M |
| 7 | 4.2 Chart output path | MED | Constrain to output dir / reject escapes | S |
| 8 | 4.3 HTML title escaping | MED | `html.escape(title)` | XS |
| 9 | 6.1 Config dedup | MED | `strata/config.py` + safe parse; consolidate dir resolvers | M |
| 10 | 6.3 Cache validation | MED | Validate/version cache | S |
| 11 | 6.2 Broad excepts | MED | Narrow + log | XS |
| 12 | 3.4 / 3.5 error redaction / config perms | LOW | Truncate detail; `0600`/`0700` config | XS |
| 13 | 4.4 Vega spec `url` | LOW | Document; optional strip | XS |
| 14 | 6.4 Security tests | — | Add coverage for the above | M |

*Effort: XS < S < M.*

---

## 8. Verification of this report
Every finding was confirmed by reading the cited source (`l1/looker.py`, `mcp/tools.py`, `viz/render.py`,
`mcp/server.py`, `outputs/dashboard.py`, `cli/*.py`). Cross-checks run during drafting:
`grep -n "transport=" src/strata/mcp/server.py`,
`grep -rn "jsdelivr|cloudflare|unpkg|cdn" src/strata`,
`grep -rn "def _repo_path" src/strata`.
No code was executed or modified; the existing test suite (53 passing) and `scripts/validate.py`
remain green by construction. The one overstated scan result (skill traversal) is explicitly downgraded
to REFUTED in §4.5.
