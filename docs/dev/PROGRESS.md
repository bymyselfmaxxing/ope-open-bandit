# Project state: ope-open-bandit

Internal development log for the OPE study. See `docs/dev/AGENT_SPEC.md` for the
full spec and this file for phase status.

## Phase 0: Research and estimand

status: blocked
built:
  - repo skeleton directories (configs/, docs/, src/ope/, experiments/, tests/fixtures/, results/, data/, mlruns/)
  - sample data download (men_random_10k.csv, men_bts_10k.csv) from st-tech/zr-obp @ master
  - data inspection and sanity numbers

make check: not yet run (Phase 1 not started; no code yet)

sanity numbers:
  - RANDOM: rows=10000, clicks=46, click_rate=0.0046, propensity constant at 1/34 = 0.0294118
  - BTS: rows=10000, clicks=69, click_rate=0.0069, propensity in [0.000165, 0.72529]
  - mean importance weight (1/34)/bts_propensity: RANDOM=1.0000 (constant), BTS=0.9433 (max=178.25, min=0.0406)
  - ESS (BTS): sum(w)^2 / sum(w^2) = 655.71
  - unique (ts,user) / rows: RANDOM=9989/10000, BTS=9998/10000 (ratio ~1.0)

gate:
  [ ] ESTIMAND.md and DATA_NOTES.md exist and are specific
  [ ] every item in section 3 of the spec is marked confirmed or corrected
  [ ] sanity numbers recorded, open questions listed
  [ ] the grouping question is answered, or its limitation is written down and approved
  - [ ] **human approved the estimand and the resampling unit — NOT YET (gate open)**

open questions:
  - impression grouping on full data (whether rows share an impression beyond
    (timestamp, user features); full-data check pending)
  - full-data details (sizes, release version/date, license, schema match vs sample)
  - paper and related-work checks (abstracts/read status pending)
  - tolerance for the full-data version of the mean-importance-weight check (Phase 0 proposal)

recent update: 2026-10-25 — Phase 0 re-assessed as BLOCKED at the approval gate after
external review. Sample-level sanity checks are recorded as confirmed; remaining gate
items and open research questions are listed above. No phase beyond Phase 0 started.

