"""Synthetic benchmark: replicate runner and summaries."""

import numpy as np

from ope.estimators import dm, dr, ess, ipw, per_sample_terms, snipw, std_error
from ope.simulate import action_scores, policy_probs, sample_actions

UNIFORM_N_ITEMS = 34


def uniform_policy(n_items: int) -> np.ndarray:
    """Uniform target policy over n_items actions."""
    return np.full(n_items, 1.0 / n_items)


def run_replicate(
    rng: np.random.Generator,
    n: int,
    temperature_b: float,
    temperature_e: float,
    reward: np.ndarray | None = None,
    propensity_sigma: float = 0.0,
    x: np.ndarray | None = None,
) -> dict:
    """Run all estimators on one synthetic bandit replicate.

    Args:
        rng: Random generator for actions.
        n: Number of units (contexts) in the replicate.
        temperature_b: Behaviour policy inverse temperature.
        temperature_e: Target policy inverse temperature.
        reward: Reward matrix of shape (n, N_ACTIONS); defaults to the true rewards.
        propensity_sigma: Propensity error dial; 0 means no error.
        x: Context matrix of shape (n, 5); generated when None.

    Returns:
        Per-estimator values plus diagnostics.
    """
    if x is None:
        x = rng.normal(0.0, 1.0, size=(n, 5))
    pi_b = policy_probs(x, temperature_b)
    pi_e = policy_probs(x, temperature_e)
    if propensity_sigma > 0:
        eps = rng.normal(0.0, 1.0, size=pi_b.shape)
        pi_b = np.clip(pi_b * np.exp(propensity_sigma * eps), 1e-6, 1.0)
    a = sample_actions(rng, pi_b)
    q = action_scores(x) if reward is None else reward
    r = q[np.arange(n), a]
    w = pi_e[np.arange(n), a] / pi_b[np.arange(n), a]
    q_pi = np.sum(pi_e * q, axis=1)
    m = q_pi
    return {
        "ipw": ipw(r, w),
        "snipw": snipw(r, w),
        "dm": dm(pi_e * q),
        "dr": dr(r, w, pi_e * q, r),
        "ess": ess(w),
        "max_weight": float(np.max(w)),
        "weight_cv": float(np.std(w) / np.mean(w)),
        "se_ipw": std_error(per_sample_terms(r, w)),
        "se_snipw": std_error(per_sample_terms(r, w)),
        "se_dm": float(np.sqrt(np.sum((m - np.mean(m)) ** 2)) / n),
        "se_dr": float(np.sqrt(np.sum((m - np.mean(m)) ** 2)) / n),
    }
