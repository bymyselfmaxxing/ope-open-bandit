"""Tests for the logistic regression reward model and cross-fitting."""

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

from ope.reward_model import crossfit, predict_all, predict_proba, train

ITEMS = list(range(34))


def test_predictions_in_unit_range_and_finite() -> None:
    df = pd.read_csv("tests/fixtures/bts_men_2k.csv")
    model = train(df, ITEMS, 34)
    pred = predict_all(model, df, ITEMS, 34)
    assert pred.shape == (2000, 34)
    assert (pred >= 0).all()
    assert (pred <= 1).all()
    assert np.isfinite(pred).all()


def test_crossfit_returns_predictions_for_every_row() -> None:
    df = pd.read_csv("tests/fixtures/bts_men_2k.csv")
    pred = crossfit(df, np.arange(len(df)), k=2, seed=0, item_ids=ITEMS, n_items=34)
    assert pred.shape == (len(df), 34)
    assert np.isfinite(pred).all()
    assert (pred > 0).any()


def test_train_returns_logistic_regression() -> None:
    df = pd.read_csv("tests/fixtures/bts_men_2k.csv")
    model = train(df, ITEMS, 34)
    assert isinstance(model, LogisticRegression)
    assert 0.0 <= predict_proba(model, np.zeros(4), 0, 1, 34) <= 1.0
