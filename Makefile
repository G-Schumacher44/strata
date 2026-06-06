-include .strata

PYTHON  := .venv/bin/python
PYTEST  := .venv/bin/pytest
REPO    ?= tests/lookml/gcs_analytics
USAGE   ?= tests/fixtures/gcs_usage_facts.json
SCHEMA  ?= tests/fixtures/gcs_schema_facts.json

.PHONY: test validate check check-replay build auth outputs dashboard ci clean

test:
	$(PYTEST)

validate:
	$(PYTHON) scripts/validate.py

check:
	$(PYTHON) scripts/check_strata.py \
		--repo $(REPO) \
		--usage-fixture $(USAGE) \
		--schema-fixture $(SCHEMA)

check-replay:
	$(PYTHON) scripts/check_replay.py

build:
	$(PYTHON) scripts/build_ir.py \
		--repo $(REPO) \
		--usage-fixture $(USAGE) \
		--schema-fixture $(SCHEMA)

auth:
	$(PYTHON) scripts/strata_auth.py status

outputs:
	$(PYTHON) scripts/generate_outputs.py \
		--repo $(REPO) \
		--usage-fixture $(USAGE) \
		--schema-fixture $(SCHEMA) \
		--out output/$(notdir $(REPO))

dashboard:
	$(PYTHON) scripts/serve_dashboard.py \
		--repo $(REPO) \
		--usage-fixture $(USAGE) \
		--schema-fixture $(SCHEMA)

ci: test validate check check-replay outputs

clean:
	rm -rf output/
	find . -name "strata_ir.db" -not -path "./.git/*" -delete
	find . -name "__pycache__" -not -path "./.git/*" -exec rm -rf {} + 2>/dev/null || true
