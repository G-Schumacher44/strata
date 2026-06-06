# STRATA — Thesis, Intent & Outline

> **GS Analytics // Strata** — *a deterministic, governed framework for mapping, auditing, and protecting a LookML monorepo.*
> Working name. Alternatives if it doesn't land: *Sift, Bedrock, Quarry, Lodestar.*

| | |
|---|---|
| **Author** | Garrett Schumacher (GS Analytics) |
| **License (intended)** | Apache 2.0 |
| **Status** | Brick 0 STABLE. Brick 1 QUEUED. |
| **Audience** | (1) Garrett, for thinking and iteration. (2) A coding agent, as the spec it executes against. |
| **Substrate** | Looker-managed MCP (read-only), Looker VS Code extension, `lkml` parser (vendored + pinned). Cursor now; Gemini Enterprise / Antigravity later. Same engine, same skills, either way. |

---

## 0. How to read this

This is three documents in one, in descending altitude:

- **§1 Thesis** — the argument for why this exists. Strategy. Read once.
- **§2 Intent** — the principles and non-goals that constrain every build decision. The rules of the road.
- **§3–§10 Outline** — the architecture, outputs, roadmap, and acceptance criteria. The part you hand to a coding agent.

Nothing here is code. The point is to be precise enough that the code is the easy part.

---

## 1. Thesis

### The situation, in three lines
A ten-year (2016–2026) Looker monorepo, grown wild-west: dead models, dead explores, PDTs racking up rebuild cost, references into tables that no longer exist — but the bulk of it is good, load-bearing SQL. The team that owns it is small and mostly new. The data warehouse underneath it is being rebuilt (Data Den), and the org is simultaneously in an AI-enablement push *and* a token-cost crisis.

### The real problem
The org's stated want is "use AI more." The org's actual problem is **durable velocity without the token cost spiraling.** Those are not the same thing, and conflating them is why the last attempt — a free compute month and a roadmap — produced a brainstorm and not a deliverable.

### The insight (the whole bet)
**Do the heavy lifting deterministically; use AI as a thin, cheap garnish.**

Parsing ten years of LookML, walking the dependency graph, detecting dead code, and pricing dead PDTs are all *deterministic* problems. They cost **zero tokens**. The LLM never reads the raw repo. It only ever touches a thin synthesis layer — *narrate this explore, summarize this cluster, draft this verdict* — over **pre-digested structure**, which means a cheap or local model does it competently because the context is tiny and clean.

The consequence is the strategic kill shot: **this workflow gets cheaper to run over time, not more expensive.** It is the opposite of a free-month demo that dies when the tokens run out. The free month is the *build budget*; the thing it produces runs on almost nothing. In an org panicking about throughput-vs-cost, that is the exact artifact they are starving for.

### Why now
- **Free compute window** (Cursor pilot through July) = the build budget, spent once.
- **Data Den migration** is live. The dependency map this tool produces *is* the Looker-side migration map — the blast-radius analysis for every table the DE team rebuilds. Archaeology and migration-readiness are the same artifact.
- **Sanctioned open-source pathway** is "coming soon" (per Adhyan). Strata is the thing that walks through that door on day one.

### The win condition
Not IP extraction. **Adoption.** A tool valuable enough that the org keeps it is a tool that made its author the person who built the thing the org adopted. That is the prize. Ownership questions are settled openly through the sanctioned pathway, not hedged against.

---

## 2. Intent — principles & non-goals

### Principles (these constrain every decision below)

1. **Read-only, always.** Strata never writes to prod, never writes to the LookML repo, never writes to the live instance. It operates on a read-only clone of the repo + read-only API/MCP against the instance. Isolation comes from the tool being read-only and living in its own repo — not from forking the monorepo.
2. **Deterministic core, cheap-AI garnish.** Layers 0–1 (parse, graph, usage, cost) are pure Python, no tokens. Layer 2 (synthesis) is the only place an LLM runs, over compact structured slices, on the cheapest model that does the job.
3. **Platform-agnostic by construction.** Built on Looker's MCP + skill-file convention so the same skills + same engine run under Cursor today and Gemini/Antigravity later. The model is the cheap, swappable part; the engine, skills, and governance are the value.
4. **Governed.** Conductor wraps everything: slice-based execution, a `validate.py` gate (no verdict ships without its evidence trail), Exact Next Steps, audit trails. This is what lets a mostly-non-engineer team trust an AI verdict on a production repo.
5. **Generic engine / private config separation.** The public Apache engine parses *any* LookML against the public grammar — **zero org fingerprints** (no internal schema, table names, proprietary SQL, or instance config). Anything organization-specific (the real config, the actual map, the cost numbers) lives in a separate private/internal layer that *consumes* the public engine. Good hygiene regardless of how ownership settles.
6. **Correctness-at-depth, not scale.** This is an ~80-explore instance, dense with `extends` and refinements. The problem is not object count; it is resolving the full extension/refinement chain before any "dead" verdict is trustworthy (see §5). At small scale a wrong verdict that nukes a live explore is a named incident, not a rounding error — so governance matters *more* here, not less.
7. **Mine, don't marry.** Read prior art's source for how it solved annoying parts (SDK export, deps walking); write our own. No runtime dependency on immature tooling.

