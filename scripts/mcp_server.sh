#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export STRATA_REPO_PATH="${STRATA_REPO_PATH:-tests/lookml/enterprise_mono}"
export STRATA_USAGE_FIXTURE="${STRATA_USAGE_FIXTURE:-tests/fixtures/enterprise_usage_facts.json}"
export STRATA_SCHEMA_FIXTURE="${STRATA_SCHEMA_FIXTURE:-tests/fixtures/enterprise_schema_facts.json}"
exec .venv/bin/python -m strata.mcp.server
