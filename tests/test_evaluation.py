"""Tests for the synthetic benchmark replicate runner."""

import numpy as np

from ope.evaluation import run_replicate


def test_run_replicate_returns_finite_estimates() -> None:
    rng = np.random.default_rng(3)
    res = run_replicate(rng, n=200, temperature_b=1.0, temperature_e=1.0)
    for key in ("ipw", "snipw", "dm", "dr", "ess"):
        assert np.isfinite(res[key])


def test_run_replicate_same_policy_gives_unit_weights() -> None:
    rng = np.random.default_rng(4)
    res = run_replicate(rng, n=100, temperature_b=0.7, temperature_e=0.7)
    assert res["ess"] == 100.0
    assert res["ipw"] > 0.0
    assert res["dm"] > 0.0
    assert res["dr"] > 0.0
    assert res["max_weight"] == 1.0
