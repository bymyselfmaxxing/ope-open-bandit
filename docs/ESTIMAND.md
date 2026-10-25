# Estimand — OPE study (draft, Phase 0)

Working definition of the estimand for the Open Bandit OPE study. Phase 0 confirms or
corrects these; anything final waits for human approval at the Phase 0 gate.

## Defaults (to be confirmed in Phase 0)

- **Unit of decision:** one row = one item shown at one position.
- **Action space:** 34 items. Position is context. Target policies written
  `pi(a | x, pos)`.
- **Policy value:** expected click per row under the target policy.

## Decisions and their status

- Independence assumption (slate effects): row-level independence ignores that a click
  can depend on other items shown. Phase 0 checks the collection protocol and records the
  limitation. Goes into README either way.
- Resampling unit: rows here (verified approximately on sample: unique (ts, user) keys ≈ rows).
  Full-data impression grouping must be settled before cross-fitting folds are final.

## Version-one comparison (direction A)

- Behavior = BTS log, target = uniform random, reference = mean click in the Random log.
- Weights use dataset's own logged propensities (BTS: Monte Carlo, approximate) and an
  exactly known target (uniform: 1/34).

## Reference value

- Sample mean with its own normal-approximation 95% CI. Not the true policy value.
- Always report the reference CI next to real-data estimates.

## Known approximations

- BTS propensities are approximate (Monte Carlo).
- Real-data results carry unquantified propensity-error caveat; synthetic propensity dial is
  a stress test, not a calibrated model.

## Reporting vocabulary

- "Coverage" = fraction of intervals containing a known true value (synthetic only).
- "Agreement" = comparison against noisy real-data reference (real data).
- Never mix the two.
