# Data Notes — Open Bandit Dataset (Men's campaign)

Dataset facts for the OPE study. Every claim below was verified in Phase 0 on the
10k-row sample before anything was written down; corrections from later phases must
update this file, not the memory of the session.

## Sample provenance

- Sample source (no auth needed):
  - Random policy: `https://raw.githubusercontent.com/st-tech/zr-obp/master/obd/random/men/men.csv`
  - BTS policy: `https://raw.githubusercontent.com/st-tech/zr-obp/master/obd/bts/men/men.csv`
- `item_context.csv` is not used (no item features). Not downloaded unless Phase 0
  decides to use item features.

## Verified facts — sample (10k rows per policy)

- RANDOM: 10,000 rows. 34 items. Positions roughly one third each (1: 3284, 2: 3388, 3: 3328).
- BTS: 10,000 rows. 34 items. Positions roughly one third each (1: 3339, 2: 3262, 3: 3399).
- Both: timestamps cover 2019-11-24 to 2019-11-30.
- Both: `item_id` in range, `position` in {1,2,3}, `click` in {0,1}, propensity in (0,1].

- RANDOM: propensity_score constant at 1/34 = 0.0294118 (uniform target over 34 items).
- BTS: propensity_score in approximately [0.000165, 0.72529]; mean 0.1636.
- Clicks: RANDOM ≈ 46 (rate 0.0046); BTS ≈ 69 (rate 0.0069). Click counts are tiny;
  the sample is only good for smoke tests and CI, not for results.

## Verified facts — grouping / weights (sample)

- Unique (timestamp, user features) keys ≈ row count (RANDOM 9989/10000, BTS 9998/10000),
  so impression grouping by that key is approximately recoverable on the sample.
- Mean importance weight `(1/34) / propensity` against BTS: RANDOM = 1.0 (constant);
  BTS = 0.9433, max = 178.25, min = 0.0406. Sum(w) = 9433.14, sum(w^2) = 135706.46,
  ESS = 655.71.

## Claims from the paper (to be re-verified)

- Men's campaign: ~453k Random rows and ~4.08M BTS rows (paper). Both policies ran
  concurrently, each impression randomly assigned to one.
- BTS propensities computed by Monte Carlo simulation → approximate; the size of the
  error is unknown (per spec, unquantified propensity-error caveat on real data).

## Full data

- Full data: ZOZO research data page (https://research.zozo.com/data.html) and Hugging Face
  mirror `zozonext/open-bandit` (CC BY 4.0 as listed there). Paper states non-commercial
  research use; attribute in README.
- Full-data facts (sizes, release version/date, schema match) to be checked in Phase 0 before
  download.

## Open items

- Whether rows share an impression beyond the (timestamp, user features) key; needs the
  full data or paper documentation. Recorded in ESTIMAND.md resampling-unit decision.
