-include .strata

PYTHON  := .venv/bin/python
PYTEST  := .venv/bin/pytest
REPO    ?= tests/lookml/gcs_analytics
USAGE   ?= tests/fixtures/gcs_usage_facts.json
SCHEMA  ?= tests/fixtures/gcs_schema_facts.json
STORE   ?= output/$(notdir $(REPO))/strata_usage.db
DAYS    ?= 30

.PHONY: test validate check check-replay build import outputs dashboard ci clean

test:
	$(PYTEST)

validate:
	$(PYTHON) scripts/validate.py

check:
	$(PYTHON) scripts/check_strata.py

check-replay:
	$(PYTHON) scripts/check_replay.py

build:
	$(PYTHON) scripts/build_ir.py \
		--repo $(REPO) \
		--usage-fixture $(USAGE) \
		--schema-fixture $(SCHEMA)

import:
	$(PYTHON) scripts/import_usage.py \
		--store $(STORE) \
		--fixture $(USAGE)

outputs:
	$(PYTHON) scripts/generate_outputs.py \
		--repo $(REPO) \
		--store $(STORE) \
		--schema-fixture $(SCHEMA) \
		--days $(DAYS) \
		--out output/$(notdir $(REPO))

dashboard:
	$(PYTHON) scripts/serve_dashboard.py \
		--repo $(REPO) \
		--store $(STORE) \
		--schema-fixture $(SCHEMA) \
		--days $(DAYS)

ci: test validate check check-replay import outputs

clean:
	rm -rf output/
	find . -name "strata_ir.db" -not -path "./.git/*" -delete
	find . -name "strata_usage.db" -not -path "./.git/*" -delete
	find . -name "__pycache__" -not -path "./.git/*" -exec rm -rf {} + 2>/dev/null || true
