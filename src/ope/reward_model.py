"""Logistic regression reward model with cross-fitting."""

import hashlib

import numpy as np
from sklearn.linear_model import LogisticRegression

N_LEVELS = 8
N_USER_FEATURES = 4
N_POSITIONS = 3


def _user_level(s: str) -> float:
    """Stable categorical level for a hashed user feature string."""
    return float(int(hashlib.md5(s.encode()).hexdigest(), 16) % N_LEVELS)


def _features(user_levels: np.ndarray, item_id: int, position: int, n_items: int) -> np.ndarray:
    """Design vector for one (context, candidate item) pair."""
    k = N_USER_FEATURES + n_items + N_POSITIONS
    x = np.zeros(k)
    x[0:N_USER_FEATURES] = user_levels
    x[N_USER_FEATURES + item_id] = 1.0
    x[N_USER_FEATURES + n_items + (position - 1)] = 1.0
    return x


def _user_levels(row) -> np.ndarray:
    return np.array(
        [_user_level(str(row[f"user_feature_{j}"])) for j in range(N_USER_FEATURES)],
        dtype=float,
    )


def _design(df, item_ids: list[int], n_items: int):
    """Design matrix and targets over all (row, candidate item) pairs."""
    xs, ys = [], []
    for _, row in df.iterrows():
        user_levels = _user_levels(row)
        for a in item_ids:
            xs.append(_features(user_levels, a, int(row["position"]), n_items))
            ys.append(float(row["click"]))
    return np.array(xs), np.array(ys)


def train(df, item_ids: list[int], n_items: int, **kwargs) -> LogisticRegression:
    """Fit the reward model on (context, candidate item) pairs."""
    X, y = _design(df, item_ids, n_items)
    model = LogisticRegression(max_iter=1000, **kwargs)
    model.fit(X, y)
    return model


def predict_proba(
    model: LogisticRegression,
    user_levels: np.ndarray,
    item_id: int,
    position: int,
    n_items: int,
) -> float:
    """Predicted click probability for one (context, candidate item)."""
    x = _features(user_levels, item_id, position, n_items)
    return float(model.predict_proba(x.reshape(1, -1))[0][1])


def predict_all(model: LogisticRegression, df, item_ids: list[int], n_items: int) -> np.ndarray:
    """Predicted click probability for every (row, candidate item); shape (n, n_items)."""
    out = np.zeros((len(df), n_items))
    for i, (_, row) in enumerate(df.iterrows()):
        user_levels = _user_levels(row)
        for a in item_ids:
            out[i, a] = predict_proba(model, user_levels, a, int(row["position"]), n_items)
    return out


def crossfit(df, groups, k: int = 2, seed: int = 0, item_ids: list[int] | None = None, n_items: int = 34) -> np.ndarray:
    """Cross-fit the reward model; each row is predicted by a model trained without its group."""
    if item_ids is None:
        item_ids = list(range(n_items))
    n = len(df)
    K = len(item_ids)
    xs, ys, row_of = [], [], []
    for i, (_, row) in enumerate(df.iterrows()):
        user_levels = _user_levels(row)
        for j, a in enumerate(item_ids):
            xs.append(_features(user_levels, a, int(row["position"]), n_items))
            ys.append(float(row["click"]))
            row_of.append(i)
    X = np.array(xs)
    y = np.array(ys)
    gid = np.asarray(groups)
    group_fold = {g: i % k for i, g in enumerate(sorted(set(gid.tolist())))}
    models: dict[int, LogisticRegression] = {}
    predictions = np.zeros((n, n_items))
    for i in range(n):
        f = group_fold[gid[i]]
        if f not in models:
            folds_per_row = [group_fold[gid[r]] for r in row_of]
            train_idx = [t for t in range(len(X)) if folds_per_row[t] != f]
            models[f] = LogisticRegression(max_iter=1000).fit(X[train_idx], y[train_idx])
        for j, a in enumerate(item_ids):
            predictions[i, a] = float(models[f].predict_proba(X[i * K + j].reshape(1, -1))[0][1])
    return predictions
