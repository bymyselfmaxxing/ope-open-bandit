"""Synthetic contextual bandit with a known true reward function."""

import numpy as np

DIM = 5
N_ACTIONS = 10
ACTIONS = np.arange(N_ACTIONS)

W1 = np.array(
    [
        [0.9, 0.4, 0.2, 0.7, 0.5],
        [0.3, 0.8, 0.1, 0.6, 0.2],
        [0.5, 0.2, 0.7, 0.3, 0.8],
        [0.2, 0.5, 0.9, 0.4, 0.1],
        [0.7, 0.1, 0.3, 0.8, 0.6],
        [0.4, 0.6, 0.5, 0.2, 0.9],
        [0.8, 0.3, 0.6, 0.1, 0.4],
        [0.1, 0.7, 0.8, 0.5, 0.3],
        [0.6, 0.9, 0.4, 0.7, 0.2],
        [0.2, 0.3, 0.9, 0.6, 0.5],
    ]
)
W2 = np.array(
    [
        [0.3, 0.2, 0.1, 0.4, 0.2],
        [0.2, 0.5, 0.3, 0.1, 0.4],
        [0.1, 0.3, 0.6, 0.2, 0.5],
        [0.4, 0.2, 0.5, 0.3, 0.1],
        [0.2, 0.6, 0.3, 0.5, 0.4],
        [0.5, 0.1, 0.4, 0.2, 0.6],
        [0.3, 0.5, 0.2, 0.7, 0.3],
        [0.6, 0.2, 0.7, 0.4, 0.2],
        [0.4, 0.7, 0.3, 0.1, 0.5],
        [0.1, 0.4, 0.6, 0.8, 0.3],
    ]
)
B = np.array([0.2, 0.1, 0.4, 0.3, 0.2, 0.5, 0.1, 0.3, 0.4, 0.2])


def action_scores(x: np.ndarray) -> np.ndarray:
    """Fixed nonlinear reward per (context, action).

    Args:
        x: Context matrix of shape (n, DIM).

    Returns:
        Reward matrix of shape (n, N_ACTIONS).
    """
    xa = np.asarray(x)
    s = xa @ W1.T + (xa**2) @ W2.T + B
    return 1.0 / (1.0 + np.exp(-s))


def policy_probs(x: np.ndarray, temperature: float) -> np.ndarray:
    """Softmax policy over actions for each context, temperature-scaled.

    Args:
        x: Context matrix of shape (n, DIM).
        temperature: Softmax inverse temperature.

    Returns:
        Policy matrix of shape (n, N_ACTIONS).
    """
    scores = action_scores(x) / temperature
    scores = scores - scores.max(axis=1, keepdims=True)
    e = np.exp(scores)
    return e / e.sum(axis=1, keepdims=True)


def true_value(x: np.ndarray, temperature: float) -> float:
    """Monte Carlo expected reward under the policy, from a context sample.

    Args:
        x: Context matrix of shape (n, DIM).
        temperature: Softmax inverse temperature.

    Returns:
        Point estimate of the expected reward and its Monte Carlo standard error.
    """
    pi = policy_probs(x, temperature)
    vals = np.sum(pi * action_scores(x), axis=1)
    se = float(np.std(vals, ddof=1) / np.sqrt(len(vals)))
    return float(np.mean(vals)), se


def sample_actions(rng: np.random.Generator, pi: np.ndarray) -> np.ndarray:
    """Sample actions from a policy matrix of shape (n, N_ACTIONS)."""
    n = len(pi)
    u = rng.random(n)
    cum = np.cumsum(pi, axis=1)
    return (u[:, None] < cum).argmax(axis=1).astype(int)
