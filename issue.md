Title: Plan: tests + Zavod scaffold for DFAT

Summary
Add tests, docs, and a minimal Zavod dataset to demonstrate crawler + Python + CI + docs skills aligned with the OpenSanctions junior data engineer role.

Motivation
- Show end-to-end ingestion quality (crawl → transform → validate).
- Add basic test coverage and CI stability.
- Demonstrate familiarity with FollowTheMoney and Zavod concepts.
- Prepare for a small upstream contribution.

Scope / Tasks
- Tests
  - [ ] tests/test_validate.py
        - [ ] valid JSONL passes and returns total
        - [ ] bad line raises AssertionError
        - [ ] min_rows enforces threshold
  - [ ] tests/test_transform_dfat.py
        - [ ] stub iterator with a DFAT-like row → assert name/notes in simple JSONL
        - [ ] basic FTM entity output (name + notes)
  - [ ] tests/test_crawl_dfat.py
        - [ ] monkeypatch requests.get → fake bytes; assert file written

- Docs
  - [ ] README: quickstart (crawl → transform → validate), DFAT source link, column mapping (Name of Individual or Entity, Committees, Listing Information)
  - [ ] docs/zavod-notes.md: what Zavod is, dataset metadata, mapping to FTM/zavod

- Zavod (minimal scaffold)
  - [ ] Add zavod to env
  - [ ] datasets/au_dfat/dataset.yml with publisher, update schedule, DFAT XLSX URL
  - [ ] datasets/au_dfat/crawler.py using zavod context/helpers (Person/Organization + name + notes)
  - [ ] Run zavod export; compare outputs; note differences in docs/zavod-notes.md

- CI/Quality
  - [ ] Ensure black and pytest pass in CI
  - [ ] No-network tests (use stubs/fixtures)

Acceptance criteria
- [ ] Tests pass locally and in CI.
- [ ] README contains reproducible quickstart commands:
      - uv run python scripts/crawl_dfat.py
      - uv run python -m sanctions_pipeline.cli transform --input data/raw/dfat_consolidated.xlsx --output data/ftm/dfat_entities.jsonl --format jsonl
      - uv run python -m sanctions_pipeline.cli validate --input data/ftm/dfat_entities.jsonl --min-rows 10
- [ ] Minimal Zavod dataset runs and emits FTM entities.
- [ ] docs/zavod-notes.md explains mapping and differences.

References
- Sources: https://www.opensanctions.org/datasets/sources/
- Zavod docs: https://zavod.opensanctions.org/
- Crawlers board: https://github.com/orgs/opensanctions/projects/2
- Parsing issues: https://www.opensanctions.org/issues/

Out of scope
- Advanced deduplication/matching.
- Full-field FTM mapping beyond name/notes.
- Robust retry/backoff.
