# Project state: ope-open-bandit

Internal development log for the OPE study. See `docs/dev/AGENT_SPEC.md` for the
full spec and this file for phase status.

## Phase 0: Research and estimand

status: blocked
built:
  - sample data download (men_random_10k.csv, men_bts_10k.csv) from st-tech/zr-obp @ master
  - partial sample inspection and sanity numbers

make check: not applicable (Phase 1 has not started; no code or Makefile exists)

sanity numbers:
  - RANDOM: rows=10000, clicks=46, click_rate=0.0046, propensity constant at 1/34 = 0.0294118
  - BTS: rows=10000, clicks=69, click_rate=0.0069, propensity in [0.000165, 0.72529]
  - mean importance weight (1/34)/bts_propensity: RANDOM=1.0000 (constant), BTS=0.9433 (max=178.25, min=0.0406)
  - ESS (BTS): sum(w)^2 / sum(w^2) = 655.71
  - unique (timestamp, user features) keys vs rows: RANDOM=9989/10000, BTS=9998/10000 (ratio ~1.0)

gate:
  [x] ESTIMAND.md and DATA_NOTES.md exist (estimand remains a draft)
  [ ] every item in section 3 of the spec is marked confirmed or corrected
  [ ] all required sanity numbers recorded, open questions listed
  [ ] the grouping question is answered, or its limitation is written down and approved
  [ ] **human approved the estimand and the resampling unit (stop here and wait)**

open questions:
  - Human approval of the estimand and resampling unit is pending.
  - Impression grouping is not established from the paper/data documentation or full data; near-unique sample keys do not settle it.
  - Required Phase 0 reading/research (Open Bandit paper protocol, IEOE, PAS-IF) is not evidenced in the deliverables.
  - Full-data release/version, sizes, license, and schema match have not been verified.
  - Click rates by position and a proposed full-data mean-weight tolerance are not recorded.
  - Several section 3 claims are still explicitly marked for re-verification in DATA_NOTES.md.

review: blocked at Phase 0 gate; do not start Phase 1 until the research gaps are resolved and the human approves the estimand and resampling unit.
