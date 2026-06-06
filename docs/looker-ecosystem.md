# Looker Ecosystem Fit

| Surface | What It Is | Where Strata Fits |
|---|---|---|
| Looker MCP Server | Read-only IDE access to Looker objects and APIs through MCP. | Source for live facts and human inspection; Strata keeps deterministic analysis local and stdio-first. |
| Looker Extension | A Looker-hosted UI/app surface running inside the Looker product. | Useful future presentation layer, not the analysis core. Strata artifacts can feed one later. |
| Strata | Offline-first LookML graph, L1 enrichment, outputs, and conductor governance. | Maps dependencies, dead code, PDT cost, schema drift, and migration blast radius from a clone plus read-only facts. |

Strata is not a replacement for Looker validation or authoring tools. It is the
analysis layer between raw LookML and governed cleanup/migration decisions.

Live Looker access is intentionally narrow: System Activity reads are normalized
into the existing UsageProvider protocol, then the same offline pipeline runs.
