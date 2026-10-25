# Data Notes — Open Bandit Dataset (Men's campaign)

## Sources and version

- Small samples: `st-tech/zr-obp/obd/{random,bts}/men/men.csv`, downloaded from `master` on 2026-10-25. The download record did not capture a commit SHA; Phase 1 must pin a repository revision and checksums for future downloads.
- Full archive: `https://research.zozo.com/data_release/open_bandit_dataset.zip` (official ZOZO Research download).
- Archive size: 412,931,917 bytes compressed; ZIP directory reports 11,746,769,342 bytes uncompressed. SHA-256 of the downloaded archive: `e8ec18196582a5937381a1776382ca940689b90a18d2dcd1fb635be6df614d78`.
- The archive contains `VERSION` = `08/18/2020 Open Bandit Dataset 1.0`; the HTTP `Last-Modified` header is 2020-08-20.
- The archive README licenses the data under CC BY 4.0 and requests citation of the OBD paper. The paper does not state a non-commercial-only license; the previous note claiming that has been corrected.

## Schema

The Men's small samples and full files have the same 44 columns: the exported index, `timestamp`, `item_id`, `position`, `click`, `propensity_score`, `user_feature_0..3`, and `user-item_affinity_0..33`. The ZOZO data release page currently says user features `0-4`; the downloaded version 1.0 files and the samples have `0-3`, so the file schema is the checked source for this release. `item_id` ranges over 34 items and `position` is 1, 2, or 3.

## Small samples (10,000 rows per policy)

| Check | Random | BTS |
| --- | ---: | ---: |
| Rows | 10,000 | 10,000 |
| Clicks / rate | 46 / 0.0046 | 69 / 0.0069 |
| Propensity range (mean) | constant `1/34 = 0.0294118` | `[0.000165, 0.72529]` (mean 0.1636) |
| Mean uniform-target weight | 1.0000 | 0.9433 |

Sample click rate by position:

Both samples span 2019-11-24 through 2019-11-30. Exact observed timestamp ranges are Random `2019-11-24 00:03:13.442536+00:00` to `2019-11-30 23:58:59.642633+00:00`, and BTS `2019-11-24 00:01:03.979311+00:00` to `2019-11-30 23:59:21.586530+00:00`.

| Position | Random rows / click rate | BTS rows / click rate |
| --- | ---: | ---: |
| 1 | 3,284 / 0.003045 | 3,339 / 0.008985 |
| 2 | 3,388 / 0.006494 | 3,262 / 0.006438 |
| 3 | 3,328 / 0.004207 | 3,399 / 0.005296 |

For the BTS sample, weights are `(1/34) / propensity_score`: minimum 0.0406, maximum 178.25, sum 9,433.14, sum of squared weights 135,706.46, and ESS 655.71. The Random weights are all one. These 10k samples are smoke-test data, not evidence for estimator performance.

## Full version 1.0: Men's campaign

The official ZIP contains `random/men/men.csv` (151,946,449 bytes uncompressed; 6,446,314 bytes compressed) and `bts/men/men.csv` (1,332,891,122 bytes uncompressed; 57,454,131 bytes compressed). A streaming scan confirmed the paper's counts and the sample/full schema match.

| Check | Random | BTS |
| --- | ---: | ---: |
| Rows | 452,949 | 4,077,727 |
| Clicks / rate | 2,321 / 0.005124 | 27,495 / 0.006743 |
| Position counts (1, 2, 3) | 150,936 / 151,008 / 151,005 | 1,358,878 / 1,359,483 / 1,359,366 |
| Click rates by position (1, 2, 3) | 0.005380 / 0.005245 / 0.004748 | 0.007245 / 0.007038 / 0.005945 |

Random propensities are constant at `1/34`. Full BTS propensities range from `1e-6` to `0.72529`; they are Monte Carlo estimates of the behavior action probabilities, not exact probabilities. A Phase 0 preflight scan (not a benchmark result) found mean uniform-target weight 1.10164, maximum 29,411.76, and row-level ESS 1,513.09. Phase 5 must recompute and investigate this diagnostic under its saved run config; this preliminary value is not an estimator finding or an automatic failure.

## Impression grouping and limits

The paper says three items are shown simultaneously and assumes click reward depends on the item and its position. It also identifies possible interactions among items in a recommendation list as a limitation. The files have no impression/slate ID. An exact key of timestamp plus all four hashed user-feature fields is not a reliable substitute: in the full files it has 439,012 unique keys among 452,949 Random rows and 3,949,468 among 4,077,727 BTS rows; repeated-key groups range from 2–5 rows in Random and up to 48 in BTS, while only 9 Random and 94 BTS keys have exactly one row at each of the three positions. Hashed features are not user IDs, and the file timestamps do not establish a common slate identifier.

The OBD paper and OBP loader treat each file row as one bandit round/action-position observation. For version one, the estimand and bootstrap/cross-fitting unit are therefore one row. This is an explicit row-independence approximation; standard errors can be too small if rows from one displayed list have dependent clicks. Results concern expected click per item-position observation under the paper's item-position reward assumption, not total slate reward or slate-level effects.

## Research notes

### Section 3 claim audit

- **Confirmed:** 10,000 rows per sample; 34 Men's items; near-equal position counts; Random propensity constant at `1/34`; sample BTS propensity range and maximum uniform-target weight; November 24–30, 2019 timestamps; sample click totals; sample schema.
- **Confirmed with limitation:** timestamp plus user-feature keys are near-unique in the small samples, but they are not a reliable impression/slate ID. The full-data scan supports that limitation.
- **Confirmed from the paper and version 1.0 files:** Men's counts are 452,949 Random and 4,077,727 BTS rows; policies were assigned across impressions; BTS action propensities are Monte Carlo estimates; the data has three positions.
- **Corrected:** the data-release webpage's current user-feature range (`0-4`) does not match the checked version 1.0 files, which contain `user_feature_0..3`. The checked files match the small samples.
- **Confirmed:** the 10k samples are too sparse for findings and are used only for smoke tests/CI.

- OBD paper: Random and Bernoulli Thompson Sampling were assigned per impression; the logged action probabilities were computed by Monte Carlo. It reports Men's Random `452,949` observations and `0.51% ± 0.021%` CTR, and Men's BTS `4,077,727` and `0.67% ± 0.008%` CTR. The full scan agrees after rounding. The paper's benchmark uses on-policy value as a noisy reference and bootstrap resampling; this project calls real-data comparisons “agreement,” not “coverage.”
- Dudík et al. (2011, 2014): DR combines reward modeling and importance weighting; its robustness depends on one nuisance component being adequate, under the contextual-bandit identification assumptions. This motivates the synthetic nuisance-error checks, not a universal claim that DR is best.
- IEOE evaluates robustness across estimator settings and target policies, including experiments on OBD. PAS-IF addresses task-adaptive estimator selection by constructing pseudo subpopulations through importance fitting. This project does not implement either procedure; it studies a fixed four-estimator set and reports its own synthetic coverage and real-data agreement.

## References

- OBD paper: https://arxiv.org/abs/2008.07146
- Dudík et al. (2011): https://arxiv.org/abs/1103.4601
- Dudík et al. (2014): https://arxiv.org/abs/1503.02834
- IEOE: https://arxiv.org/abs/2108.13703
- PAS-IF: https://arxiv.org/abs/2211.13904
- Official data release and license: https://research.zozo.com/data.html and the version 1.0 archive README
