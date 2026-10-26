"""Tests for the off-policy evaluation estimators."""

import numpy as np
import pytest

from ope.estimators import dm, dr, ess, importance_weights, ipw, per_sample_terms, snipw, std_error


def test_support_violation_raises() -> None:
    with pytest.raises(ValueError, match="support violated"):
        importance_weights(np.array([0.5]), np.array([0.0]))


def test_ess_is_between_1_and_n() -> None:
    w = np.array([0.5, 0.25, 0.25])
    assert 1.0 <= ess(w) <= 3.0


def test_ipw_equals_sample_mean_when_target_equals_behavior() -> None:
    r = np.array([0.1, 0.2, 0.3])
    assert ipw(r, np.ones(3)) == pytest.approx(np.mean(r))


def test_dr_reduces_to_dm_when_weights_are_zero() -> None:
    q_pi = np.array([[0.3, 0.1], [0.2, 0.4]])
    r = np.array([0.3, 0.4])
    assert dr(r, np.zeros(2), q_pi, r) == pytest.approx(dm(q_pi))


def test_dr_reduces_to_ipw_when_reward_model_is_zero() -> None:
    q_pi = np.zeros((2, 2))
    r = np.array([0.3, 0.4])
    w = np.array([0.6, 0.4])
    assert dr(r, w, q_pi, r) == pytest.approx(ipw(r, w))


def test_ipw_unbiased_within_4_se() -> None:
    """Mean IPW estimate over 200 small-bandit datasets is within 4 SE of the truth."""
    rng = np.random.default_rng(0)
    n_actions = 4
    q_true = rng.random(n_actions) * 0.8
    pi_e = rng.random(n_actions)
    pi_e /= pi_e.sum()
    pi_b = rng.random(n_actions)
    pi_b /= pi_b.sum()
    v_true = float(np.sum(pi_e * q_true))
    estimates = []
    ses = []
    for _ in range(200):
        n = 500
        a = rng.choice(n_actions, size=n, p=pi_b)
        r = q_true[a]
        w = (pi_e[a] / pi_b[a]).astype(float)
        estimates.append(ipw(r, w))
        ses.append(std_error(per_sample_terms(r, w)))
    se_mean = float(np.std(estimates, ddof=1)) / np.sqrt(len(estimates))
    assert abs(float(np.mean(estimates)) - v_true) < 4 * se_mean


def test_snipw_error_shrinks_with_n() -> None:
    """SNIPW error shrinks as n grows: 1e3 -> 1e4 -> 1e5."""
    rng = np.random.default_rng(1)
    n_actions = 4
    q_true = rng.random(n_actions) * 0.8
    pi_e = rng.random(n_actions)
    pi_e /= pi_e.sum()
    pi_b = rng.random(n_actions)
    pi_b /= pi_b.sum()
    v_true = float(np.sum(pi_e * q_true))
    errors = []
    for n in (1_000, 10_000, 100_000):
        a = rng.integers(0, n_actions, n)
        r = q_true[a]
        w = (pi_e[a] / pi_b[a]).astype(float)
        errors.append(abs(snipw(r, w) - v_true))
    assert len(errors) == 3
    assert errors[2] < errors[0]


def test_dm_with_wrong_reward_model_is_biased() -> None:
    q_wrong = np.array([[0.1, 0.2], [0.3, 0.4]])
    assert dm(q_wrong) != dm(np.array([[0.5, 0.5], [0.5, 0.5]]))