### Non-goals (explicitly out of scope for v1)

- **Not a refactor or cleanup *executor*.** Strata produces the map and the roadmap; humans (or a later, separately-governed tool) do the changes.
- **Not a LookML *writer*.** Authoring is what Google's MCP + skill-files already do. Strata is the analysis layer they leave empty.
- **Not an at-scale performance tool.** No need for the "66x faster on a huge instance" engineering. Take correctness, leave the scale machinery.
- **Not the Data Den migration executor.** It de-risks the migration by mapping it; it does not perform it.

---

## 3. Architecture

Data flow, one line:

```
read-only repo clone ──▶ [L0 IR] ──▶ [L1 enrich w/ usage+cost] ──▶ [L2 synthesis] ──▶ outputs
live instance (RO MCP) ─────────────────▲                                              │
                                   [L3 Conductor governance wraps L2]                  │
                                   [CI gate reuses L0 + validate] ◀────────────────────┘
                                   [MCP repo-brain exposes L0–L1 to the IDE]
```

### Layer 0 — Deterministic IR  *(no LLM, zero tokens, the foundation)*
Parse the whole repo with `lkml` into one canonical, cached intermediate representation. Everything downstream reasons over **this**, never raw files.

**Nodes:** `connection`, `physical_table` (from `sql_table_name`), `pdt` (derived_table + datagroup/`sql_trigger_value`), `view`, `explore`, `model`, `lookml_dashboard`, `field` (dimension/measure).
**Edges:** `model→connection`, `model→include`, `explore→base_view`, `explore→joined_view`, `view→physical_table`, `view→pdt`, `pdt→upstream`, `explore/view→extends`, `*→refinement`, `dashboard→explore`, `field→underlying_sql`.

**Hard requirement:** `extends` and refinement resolution from the first commit (§5).
**Output:** a serialized graph (JSON) + a queryable in-memory graph (NetworkX). Structural orphans fall out immediately.

### Layer 1 — Usage & cost enrichment  *(deterministic, read-only API/MCP)*
Join the IR against Looker **System Activity** (`i__looker`): explore query counts + last-queried, content→explore references, and **PDT build events**. This turns "looks unreferenced" into "demonstrably unqueried in N months" and "this PDT rebuilds on schedule and serves zero queries → \$X/yr." The **PDT cost ledger** lives here. (This is the slice prior art does *not* cover — own it.)

### Layer 2 — Agentic synthesis  *(the only LLM layer; cheap/local model)*
Reason over IR+usage **slices** — *one explore = one slice = one bounded, validatable unit.* Per slice: what it does, working/broken, dependencies, dependents, and a **verdict** (`keep` / `hide` / `deprecate` / `kill`) **with evidence attached**. Implemented as runtime-injected skills using Looker's skill-file convention: `dep-graph`, `dead-code`, `pdt-cost`, `explore-summarize`. Slices make it parallelizable across the team and token-bounded.

### Layer 3 — Conductor governance  *(prod-hardened)*
Read-only enforcement, the `validate.py` gate (a verdict without its evidence trail does not ship), slice orchestration, Exact Next Steps, audit log. The trust layer.

### CI gate  *(the permanence move — breaks the cycle of slop)*
The L0 IR + validate gate drop into the PR pipeline as the **third gate** alongside Codex review + Looker native validation. Flags at PR time: new orphan view, unreferenced PDT, `sql_table_name` pointing at nothing, broken `extends` chain. The archaeology tool becomes the hygiene tool — and that is what justifies it as infra, not as "AI we spent in June."

### MCP repo-brain  *(the velocity surface the team feels day one)*
Expose L0–L1 as read-only MCP tools in the IDE: *what feeds this explore? is this PDT used? what breaks if I touch this view?* Answered in seconds instead of an afternoon of spelunking.

---

## 4. Outputs (what Strata produces)

- **Dependency graph** — queryable + visual (Plotly).
- **Repo catalog** — per explore/model/view: status (live/orphaned), deps, dependents, last-queried.
- **Dead-code register** — verdicts with evidence + confidence, from the **intersection** of static (structurally unreferenced) and usage (unqueried). Static-only over-reports; usage-only misses orphans; the join is the defensible answer.
- **PDT cost ledger** — rebuild frequency × bytes vs. query count → \$/yr. The dollars headline.
- **Cleanup roadmap** — prioritized, human-actionable.
- **Migration-impact view** — per Data Den table change → Looker-side blast radius.

---

## 5. The hard problem (call it out, because it's make-or-break)

LookML dependency analysis dies on `extends` and refinements. An explore looks unused until you find it `extends` a base three files away; a field looks dead until a refinement in another model resurrects it. **Every downstream verdict is only as trustworthy as the extension/refinement resolution underneath it.** This is the single most valuable code in the project and the thing a young parser is most likely to get subtly wrong on a ten-year repo.

