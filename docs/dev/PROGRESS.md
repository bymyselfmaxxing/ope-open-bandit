# Project state: ope-open-bandit

Internal development log for the OPE study. See `docs/dev/AGENT_SPEC.md` for the
full spec and this file for phase status.

## Phase 0: Research and estimand

status: done
built:
  - repository skeleton directories
  - 10k Random and BTS sample inspection
  - official OBD version 1.0 metadata, full-file schema and row-count verification
  - paper and related-work review; estimand and inference limitation recorded

make check: not applicable (Phase 1 has not started; no Makefile or library code exists)

sanity numbers — sample:
  - RANDOM: rows=10000, clicks=46, click_rate=0.0046, propensity constant at 1/34 = 0.0294118
  - BTS: rows=10000, clicks=69, click_rate=0.0069, propensity in [0.000165, 0.72529]
  - sample click rates by position (1, 2, 3): RANDOM=(0.003045, 0.006494, 0.004207); BTS=(0.008985, 0.006438, 0.005296)
  - mean uniform-target weight: RANDOM=1.0000; BTS=0.9433 (min=0.0406, max=178.25)
  - ESS (BTS): 655.71
  - exact timestamp + hashed user-feature key unique counts: sample RANDOM=9989/10000, BTS=9998/10000; these near-unique sample keys do not establish slate grouping

full-data verification:
  - official version 1.0 (2020-08-18); CC BY 4.0; archive=412931917 compressed bytes
  - Men's rows: RANDOM=452949; BTS=4077727; schema matches the 44-column samples
  - key-based grouping is unreliable; see DATA_NOTES.md and the approved row-level limitation in ESTIMAND.md
  - preliminary full-data weight scan: mean=1.10164, max=29411.76, ESS=1513.09; exploratory only, not an estimator finding

tool compatibility:
  - Python 3.11.17 clean-environment `uv pip install obp` failed after 13.2s while building `PyYAML 5.4.1` (`build_ext` lacks `cython_sources`); resolution also attempted large Torch/CUDA dependencies. Dropped within the 15-minute timebox; OBP remains optional and is not a project dependency.

gate:
  [x] ESTIMAND.md and DATA_NOTES.md exist and are specific
  [x] section 3 data claims are confirmed or corrected in DATA_NOTES.md
  [x] required sample sanity numbers and open questions/limitations are recorded
  [x] grouping limitation is written down and approved for row-level inference
  [x] Phase 0 human gate: reviewer sign-off delegated to Codex by the user, recorded in ESTIMAND.md

open questions: none required to close Phase 0. Phase 5 must recompute the preliminary
full-data weight diagnostic under a saved run config and investigate any deviation.

review decision: Phase 0 approved on 2026-10-26. Approval is by the user's delegated
reviewer, not attributed to the user's personal sign-off. No Phase 1 work is included here.

process note: the full-data mean-weight statistic was calculated during the Phase 0
streaming preflight before the 3-SE diagnostic rule was written. Treat that value as
exploratory; Phase 5 must rerun and report it. The chosen rule is a warning for
investigation, not an automatic pass/fail, because BTS propensities are approximate and
weights are heavy-tailed.
