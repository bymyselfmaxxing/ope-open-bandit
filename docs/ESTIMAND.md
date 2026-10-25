# Estimand — OPE study (Phase 0 approved)

## Decision unit and value

- **Unit:** one row: one item shown at one of the three recommendation positions. This matches the row/round convention in the OBD paper and OBP loader.
- **Context:** the available user features and the displayed position. Position is part of context, not a target-selected action.
- **Action:** one of the campaign's 34 items.
- **Reward:** whether that item-position observation received a click.
- **Policy value:** expected click per item-position row under the target item policy, averaged over the context and position distribution represented by the logged campaign.

The target policy is uniform over 34 items at each position, so its logged-action probability is exactly `1/34`. The version-one behavior log is BTS. Its provided action propensities were computed by Monte Carlo and are approximate. The reference is the mean click in the full Random log, with its own normal-approximation 95% CI. That reference is noisy and is not the true target value.

## Resampling and inference decision

The paper says three items are presented simultaneously and assumes reward depends on item and position. The released row schema has no reliable slate/impression ID. Exact timestamp plus hashed user-feature keys do not recover the three positions consistently and also collide across rows. I approve one-row resampling and row-level cross-fitting for version one, under the explicit assumption that row observations are independent for inference. This decision follows the OBD row-as-round convention and is a pragmatic limitation, not evidence that slate effects are absent.

Consequences: real-data standard errors and agreement may be optimistic if rows from a displayed list have dependent outcomes. No claim will be made about slate-level value or interaction effects. The synthetic benchmark remains the only setting where coverage against a known truth is reported.

## Weight diagnostic rule

Under exact behavior propensities and full target support, the expected uniform-target importance weight is one. For a full-log diagnostic, flag `abs(mean(w) - 1) > 3 * s(w) / sqrt(n)` for investigation, where `s(w)` is the sample standard deviation of row weights. This is a warning, not an automatic pass/fail: BTS propensities are approximate, weights are heavy-tailed, and the independence approximation may fail. The preliminary full-data scan happened before this rule was written, so its observed weight summary is reconnaissance only; Phase 5 must recompute and report the diagnostic from the saved run.

## Reviewer sign-off

On 2026-10-26, Codex approved this estimand and row-level resampling plan as the user's explicitly delegated reviewer for the Phase 0 human gate. This is not represented as the user's personal sign-off. The approval accepts the documented row-independence and slate-effect limitations for this version-one study.

## Reporting vocabulary

- **Coverage** is the fraction of intervals containing a known true value; report it for synthetic experiments only.
- **Agreement** is the fraction of real-data replicate intervals meeting the specified combined-SE rule against the noisy Random reference; it is not calibration or true-value coverage.
