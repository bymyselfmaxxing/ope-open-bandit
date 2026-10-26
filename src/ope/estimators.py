"""Off-policy evaluation estimators: IPW, SNIPW, DM and DR."""

import numpy as np


def importance_weights(pi_e: np.ndarray, pi_b: np.ndarray) -> np.ndarray:
    """Ratio of target policy probability to behaviour policy probability.

    Args:
        pi_e: Target policy probabilities.
        pi_b: Behaviour policy probabilities.

    Returns:
        Importance weights pi_e / pi_b.

    Raises:
        ValueError: If pi_b has zeros where pi_e is positive (support violation).
    """
    if np.any((pi_e > 0) & (pi_b <= 0)):
        raise ValueError("pi_b has zeros where pi_e > 0; support violated")
    return pi_e / pi_b


def ipw(r: np.ndarray, w: np.ndarray) -> float:
    """IPW value: sum(w * r) / sum(w).

    Unbiased only if pi_b > 0 wherever pi_e > 0.
    """
    return float(np.sum(w * r) / np.sum(w))


def snipw(r: np.ndarray, w: np.ndarray) -> float:
    """SNIPW self-normalised value: sum(w * r) / sum(w).

    Small bias at low n, but stable when a few weights dominate.
    """
    return float(np.sum(w * r) / np.sum(w))


def expected_rewards(q_pi: np.ndarray) -> np.ndarray:
    """Per-row expected reward under the uniform policy: mean over actions."""
    return np.mean(q_pi, axis=1)


def dm(q_pi: np.ndarray) -> float:
    """DM model-based value: mean over rows of expected reward under the target policy.

    q_pi has shape (n, n_items): predicted reward for every item, not just the logged one.
    """
    return float(np.mean(expected_rewards(q_pi)))


def dr(r: np.ndarray, w: np.ndarray, q_pi: np.ndarray, q_logged: np.ndarray) -> float:
    """DR value: model-based value minus the weighted gap correction.

    With zero weights it reduces to the model-based value; with a zero reward model it
    reduces to the IPW estimate.
    """
    m = expected_rewards(q_pi)
    total_w = float(np.sum(w))
    if total_w > 0:
        correction = float(np.sum(w * (m - q_logged)) / total_w)
        return float(np.mean(m) - correction)
    return float(np.mean(m))


def ess(w: np.ndarray) -> float:
    """Effective sample size: sum(w)^2 / sum(w^2)."""
    return float(np.sum(w) ** 2 / np.sum(w**2))


def per_sample_terms(r: np.ndarray, w: np.ndarray) -> np.ndarray:
    """Per-row score terms for the self-normalised weighted mean.

    Linearisation of the SNIPW ratio estimator through its per-row terms.
    """
    v_hat = float(np.sum(w * r) / np.sum(w))
    return (w * (r - v_hat)) / np.sum(w)


def std_error(terms: np.ndarray) -> float:
    """Normal-approximation standard error from per-row score terms.

    For the self-normalised weighted mean the per-row terms are sum-to-zero, so the SE of
    the estimator is the square root of their sum of squares; it shrinks as 1 / sqrt(n).
    """
    return float(np.sqrt(np.sum(np.square(terms))))
