# Strata — Thesis, Intent & Principles

**Author:** Garrett Schumacher (GS Analytics)
**License (intended):** Apache 2.0
**Status:** Brick 0 complete. Brick 1 in progress.

---

## 1. Thesis

### The situation, in three lines

A ten-year (2016–2026) Looker monorepo, grown wild-west: dead models, dead explores,
PDTs racking up rebuild cost, references into tables that no longer exist — but the bulk
of it is good, load-bearing SQL. The team that owns it is small and mostly new. The data
warehouse underneath it is being rebuilt (Data Den), and the org is simultaneously in an
AI-enablement push and a token-cost crisis.

### The real problem

The org's stated want is "use AI more." The org's actual problem is durable velocity
without the token cost spiraling. Those are not the same thing, and conflating them is
why the last attempt — a free compute month and a roadmap — produced a brainstorm and
not a deliverable.

### The insight (the whole bet)

**Do the heavy lifting deterministically; use AI as a thin, cheap garnish.**

Parsing ten years of LookML, walking the dependency graph, detecting dead code, and
pricing dead PDTs are all deterministic problems. They cost zero tokens. The LLM never
reads the raw repo. It only ever touches a thin synthesis layer — narrate this explore,
summarize this cluster, draft this verdict — over pre-digested structure, which means a
cheap or local model does it competently because the context is tiny and clean.

The consequence is the strategic kill shot: **this workflow gets cheaper to run over
time, not more expensive.** It is the opposite of a free-month demo that dies when the
tokens run out. The free month is the build budget; the thing it produces runs on almost
nothing. In an org panicking about throughput-vs-cost, that is the exact artifact they
are starving for.

### Why now

- **Free compute window** (Cursor pilot through July) = the build budget, spent once.
- **Data Den migration is live.** The dependency map this tool produces is the Looker-side
  migration map — the blast-radius analysis for every table the DE team rebuilds.
  Archaeology and migration-readiness are the same artifact.
- **Sanctioned open-source pathway** is "coming soon" (per Adhyan). Strata is the thing
  that walks through that door on day one.

### The win condition

Not IP extraction. Adoption. A tool valuable enough that the org keeps it is a tool that
made its author the person who built the thing the org adopted. That is the prize.
Ownership questions are settled openly through the sanctioned pathway, not hedged against.

---

## 2. Intent — Principles & Non-Goals

### Principles (these constrain every build decision)

1. **Read-only, always.** Strata never writes to prod, never writes to the LookML repo,
   never writes to the live instance. It operates on a read-only clone of the repo +
   read-only API/MCP against the instance. Isolation comes from the tool being read-only
   and living in its own repo — not from forking the monorepo.

2. **Deterministic core, cheap-AI garnish.** Layers 0–1 (parse, graph, usage, cost) are
   pure Python, no tokens. Layer 2 (synthesis) is the only place an LLM runs, over compact
   structured slices, on the cheapest model that does the job.

3. **Platform-agnostic by construction.** Built on Looker's MCP + skill-file convention so
   the same skills + same engine run under Cursor today and Gemini/Antigravity later. The
   model is the cheap, swappable part; the engine, skills, and governance are the value.

4. **Governed.** Conductor wraps everything: slice-based execution, a `validate.py` gate
   (no verdict ships without its evidence trail), Exact Next Steps, audit trails. This is
   what lets a mostly-non-engineer team trust an AI verdict on a production repo.

5. **Generic engine / private config separation.** The public Apache engine parses any
   LookML against the public grammar — zero org fingerprints (no internal schema, table
   names, proprietary SQL, or instance config). Anything organization-specific lives in a
   separate private/internal layer that consumes the public engine.

6. **Correctness-at-depth, not scale.** This is an ~80-explore instance, dense with extends
   and refinements. The problem is not object count; it is resolving the full
   extension/refinement chain before any "dead" verdict is trustworthy. At small scale a
   wrong verdict that nukes a live explore is a named incident, not a rounding error —
   so governance matters more here, not less.

7. **Mine, don't marry.** Read prior art's source for how it solved annoying parts;
   write our own. No runtime dependency on immature tooling.

### Non-Goals (explicitly out of scope for v1)

- **Not a refactor or cleanup executor.** Strata produces the map and the roadmap;
  humans (or a later, separately-governed tool) do the changes.
- **Not a LookML writer.** Authoring is what Google's MCP + skill-files already do.
  Strata is the analysis layer they leave empty.
- **Not an at-scale performance tool.** No need for the "66x faster on a huge instance"
  engineering. Take correctness, leave the scale machinery.
- **Not the Data Den migration executor.** It de-risks the migration by mapping it;
  it does not perform it.

---

## 3. The Hard Problem

LookML dependency analysis dies on extends and refinements. An explore looks unused until
you find it extends a base three files away; a field looks dead until a refinement in
another model resurrects it. Every downstream verdict is only as trustworthy as the
extension/refinement resolution underneath it.

**Therefore:** the IR must resolve the full extends/refinement chain before emitting any
structural-orphan signal, and the first stress test of any parser is pointing it at the
gnarliest extended explore on the test instance and checking the chain resolves — not
just direct references.

This is the single most valuable code in the project and the thing a young parser is
most likely to get subtly wrong on a ten-year repo.
