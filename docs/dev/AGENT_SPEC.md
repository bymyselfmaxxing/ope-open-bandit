# AGENT_SPEC.md

Reliability of off-policy evaluation (OPE) estimators, on synthetic bandits and the Open Bandit Dataset. Small, rigorous, built in gated phases.

Keep this file at `docs/dev/AGENT_SPEC.md`. It is an internal development document. Read all of it before writing anything.

---

## 1. What this project is

A portfolio project for an applied scientist / ML engineer. Reviewers will read the code and the method. Every claim in the repo has to be checkable. The goal is a small study that is correct and finished, not a platform.

**The question.** When can you trust an offline estimate of a recommendation policy's value, and how do estimator choice, overlap between policies, and reward-model error change that?

**What gets built.**
1. Four estimators from scratch: IPW, SNIPW, DM, DR.
2. A synthetic benchmark with a known true value: bias, variance, RMSE and real confidence-interval coverage under controlled conditions. This is the main evidence.
3. A real-data benchmark on the Open Bandit Dataset (Men's campaign), compared with an on-policy reference, with ESS and weight diagnostics.
4. Tests, a short README, one-command reproduction, basic CI, and local MLflow tracking of every experiment run.

**What it is not.** Not a new estimator, not paper-level novelty. The honest framing is a reproducible replication and failure analysis. The README says which parts replicate the Open Bandit paper and which are new experiments.

**Balance.** Keep the science simple: four estimators, one synthetic benchmark, one real dataset, no extra methods. Engineering is first-class and should be visible in the repo: tests, CI, config-driven runs, MLflow tracking, verified data download, pinned environment, one Dockerfile, one-command reproduction. Engineering stays small and must never change results.

**Hypotheses.** Starting points the experiments can contradict. Report what the data shows, including negative results.
- H1. When a few observations carry most of the importance weight, IPW error grows and interval coverage drops. ESS is a useful warning signal, with cases where it is not.
- H2. DR is more robust to a bad reward model or bad propensities than IPW or DM, but that does not make its finite-sample intervals reliable.
- H3. The best estimator depends on the regime (sample size, overlap, reward-model quality). No single winner.

**Related work (read, do not copy):**
- Open Bandit Dataset and Pipeline: https://arxiv.org/abs/2008.07146
- Doubly Robust Policy Evaluation and Learning (Dudik et al., 2011; the bias and variance theorems used in Phase 3): https://arxiv.org/abs/1103.4601
- Doubly Robust Policy Evaluation and Optimization (Dudik et al., 2014; stochastic target policies, the form implemented here): https://arxiv.org/abs/1503.02834
- Interpretable Evaluation for OPE (IEOE): https://arxiv.org/abs/2108.13703
- Policy-Adaptive Estimator Selection (PAS-IF): https://arxiv.org/abs/2211.13904
- Open Bandit Pipeline repo (data sample, reference code): https://github.com/st-tech/zr-obp
- pyIEOE (cross-check only, not a dependency): https://github.com/sony/pyIEOE

Budget is zero. Free tools only. Assume a laptop with 16 GB RAM and no GPU.

---

## 2. Rules that apply to every phase

1. **Phases are gated by sanity checks.** Before starting phase N+1, run `make check` (lint plus every test written so far, including the sanity tests) and tick the phase's checklist in `docs/dev/PROGRESS.md`, pasting the test summary and the key sanity numbers. If any check fails, find the cause and fix it. Never loosen a test, tolerance or threshold to make it pass. If it cannot be fixed in a reasonable attempt, stop and report in `PROGRESS.md`.
2. **Sanity checks are real tests.** They live in `tests/` and run in `make check`. Checks that need the full data are marked `fulldata`, skip when the data is missing, and are run locally with their output pasted into `PROGRESS.md`.
3. **Earlier phases keep passing.** A later change that breaks an earlier test is a bug in the later change.
4. **No invented numbers.** Experimental results come only from logged runs, through `make_report.py`. Never type a result by hand and never estimate "likely" values. Dataset facts (sizes, schema, counts) are verified and recorded in `docs/DATA_NOTES.md`. Settings trace to each run's saved config. If something was not run, say so.
5. **Do not change the estimand without approval.** Phase 0 fixes it. If the data disagrees with it, stop and write the question in `PROGRESS.md`.
6. **When unsure, ask.** Write the question in `PROGRESS.md` and stop. Do not guess on anything that changes results.
7. **No scope creep.** The do-not list in section 9 is binding. Extensions (section 8) need explicit human approval.
8. **Small commits.** One logical change each, plain messages ("add snipw and tests"). When a phase's gate passes, tag it `phase-N-done`.
9. **Reproducible.** Fixed seeds, pinned dependencies, no hidden global state.
10. **Time-box dead ends.** An install or integration problem that takes more than 15 minutes gets dropped and logged. This applies to the OBP library in particular.
11. **Two different words.** "Coverage" means the fraction of confidence intervals that contain a *known* true value, so it is only used for synthetic experiments. On real data the comparison is against a noisy reference, so it is called "agreement" (section 7). Never mix them.

### Where the agent must stop for the human
End of Phase 0 (estimand approval), end of Phase 5 (real-data results), end of Phase 6 (final review). Other phases continue once their gate passes.

### docs/dev/PROGRESS.md
Create it in Phase 0 and update it at the end of every phase:

```
## Phase N: <name>
status: done | blocked
built: <short list>
make check: <pass/fail, test count>
sanity numbers: <the key values the checks printed>
gate: [x] item  [ ] item
open questions: <or "none">
```

---

## 3. Facts about the data

Observed on the 10k-row sample (Men's campaign). Re-verify all of it in Phase 0. Do not trust this list blindly.

**Sample source (no auth needed):**
- `https://raw.githubusercontent.com/st-tech/zr-obp/master/obd/random/men/men.csv`
- `https://raw.githubusercontent.com/st-tech/zr-obp/master/obd/bts/men/men.csv`

`item_context.csv` is not used (no item features) and is not downloaded unless Phase 0 decides to use item features.

**Full data (verify size and license before downloading):** ZOZO's research data page, `https://research.zozo.com/data.html` (the OBP README points there), and the Hugging Face mirror `zozonext/open-bandit` (CC BY 4.0 as listed there). The paper states non-commercial research use; attribute it in the README.

**Schema (sample):** unnamed index column, `timestamp`, `item_id`, `position` (1 to 3), `click` (0/1), `propensity_score`, `user_feature_0..3` (hashed categorical strings), `user-item_affinity_0..33`.

**Observed on the sample:**
- 10,000 rows per policy file. 34 items. Positions roughly one third each.
- Random policy: `propensity_score` is constant at 1/34 (0.0294118).
- BTS policy: `propensity_score` ranges from about 0.000165 to 0.725. Under a uniform target, importance weights against the BTS log reached about 178 in the sample.
- Timestamps cover 2019-11-24 to 2019-11-30.
- Unique (timestamp, user features) keys are about equal to the row count in the sample. That says little about the full data: a small random subsample would rarely contain two rows of the same impression. Whether rows share an impression has to be settled from the paper, the data documentation and the full data.
- Click counts are tiny: about 46 clicks in the Random sample and about 69 in the BTS sample. **The sample is only good for smoke tests and CI. Do not read results from it.**

**From the paper (re-verify):** Men's campaign has about 453k Random rows and about 4.08M BTS rows. Both policies ran concurrently, each impression randomly assigned to one of them. BTS propensities were computed by Monte Carlo simulation, so they are approximate.

---

## 4. Working estimand (confirm in Phase 0)

Defaults. Phase 0 confirms or corrects them in `docs/ESTIMAND.md`.

- **Unit of decision:** one row, meaning one item shown at one position.
- **Action space:** 34 items. Position is context. Target policies are written `pi(a | x, pos)`.
- **Policy value:** expected click per row under the target policy.
- **Independence assumption:** treating each row as an independent decision ignores slate effects (a click can depend on the other items shown). Phase 0 checks the collection protocol and records how far this can be trusted. It goes in the limitations either way.
- **Resampling unit:** if the full data has several rows per impression, resample whole impressions, and split cross-fitting folds by impression too. Otherwise standard errors come out too small and folds leak. If impression groups cannot be recovered reliably, Phase 0 documents that limitation and the human approves the resampling and inference method before it is finalised; the README states the limitation either way.
- **Version-one comparison (direction A):** behavior = BTS log, target = uniform random, reference = mean click in the Random log. The weights use the dataset's own logged propensities and an exactly known target.
- **Reference value:** a sample mean with its own normal-approximation 95% CI. It is not the true policy value. Always report the reference CI next to it.
- **Behavior propensities are approximate** (Monte Carlo estimates, per the paper). The size of the error is unknown, so real-data results carry an unquantified propensity-error caveat, and the synthetic propensity dial is a stress test, not a model of it. Say so in the README.

---

## 5. Repo layout and tooling

```
ope-open-bandit/
  README.md               question, headline findings, method summary, limitations, how to run
  Makefile                setup, data, test, lint, check, synthetic, smoke, bench, report, ui, docker, all
  pyproject.toml          pinned versions
  Dockerfile              one CPU image, no compose
  .github/workflows/ci.yml
  configs/
    synthetic.yaml        grid definition for Phase 3
    real_data.yaml        settings for Phases 4 and 5
  docs/
    ESTIMAND.md
    DATA_NOTES.md
    dev/
      AGENT_SPEC.md
      PROGRESS.md
  src/ope/
    data.py               load + schema checks
    estimators.py         ipw, snipw, dm, dr, ess, standard errors
    simulate.py           synthetic bandit with known true value
    reward_model.py       logistic regression, predict_all_items, cross-fit
    evaluation.py         replicate runner, summaries, diagnostics, uniform policy
    tracking.py           thin MLflow wrapper (log_run)
  experiments/
    download_data.py      fetch sample or full data, verify SHA-256
    run_synthetic.py
    run_real_data.py
    make_report.py        results CSVs -> results/summary.md
  tests/
    fixtures/             2,000 rows per policy, attribution note
    test_*.py
  results/                CSVs, configs, PNGs, committed
  data/                   gitignored
  mlruns/                 gitignored, local MLflow file store
```

**Stack:** Python 3.11, numpy, pandas, scipy, scikit-learn, matplotlib, mlflow, pyyaml, pytest, pytest-cov, ruff. Optional: `obp`, used only for a cross-check test and skipped if not installed (`pytest.importorskip`). Nothing else without a reason logged in `PROGRESS.md`.

**Run records:** each experiment run writes its config (parameters, seed, git commit) as JSON next to its results CSV. Those files are the source of truth. `tracking.py` mirrors each run into a local MLflow file store (params, metrics, the CSV and config as artifacts) so runs can be compared in `mlflow ui`. `make_report.py` reads the CSVs, never MLflow, so the repo's results do not depend on it. No tracking server, no cloud, and no Airflow.

**Makefile:** `make check` is `ruff` plus the full `pytest` run. It is the gate command.

---

## 6. Code style

Write it the way a careful senior engineer would. Short, plain, no ceremony.

- Small functions, numpy first. Pandas only for I/O and column handling.
- Type hints on public functions. One-line docstrings at most.
- No class hierarchies. A dataclass is fine for config.
- No global state. Pass a `numpy.random.Generator`, never touch the global seed.
- No `print` in `src/`. Use `logging`.
- Line length 100. `ruff` clean.

**Comments:** explain *why*, or state an assumption or a shape. Never restate the code. No filler, no section banners, no "this function does...", no emojis, no cheerful tone. Plain words, lowercase is fine.

Good:
```python
# w = pi_e / pi_b. unbiased only if pi_b > 0 wherever pi_e > 0
w = pi_e / pi_b

# self-normalised: small bias at low n, but stable when a few weights dominate
def snipw(r, w):
    return np.sum(w * r) / np.sum(w)

# q has shape (n, n_items): prediction for every item, not just the logged one
```

Bad:
```python
# This function calculates the IPW estimate by multiplying the rewards by the weights
# ===== Helper functions =====
# Now we compute the final result!
```

Error messages say what is wrong and what was expected: `"pi_b has zeros where pi_e > 0; support violated"`.

---

## 7. Phases

### Phase 0. Research and estimand (no library code)

**Do:**
1. Read the Open Bandit paper: data collection, dataset description, data format appendix, and its OPE evaluation protocol.
2. Skim IEOE and PAS-IF for what they already cover on this dataset.
3. Download the 10k sample and inspect it. Check everything in section 3.
4. Decide what one row means, what the action is, what `propensity_score` means for each policy, and how the paper defines the reference value.
5. Settle the grouping question: does an impression identifier exist, can the three positions of one impression be grouped reliably (for example by identical timestamp and user features, checked against the paper and the data documentation on the full data, not only the sample), and what does `propensity_score` represent for the chosen unit? If groups cannot be recovered reliably, Phase 0 documents that limitation and the human approves the resampling and inference method before it is finalised; the README states the limitation either way.
6. Find the full Men's data, with file sizes, release version or date, and whether its schema matches the sample.
7. Check whether `pip install obp` works in a clean Python 3.11 environment (the README says Python 3.7 or newer, badges stop at 3.9; a 3.9 environment is the fallback). Time-box to 15 minutes. If it fails, move on.

**Deliver:**
- `docs/ESTIMAND.md`: unit of decision, action space, policy value, behavior and target policy, reference value and its CI, resampling unit, independence assumption, known approximations.
- `docs/DATA_NOTES.md`: verified schema, counts, propensity ranges, anything surprising, plus every claim in section 3 marked confirmed or corrected.
- `docs/dev/PROGRESS.md` with Phase 0 filled in.

**Sanity checks (print the numbers into `PROGRESS.md`):**
- row counts per policy file match section 3 or are corrected
- Random log: propensity constant, equal to 1 / n_items
- BTS log: propensities in (0, 1], min and max recorded
- click rates per policy and per position recorded
- mean of `(1/34) / bts_propensity` on the sample, expected near 1 if the BTS propensities are right and support is full (a noisy check on 10k rows; record it, do not tune anything to it); also propose the tolerance for the full-data version of this check, for example from the sampling error of the mean weight

**Gate:**
- [ ] `ESTIMAND.md` and `DATA_NOTES.md` exist and are specific
- [ ] every item in section 3 is marked confirmed or corrected
- [ ] sanity numbers recorded, open questions listed
- [ ] the grouping question is answered, or its limitation is written down and approved
- [ ] **human approved the estimand and the resampling unit (stop here and wait)**

---

### Phase 1. Skeleton, loader, CI

**Build:** repo layout, `pyproject.toml` with pinned versions, Makefile (`setup`, `test`, `lint`, `check`). `data.py` with `load_log(path)` and schema checks (required columns, click in {0,1}, propensity in (0, 1], position in {1, 2, 3}, item_id in range, no NaN), failing loudly with a specific message. `tests/fixtures/` with 2,000 rows per policy from the sample plus an attribution note. `tracking.py`: `log_run(config, metrics, artifact_paths, experiment)` wrapping `mlflow` with a local store (path from config, default `mlruns/`). Keep it under about 40 lines. `experiments/download_data.py` fetches the sample (and the full data when asked) from a pinned commit SHA of the OBP repo, not `master`, and verifies SHA-256 checksums. The commit SHA, download date, file sizes and checksums, and the full-data release version or date, get recorded in `docs/DATA_NOTES.md`. Experiment settings live in `configs/*.yaml`; the run scripts take `--config`, so a run never needs a code edit. A CI workflow that installs the pinned dependencies and runs `make check` on the fixtures only (the tests make no network calls), with `pytest-cov` printing coverage (no threshold).

**Tests:** loader accepts the fixtures and returns the expected columns and dtypes. Loader rejects a missing column, a click of 2, a propensity of 0, and an unknown position. `log_run` against a temporary store creates one run with the expected params, metrics and artifacts. A config with a missing or misspelled key fails with a clear error. A download whose checksum does not match is rejected.

**Sanity checks:** fixture row counts and click totals are what `DATA_NOTES.md` says they should be.

**Gate:**
- [ ] `make check` passes locally and CI is green
- [ ] the tracking, config and checksum tests pass, and `make ui` opens the run list
- [ ] fresh clone + `make setup && make check` works

---

### Phase 2. Estimators

**Build** in `estimators.py`, vectorised numpy:
- `ipw(r, w)`, `snipw(r, w)`, `dm(q_pi)`, `dr(r, w, q_pi, q_logged)`.
- `ess(w) = sum(w)**2 / sum(w**2)`.
- `per_sample_terms(...)` giving each estimator's per-row terms (SNIPW through its linearisation), and `std_error(terms)` for normal-approximation standard errors.
- `importance_weights(pi_e_logged, pi_b)`: raises `ValueError` if `pi_b <= 0` where `pi_e > 0`.

**Unit tests** (tolerances in standard errors, not magic constants). Use a small throwaway bandit with a known true value; the full simulator comes in Phase 3.
- IPW is unbiased: the mean over about 200 independent datasets is within 4 SE of the truth.
- SNIPW is consistent: error shrinks as n goes 1e3, 1e4, 1e5.
- DM with a wrong reward model is biased (the test documents this).
- DR with a perfect reward model and wrong propensities stays close to the truth.
- DR with a bad reward model and correct propensities stays close to the truth.
- DR reduces to DM when the weights are zero, and to IPW when the reward model is zero.
- Support violation raises `ValueError`.
- Optional cross-check against `obp` estimators if installed.

**Sanity checks (tests that also print their numbers):**
- when target equals behavior, every weight is 1, ESS equals n, and IPW equals the sample mean exactly
- with correct propensities, the mean weight is close to 1 over a large sample
- ESS is between 1 and n for any positive weights
- standard errors shrink roughly as 1 / sqrt(n)

**Gate:**
- [ ] `make check` passes, run twice with the same seeds
- [ ] sanity numbers pasted into `PROGRESS.md`
- [ ] no test was loosened; estimator code is readable and about 150 lines or less

---

### Phase 3. Synthetic benchmark (the main evidence)

Coverage is only meaningful where the true value is known, so this phase carries the project's central claims. Keep the grid small.

**Build:**
- `simulate.py`: a contextual bandit. Context `x ~ N(0, I_d)` with d around 5, around 10 actions, true reward probability `q(x, a)` from a fixed nonlinear function. Behavior and target policies are softmax policies with their own temperatures. The true target value comes from a very large fixed-seed context sample, with its Monte Carlo error reported (it should be negligible next to estimator error).
- Dials:
  1. **Overlap:** target temperature relative to behavior temperature, three levels.
  2. **Reward-model error:** `q_hat = clip(q + eta * g(x, a), 0, 1)` with `g` a fixed pseudo-random function, `eta` in {0, 0.1, 0.2}. `q_hat` is fixed, not fit on the sample.
  3. **Propensity error:** the true logging probabilities generate the data and never change. The estimator receives perturbed estimates `p_hat = clip(p * exp(sigma * eps), 1e-6, 1)` with `eps ~ N(0, 1)` per row and `sigma` in {0, 0.5}. The BTS propensities in the real data are Monte Carlo estimates and the size of their error is unknown, so this perturbation is a controlled stress test of a misspecified denominator, not a calibrated model of the real dataset's propensity error. It is not a new behavior policy, so `p_hat` need not be a valid distribution.
- Sample sizes `n` in {500, 1k, 5k, 20k}, `B = 1000` replicates per cell.
- `evaluation.py` summaries: bias, std, RMSE, **coverage against the known true value**, the Monte Carlo error of the coverage estimate `sqrt(0.95 * 0.05 / B)`, mean ESS, mean max normalised weight, coefficient of variation of the weights.
- Each cell writes a results CSV and a config JSON under `results/synthetic/` and logs one MLflow run (experiment `synthetic`) with the dials as params and bias, RMSE, coverage, ESS as metrics.

**Analysis (tied to the hypotheses):**
- H1: bin replicates by ESS, by max normalised weight and by weight CV; report coverage and RMSE per bin. Find where ESS stops predicting coverage, if it does, and say which diagnostic predicts best.
- H2: DR versus IPW and DM across the `eta` and `sigma` dials. Report where DR does and does not improve variance and RMSE over IPW. This is reported, not asserted in `make check`.
- H3: which estimator has the lowest RMSE in each regime.
- **Theory check** (Dudik et al. 2011, Theorems 1 and 2; applies because `q_hat` and `p_hat` are independent of the sample). Let `Delta = q_hat - q` and `delta = 1 - p / p_hat`. For stochastic policies the signed biases are, with expectations over contexts, actions and the perturbation (estimate them by Monte Carlo on a large fixed-seed sample):
  - DM: `+E_x[ sum_a pi(a|x) * Delta(x,a) ]`
  - IPW: `-E_x[ sum_a pi(a|x) * q(x,a) * delta(x,a) ]`
  - DR: `+E_x[ sum_a pi(a|x) * Delta(x,a) * delta(x,a) ]`
  
  The measured bias should track these. Compare DR and IPW variance and RMSE across the regimes and interpret them with the paper's bias and variance analysis; do not assume a universal condition for variance reduction. Report whether the measured biases agree with the formulas. Disagreement is either a finding or a bug; find out which.

**Figures** (matplotlib, saved to `results/`): RMSE versus n; coverage versus n with Monte Carlo error bars; coverage by ESS bin; DR versus IPW across the dials.

**Tests and sanity checks:**
- The simulator's true value matches a brute-force estimate on a small case, and lies in [0, 1].
- Same seed gives identical output.
- With `eta = 0`, `sigma = 0`: IPW and DR bias are within 3 SE of zero, and the mean weight is near 1.
- With `eta > 0`, `sigma = 0`: DM bias is clearly nonzero while IPW and DR bias stay within 3 SE of zero.
- With `eta = 0`, `sigma > 0`: DR bias reflects the perturbation as expected; document.
- Measured biases match the theory formulas above within Monte Carlo error. Tolerances are set before the run.
- RMSE of IPW falls roughly as 1 / sqrt(n) in a well-overlapped cell (log-log slope near -0.5, tolerance fixed in advance).
- **Coverage acceptance:** IPW coverage in a well-overlapped, large-n cell falls inside a 99% binomial acceptance interval around 0.95 (about 0.932 to 0.968 at B = 1000), fixed before the run. If it falls outside, investigate before continuing: standard error bug first, then genuine finite-sample undercoverage by repeating at larger n. Never change the interval after seeing the result.

**Gate:**
- [ ] grid runs end to end; CSVs, configs and figures are in `results/`, and every cell has an MLflow run
- [ ] every sanity check above passes and its numbers are in `PROGRESS.md`
- [ ] coverage was computed only against the known true value
- [ ] findings written down per hypothesis, including any that were contradicted
- [ ] `make check` passes, earlier phases included

---

### Phase 4. Reward model and real-data runner (smoke only)

**Build:**
- `reward_model.py`: logistic regression. Features: hashed user features as categoricals, item id, position. If affinity is used, the feature row for candidate item `a` must use that item's own affinity column (`user-item_affinity_{a}`), never the shown item's. `predict_all_items(model, df)` returns `(n, n_items)` in batches. `crossfit(df, groups, k=2, seed)` splits by group (the impression if rows share one, else the row) and returns predictions where each row is predicted by a model that trained on neither it nor any other row of its impression.
- `evaluation.py`: `uniform_policy(n_items)` and `run_replicates(behavior, target, reference_log, n, B, seed)`. Each replicate draws `n` units with replacement, cross-fits the reward model (folds split by the same unit), and computes all four estimates, their standard errors, ESS and max weight.
- Real-data summary uses **agreement**: a replicate agrees with the reference if `|est - ref| <= 1.96 * sqrt(se_est**2 + se_ref**2)`. Also bias, std, RMSE and relative RMSE against the reference, and the reference CI.
- `run_real_data.py` with argparse. A saved config JSON per run, and one MLflow run per (n, reward model) setting in experiment `real_data`.

**Tests and sanity checks:**
- Policy probabilities are non-negative and sum to 1 per position.
- Cross-fitting: indices disjoint within each fold; every row gets exactly one out-of-fold prediction; no group on both sides of a split.
- Candidate features: on a hand-built row, the feature vector for candidate `a` uses affinity column `a` and item id `a`, for every `a`.
- Reward model on fixtures: predictions in [0, 1]; mean prediction near the mean click rate; no NaN or inf.
- All weights are finite and positive, and all estimates are finite, on the fixtures. An estimate can legitimately be zero or small on a tiny sample with few clicks.
- Same seed gives identical per-replicate output.
- The summary code is correct on a hand-made tiny table, including the combined-SE agreement rule.
- Smoke run on the fixtures (B around 20, small n) finishes in under 5 minutes. It is a pipeline check, not a result.

**Gate:**
- [ ] `make smoke` works and `make check` passes
- [ ] sanity numbers in `PROGRESS.md`

---

### Phase 5. Full real-data benchmark (direction A)

**Do** (the agent writes the code and exact commands; the human may run the heavy part locally):
- Before the full grid, time one replicate and a 5-replicate run at each `n`, record the measured bottleneck (reward-model refits or `predict_all_items`), and extrapolate. Only then launch the grid.
- Full Men's data, `n` in {10k, 30k, 100k}, logistic-regression reward model.
- `B = 500` for final runs, reduced to 200 at `n = 100k` if too slow. Reduce `B` before `n`. Log every reduction and why.
- Reference value and CI from the full Random log.
- Diagnostics: bin replicates by ESS and max weight; report agreement and RMSE per bin and compare with the synthetic findings from Phase 3.

**Sanity checks (`fulldata`, run locally, numbers pasted into `PROGRESS.md`):**
- full row counts match `DATA_NOTES.md`
- report the observed mean importance weight on the full logs and compare it with the tolerance fixed in Phase 0; a deviation triggers an investigation (propensities, target definition, support, heavy tails) and is not an automatic verdict that something is wrong
- reference click rate is in the range `DATA_NOTES.md` expects from the paper
- compare SNIPW and IPW at the largest n; they should be close when the mean weight is near 1, and a gap says something about weight concentration or propensity error rather than being a failure by itself
- no NaN or inf, ESS > 0 in every replicate, determinism with the same seed
- at the largest n, estimates are on the same order as the reference; at small n with few clicks an estimate can legitimately be zero

**Figures:** RMSE versus n per estimator; agreement versus n; agreement by ESS bin; absolute error versus max weight.

**Report:** `make_report.py` reads the results CSVs and writes `results/summary.md` (generated tables only).

**Gate:**
- [ ] results, configs and figures in `results/`; `summary.md` generated by script
- [ ] every sanity check passed and recorded; reduced settings listed
- [ ] **stop: human reviews the numbers before Phase 6**

---

### Phase 6. README, reproducibility, cleanup

**Build:** `README.md`, short enough to read in a few minutes: what this is (two sentences), the question, headline findings (from `results/summary.md`), method summary (estimand, coverage versus agreement, diagnostics), limitations, what is replicated versus new, how to run (including `make ui` to browse the MLflow runs), references, data attribution and license. Optionally commit one screenshot of the MLflow run comparison view, taken from real runs, in `docs/img/`.

Limitations must include: the reference is a noisy sample mean, not the true value; BTS propensities are approximate; one campaign; two logged policies only; the independence and slate assumption; real-data results show agreement, not coverage.

One `Dockerfile` (a slim Python 3.11 base, pinned dependencies, `make check` as the default command), no compose.

**Checks:**
- if Docker is available, `docker build` and `docker run <image>` work; if it could not be run, say so in the README instead of claiming it
- fresh clone, then `make setup && make check && make smoke` works
- `make smoke` twice gives identical results-CSV hashes (compare the CSVs, not MLflow stores, whose run IDs and timestamps differ)
- every number in the README and docs traces to `results/` (findings), `docs/DATA_NOTES.md` (dataset facts), or a run config (settings); anything else is removed

**Gate:**
- [ ] all checks above pass, CI is green
- [ ] **stop: human final review**

---

## 8. Extensions (not part of version one)

Do these only after the Phase 6 review, and only one at a time with explicit approval. None is required.

- **E1. Direction B and a second reward model:** Random log as behavior, BTS as target (try OBP's `BernoulliTS(is_zozotown_prior=True)` with `compute_batch_action_dist` first; the empirical item-frequency table is an approximation and must be labelled as one), plus `HistGradientBoostingClassifier`.
- **E2. Policy loop and ship/no-ship gate.** If built, it needs these, written down before any code:
  - time split by timestamp (70 / 15 / 15), hyperparameters on validation only, test slice touched once; everything data-derived (baseline table, probability floors, thresholds) fit on train or validation only
  - the log gives the propensity of the logged item only, so a support check needs behavior probabilities for unlogged items; take them from OBP's BTS simulation or an empirical table fit on the train slice, label them estimates, restrict the policy to items above a floor and renormalise, and state what the check cannot show
  - ship only if the one-sided 95% lower bound on `V(pi) - V(baseline)` is above 0 and ESS, max-weight and support checks pass thresholds set from the Phase 3 findings
  - an optional check against the Random log (uniform propensities, so IPW there is unbiased for any supported policy); this idea is unvalidated, so drop it if Phase 0 shows it is unsound
- **E3. Thin CLI:** `python -m ope evaluate --log <csv> --target uniform` printing the four estimates, standard errors and ESS. Only after everything else is done.

---

## 9. Do not

- Add Airflow, Docker Compose, Kubernetes, cloud services, paid APIs, a dashboard, or a serving layer. A single Dockerfile is allowed.
- Rewrite the OBP library. Use it only for the optional cross-check.
- Add features, estimators, datasets or campaigns that are not in this spec.
- Claim novelty. Do not describe the estimators as the project's contribution.
- Write resume bullets, marketing language, or numbers that cannot be traced to results, `DATA_NOTES.md`, or a run config.
- Edit tests, tolerances or thresholds to make them pass, or change the estimand to make results look better.
- Commit raw data. Only the small attributed fixtures are committed.

---

## 10. Reporting rules

- **Coverage:** fraction of intervals containing a known true value. Synthetic only.
- **Agreement:** fraction of replicates within `1.96 * sqrt(se_est**2 + se_ref**2)` of the real-data reference. It measures consistency with a noisy empirical reference, not calibration.
- Report bias, std and RMSE with the reference CI. A bare "RMSE = x" without a baseline is not a finding.
- State the replicate count `B` wherever a coverage or agreement number appears.
- When two results are within Monte Carlo noise of each other, say so instead of naming a winner.
- On real data, keep every statement relative to the reference: "agrees with" or "differs from the reference". Never write "accurate", "unbiased" or "covers the true value" for a real-data result.
- Write what the data shows, including results that are boring, negative, or contradict a hypothesis.

---

## 11. Definition of done

- A fresh clone runs `make setup && make check && make smoke`. Network is needed only to install dependencies (`make setup`) and to download data (`make data`); `make check` and `make smoke` run offline on the fixtures.
- Experiments run from `configs/` and every run is recorded in MLflow.
- Every phase's sanity checks passed and their numbers are recorded in `PROGRESS.md`.
- Every finding in the README comes from a logged run in `results/`; dataset facts and settings trace to `DATA_NOTES.md` and run configs.
- `docs/ESTIMAND.md` matches what the code does.
- Limitations are written down, and replicated parts are separated from new ones.
- Someone reviewing only the repo can state the question, the method, the result and the main weakness.
