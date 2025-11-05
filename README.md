# Sanctions Data Mini-Pipeline

A focused demo of sanctions data engineering with Python, tests, and CI. Ready to run locally. It downloads a public source, normalizes varied headers into a consistent JSONL structure, validates basic quality, and provides a simple screening utility.

[![CI](https://github.com/rajsandhu/sanctions-pipeline/actions/workflows/ci.yml/badge.svg)](https://github.com/rajsandhu/sanctions-pipeline/actions/workflows/ci.yml)

Note: This is a compact, (reasonably) well-documented demo, not a full product. It’s designed to be cloned, run, and adapted.

## Why

- Reproducible: deterministic steps (extract → transform → validate → screen) that run locally and in CI
- Open-source hygiene: tests, CI, pinned dependencies, and clear data provenance
- Practical: converts a public source into screenable entities for quick checks

## Features

- Extract: download a public sanctions file (CSV/XLSX) to data/raw with a single CLI command
- Transform: normalize varied headers across sources and write simplified JSONL entities (schema, id, name, notes)
- Validate: run basic checks (valid JSON, non‑empty names, minimum rows) to catch silent failures early
- Screen: perform a simple, case‑insensitive substring match of input names against entities; designed to be a baseline

Note: Screening is intentionally simple; fuzzy/entity‑resolution is listed in the roadmap.



## Quickstart

Requirements
- Python 3.12+
- uv (https://docs.astral.sh/uv/)

Setup
```bash
git clone https://github.com/rajsandhu/sanctions-pipeline.git
cd sanctions-pipeline
uv sync
uv pip install -e .
```

Example: Australia DFAT consolidated list (XLSX)

These commands fetch a public sanctions list, convert it to JSONL, validate it, and screen a tiny CSV of names—so you can see the outputs immediately

```bash
# Extract
uv run python -m sanctions_pipeline.cli extract \
  --url https://www.dfat.gov.au/sites/default/files/regulation8_consolidated.xlsx \
  --out data/raw/dfat_consolidated.xlsx

# Transform to JSONL
uv run python -m sanctions_pipeline.cli transform \
  --input data/raw/dfat_consolidated.xlsx \
  --output data/ftm/entities.jsonl

# Validate (ensure at least 10 rows)
uv run python -m sanctions_pipeline.cli validate \
  --input data/ftm/entities.jsonl \
  --min-rows 10

# Screen a list of names (demo)
printf "name\nJane Doe\nAcme Corp\n" > people.csv
uv run python -m sanctions_pipeline.cli screen \
  --input-csv people.csv \
  --entities data/ftm/entities.jsonl \
  --output-csv matches.csv
head matches.csv
```

Makefile (optional shortcuts)

```bash
make setup      # uv sync + editable install
make extract    # DFAT XLSX → data/raw
make transform  # → data/ftm/entities.jsonl
make validate   # basic checks
make screen     # requires people.csv
make lint       # ruff + black --check
make test       # pytest
```
Samples (no download needed)

Use built-in tiny CSVs for a quick demo.

```bash
# Transform the sample sanctions CSV → JSONL
uv run python -m sanctions_pipeline.cli transform \
  --input data/sample/sdn_sample.csv \
  --output data/ftm/entities.jsonl

# Validate
uv run python -m sanctions_pipeline.cli validate \
  --input data/ftm/entities.jsonl \
  --min-rows 1

# Screen sample names against entities
uv run python -m sanctions_pipeline.cli screen \
  --input-csv data/sample/people_sample.csv \
  --entities data/ftm/entities.jsonl \
  --output-csv data/sample/matches_sample.csv

# View results
cat data/sample/matches_sample.csv
```

## Data

- Source: Australia DFAT consolidated list (public): https://www.dfat.gov.au/

  - Example file used here: regulation8_consolidated.xlsx (live URL in Quickstart)

- Provenance: Fetched directly from the public URL; no scraping

- Format (output): simplified JSONL — one entity per line with fields:
  - schema (“Person” or “Organization”)
  - id (row‑based id)
  - name
  - notes (optional; program/remarks if present)
- Normalization:
  - Handles CSV or XLSX
  - Normalizes varied column headers to a consistent shape (e.g., name, type, program/remarks)
- Limitations:
  - Output is simplified JSON (not full FollowTheMoney yet)
  - Screening is substring‑only (case‑insensitive), so it may miss variants and produce false positives
    - Single snapshot; no scheduled updates or versioning

This repo emphasizes transparency and reproducibility over completeness; see Roadmap for next steps (FTM export, fuzzy matching, additional sources).

## Pipeline Overview

1. **Extract**: Download a public sanctions file (CSV/XLSX) to `data/raw/`
2. **Transform**: Normalize headers, write simplified JSONL entities to `data/ftm/entities.jsonl`
3. **Validate**: Check JSON validity, non-empty names, and minimum row count
4. **Screen**: Match input names against entities; write matches to CSV

## Testing & CI
Tests: `uv run pytest -q` (covers extract, transform, validate, screen)
Lint: `uv run ruff check .` + `uv run black --check .`
CI: GitHub Actions on push/PR (Python 3.12 + uv). See CI badge at the top of this doc.

note: don't forget the periods in there

## Roadmap

- Add one more public data source (EU or UN)
- Improve screening a bit (case-insensitive, simple partial match)
- Write a few more tests and small validation checks
- Add a Dockerfile for easier running (optional)
- Learn and use AI coding assistants in VS Code (GitHub Copilot, Claude Code) to refine this repo and future projects

## AI-assisted development

- Current use: I’ve started using GitHub Copilot for drafting code and unblocking issues directly in my editor.
- Plan (in-editor tools):
    - **GitHub Copilot (primary)**: enable inline suggestions and Copilot Chat in VS Code (first month free). Use it for test scaffolding, small refactors, and CI/YAML boilerplate.
- Quality control: All AI-assisted changes are validated by tests (pytest), linting/formatting (Ruff/Black), and CI (GitHub Actions). I keep diffs small and readable.
- Transparency: I document commands in the README and note AI-assisted changes in PRs when applicable.
- Learning goals: get comfortable with Copilot inline suggestions and Copilot Chat; explore its capabilities for enhancing productivity and code quality.


## License

MIT

## Notes

Developed with AI coding assistance (initially with a messy mix of ChatGPT 5, Phind, Claude Sora, Llama, etc, then finally with GitHub Copilot); validated by tests and CI.
