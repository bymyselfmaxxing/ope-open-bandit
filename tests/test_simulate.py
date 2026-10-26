"""Tests for the synthetic bandit simulator."""

import numpy as np

from ope.simulate import policy_probs, sample_actions, true_value


def test_true_value_is_finite_and_se_positive() -> None:
    v, se = true_value(np.random.default_rng(0).normal(0.0, 1.0, size=(500, 5)), 1.0)
    assert 0.0 <= v <= 1.0
    assert se > 0.0


def test_policy_probs_sum_to_one() -> None:
    pi = policy_probs(np.random.default_rng(1).normal(0.0, 1.0, size=(20, 5)), 2.0)
    assert np.allclose(pi.sum(axis=1), np.ones(20))
    assert (pi >= 0).all()


def test_sample_actions_in_range() -> None:
    pi = np.full((7, 10), 0.1)
    a = sample_actions(np.random.default_rng(2), pi)
    assert len(a) == 7
    assert (a >= 0).all()
    assert (a < 10).all()
