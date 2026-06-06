PYTHON  := .venv/bin/python
PYTEST  := .venv/bin/pytest
REPO    := tests/lookml/gcs_analytics
USAGE   := tests/fixtures/gcs_usage_facts.json
SCHEMA  := tests/fixtures/gcs_schema_facts.json

.PHONY: test validate check check-replay build outputs dashboard clean

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

outputs:
	$(PYTHON) scripts/generate_outputs.py \
		--repo $(REPO) \
		--usage-fixture $(USAGE) \
		--schema-fixture $(SCHEMA) \
		--out output/gcs_analytics

dashboard:
	$(PYTHON) scripts/serve_dashboard.py \
		--repo $(REPO) \
		--usage-fixture $(USAGE) \
		--schema-fixture $(SCHEMA)

clean:
	rm -rf output/
	find . -name "strata_ir.db" -not -path "./.git/*" -delete
	find . -name "__pycache__" -not -path "./.git/*" -exec rm -rf {} + 2>/dev/null || true
