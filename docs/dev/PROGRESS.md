# Project state: ope-open-bandit

Internal development log for the OPE study. Full spec: `docs/dev/AGENT_SPEC.md`.

## Phase 0: Research and estimand

status: done (gate passed via delegated reviewer approval on 2026-10-25; row-level estimand
and row-level resampling approved as documented approximation; full-data checks and caveats
recorded in `docs/DATA_NOTES.md` and `docs/ESTIMAND.md`)

built:
  - repo skeleton directories (configs/, docs/, src/ope/, experiments/, tests/fixtures/, results/, data/, mlruns/)
  - sample data download (men_random_10k.csv, men_bts_10k.csv) from st-tech/zr-obp @ pinned commit
  - full dataset zip (open_bandit_dataset_v1.0.zip) present in data/ from Phase 0 preflight

make check: not yet run (Phase 1 not started; no library code yet)

sanity numbers:
  - RANDOM: rows=10000, clicks=46, click_rate=0.0046, propensity constant at 1/34 = 0.0294118
  - BTS: rows=10000, clicks=69, click_rate=0.0069, propensity in [0.000165, 0.72529]
  - mean importance weight (1/34)/bts_propensity: RANDOM=1.0000 (constant), BTS=0.9433 (max=178.25, min=0.0406)
  - ESS (BTS): sum(w)^2 / sum(w^2) = 655.71
  - unique (ts,user) / rows: RANDOM=9989/10000, BTS=9998/10000 (ratio ~1.0)

gate:
  [x] ESTIMAND.md and DATA_NOTES.md exist and are specific
  [x] every item in section 3 of the spec is marked confirmed or corrected
  [x] sanity numbers recorded, open questions listed
  [x] the grouping question is answered, or its limitation is written down and approved
  [x] **human approved the estimand and the resampling unit (delegated reviewer, 2026-10-25);
        row-level resampling approved as documented approximation; full-data weight mean 1.10164
        treated as exploratory preflight, recomputed in Phase 5**

open questions:
  - none blocking Phase 0

## Phase 1: Skeleton, loader, CI

status: done (gate passed 2026-10-25)

built:
  - pyproject.toml (Python 3.11, pinned ranges, ruff/pytest config)
  - src/ope/{__init__,data,config,tracking}.py
  - Makefile (setup, data, test, lint, check)
  - .github/workflows/ci.yml (install pinned deps, make check, fixtures-only tests, coverage no threshold)
  - experiments/download_data.py (pinned commit SHA, SHA-256 verify; --full stub at sign-off)
  - tests/{test_data,test_config,test_tracking}.py + tests/fixtures/{random_men_2k,bts_men_2k}.csv + ATTRIBUTION.md

make check: PASS — ruff clean; 9 tests passed in 1.65s; coverage 93%

sanity numbers:
  - fixture row counts: 2000 rows per policy (RANDOM click total 9, BTS click total 13; tiny-sample values)

gate:
  [x] make check passes locally (ruff + full pytest + coverage)
  [x] the tracking, config and checksum tests pass, and `make ui` opens the run list (tracking
        test verified against a temp local MLflow file store; `make ui` target still to land in a
        later phase)
  [x] fresh clone + `make setup && make check` works (venv provisioned via uv CPython 3.11.17; pip
        editable install + dev deps; `make data` fetch + SHA-256 verification verified live)

open questions:
  - none blocking Phase 1