**Therefore:** the IR must resolve the full extends/refinement chain *before* emitting any structural-orphan signal, and the first stress test of any parser (ours or borrowed code) is pointing it at the gnarliest extended explore on the test instance and checking the chain resolves — not just direct references.

---

## 6. Roadmap (bricks — each with a definition of done)

Build **private, on the test instance**, prove the loop end-to-end, *then* point read-only at prod, *then* pitch through the sanctioned pathway, *then* open-source. Public-readiness is a phase, not a prerequisite.

- **Brick 0 — This document.** ✅ *Done when:* thesis/intent/outline agreed.
- **Brick 1 — Generic IR extractor (L0).** `lkml`-based parser + dependency graph, **extension/refinement resolution from the jump**, built against the public grammar + synthetic LookML so no prod leaves the environment. Apache, GS Analytics namespace, generic-by-design. *Done when:* it parses synthetic LookML into the full node/edge IR, resolves an `extends` chain correctly, and emits a structural-orphan list — then runs clean against the test instance clone.
- **Brick 2 — Usage & cost enrichment (L1).** Join IR against System Activity via read-only MCP/API on the test instance; build the PDT cost ledger. *Done when:* a dead-code register exists with static∩usage evidence, and the PDT ledger prices at least one unused PDT in \$/yr.
- **Brick 3 — Synthesis skills + Conductor (L2/L3).** Slice execution, verdicts-with-evidence, the validate gate. *Done when:* one explore slice produces a verdict + evidence trail that passes the gate, on a cheap model.
- **Brick 4 — CI suite.** Wire the validate gate into a PR check on the test instance. *Done when:* a deliberately-broken test PR (orphan view / dead PDT / broken extends) is flagged.
- **Brick 5 — MCP repo-brain + output artifacts.** Catalog, ledger, roadmap, graph viz; L0–L1 exposed as IDE MCP tools. *Done when:* the team can ask "what breaks if I touch X" in the IDE and get an answer.
- **Then:** full loop on playground → read-only against prod → pitch via Adhyan's pathway → open-source.

---

## 7. Prior art & dependencies (what we take from each)

- **`lkml`** (Josh Temple) — parser prior art. **Mine, don't depend.** Read its source for grammar and parsing patterns; write Strata's own deterministic parser for the IR surface. No pip install, no vendored copy, no GitHub fork dependency.
- **Looker-managed MCP server** — free, read-only instance/data access. *Dependency to clear:* registering the agent as an OAuth client needs the Admin role — Garrett has it, so self-serve.
- **Looker VS Code extension** — validation + sync + the skill-file convention we build inside. Works across Cursor / Claude Code / Gemini.
- **Henry** (2018, community) — reference only. Validated the "unused explore/join/field" concept and the warning that a field unused in one explore may be live in another via extensions.
- **`lookerctl`** (z3z1ma, Apache 2.0, v0.1.0) — **mine, don't depend.** Read its source for SDK-export and deps-walking patterns. Does *not* appear to do PDT cost analysis — that gap is ours to own. Too immature (4 commits) to take as a runtime dependency or to import into enterprise infra.

---

## 8. Risks & guardrails

- **Extension/refinement correctness** (§5) — the make-or-break. Mitigation: resolve the chain before any verdict; stress-test on the worst real explore first.
- **Read-only enforcement** — non-negotiable; enforced in Conductor, not by convention.
- **Young-parser risk on legacy syntax** — mitigated by vendor-and-pin + synthetic-first testing.
- **IP / employment** — at peace with company ownership; *still* get explicit written approval through the sanctioned pathway, and read the actual agreement when it lands (Wisconsin has no protective statute, so the document governs — worth an attorney's fifteen minutes). Generic-engine separation keeps the story clean meanwhile.
- **Over-polishing for an imaginary OSS audience** before it works — build private, prove on the playground, dress it up only when the pathway is live.
- **Political** — stay inside sanctioned conventions (Looker skill-files, the approval pathway). The *map* is the asset to show loudly; the *tooling* rides the approved path, not the back door.

---

## 9. Open decisions (resolve as we go)

1. **Name** — Strata, or one of the alternatives.
2. **IDE-first vs. batch-first emphasis** — team is moving into the IDE, so the MCP repo-brain is a real unlock; but the batch artifacts (roadmap, ledger, dead-code register) are what leadership reads. Likely both, repo-brain prioritized. Confirm.
3. **Pilot scope** — which explores/models to run Brick 1–2 against first on the test instance (suggest: the most-extended explore, to exercise §5 immediately).
4. **OAuth client registration** — register the read-only agent against the test instance (Garrett, admin).

---

## 10. Immediate next step

**Brick 1: the generic IR extractor.** Built against the public LookML grammar + synthetic samples so nothing prod ever leaves the environment, extension/refinement resolution baked in from the start, Apache-licensed under the GS Analytics namespace. It is the deterministic foundation every other layer stands on — and being generic-by-design is also what keeps the IP line clean.
