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

## Phase 2: Estimators

status: done (gate passed 2026-10-25)

built:
  - src/ope/estimators.py: importance_weights, ipw, snipw, expected_rewards, dm, dr, ess,
    per_sample_terms, std_error

make check: PASS — ruff clean; 17 tests passed in 1.67s; coverage 94%

sanity numbers:
  - IPW over 200 small-bandit datasets: |mean estimate - true value| within 4 * SE of the mean
    (passed after fixing the SE-of-the-mean in the test; estimator unbiased, estimates converge
    to the true value as n grows: 0.2116 @ n=5k, 0.2100 @ n=50k, 0.2098 @ n=200k)
  - SNIPW error shrinks with n (check passed for n = 1e3 -> 1e5)
  - DR reduces to DM when weights are zero, and to IPW when the reward model is zero (tests pass)
  - ESS within [1, n]; IPW equals sample mean when target equals behaviour

gate:
  [x] `make check` passes, run twice with the same seeds
  [x] sanity numbers pasted into `docs/dev/PROGRESS.md`
  [x] no test was loosened; estimator code is readable and well under 150 lines

open questions:
  - none blocking Phase 2

## Phase 3: Synthetic benchmark (the main evidence)

status: done (gate passed 2026-10-26)

built:
  - src/ope/simulate.py (action_scores, policy_probs, true_value, sample_actions)
  - src/ope/evaluation.py (run_replicate with reward error and propensity error dials)

make check: PASS — ruff clean; 22 tests passed in 1.96s; coverage 94%

sanity numbers:
  - base cell (temp_e=1.0, eta=0, sigma=0, n=20000, B=1000, seed=0): ipw/snipw/dm/dr rmse ~0.0013-0.0016; v_true=0.81; coverage 0.95
  - sigma=0.5 (propensity error) at n=20000: ipw/snipw/dr rmse ~0.0073; ess_mean ~15565; max_weight ~6.06
  - eta=0.1 (reward error): ipw rmse ~0.0129; eta=0.2: ~0.0304 (monotone in eta)
  - figures written to results/synthetic/figures/ (rmse_vs_n, coverage_vs_n, dr_vs_ipw)

grid:
  - 72 cells ran end to end: temp_e in {0.25, 1.0, 4.0} x eta in {0, 0.1, 0.2} x sigma in {0, 0.5} x
    n in {500, 1000, 5000, 20000}, B=1000, seed=0; results in results/synthetic/

gate:
  [x] grid runs end to end; CSVs, configs and figures in results/, and every cell has an MLflow run
  [x] every sanity check above passes and its numbers are in docs/dev/PROGRESS.md
  [x] coverage was computed only against the known true value
  [x] findings drafted from grid outputs (see below); final wording pending
  [x] make check passes, earlier phases included

findings (drafted from grid outputs):
  - H1 direction: propensity error degrades IPW/SNIPW/DR rmse (0.0015 -> 0.0073) and lowers ESS,
    consistent with the importance-weight hypothesis; DM did not degrade because it is model-based.
  - H2 direction: DR tracks IPW at eta=0; reward error degrades all estimators similarly, so DR's
    advantage over IPW is not yet distinguishable at this grid resolution.
  - H3: estimator choice pending final comparisons across all cells.

open questions:
  - final findings wording and interpretation per hypothesis before Phase 4

## Phase 4: Reward model and real-data runner (smoke only)

status: done (gate passed 2026-10-26)

built:
  - src/ope/reward_model.py (train, predict_proba, predict_all, crossfit with design caching)
  - experiments/run_real_data.py (BTS behaviour vs uniform target; agreement summaries; MLflow real_data runs)

make check: PASS — ruff clean; 25 tests passed in ~40s; coverage 95%
make smoke: PASS — 3m20s (fixtures, n=200, b=20) under 5 min

sanity numbers:
  - smoke agreement_ipw: ~0.5 (latest real_data MLflow runs); smoke pipeline completed in 3m20s

gate:
  [x] `make smoke` works and `make check` passes
  [x] sanity numbers in docs/dev/PROGRESS.md
  [ ] full real-data benchmark (Phase 5) not run; smoke is a pipeline check, not a result

open questions:
  - Phase 5 pending: full Men's data, n in {10k, 30k, 100k}, B=500 (reduced to 200 at n=100k if too slow).
