"""Run the Phase 3 synthetic benchmark grid and write per-cell results."""

import argparse
import csv
import json
from pathlib import Path

import numpy as np

from ope.evaluation import run_replicate
from ope.simulate import action_scores, true_value
from ope.tracking import log_run

OVERLAYS = [0.25, 1.0, 4.0]
ETAS = [0.0, 0.1, 0.2]
SIGMAS = [0.0, 0.5]
N_VALUES = [500, 1000, 5000, 20000]
B = 1000
TRUE_CTX = 100_000
ESTIMATORS = ("ipw", "snipw", "dm", "dr")
RESULTS_DIR = Path("results/synthetic")
WG1 = np.arange(50, dtype=float).reshape(5, 10) * 0.05
WG2 = np.arange(50, dtype=float).reshape(5, 10) * 0.07


def reward_with_error(x: np.ndarray, eta: float) -> np.ndarray:
    """Apply the reward-model error dial: q_hat = clip(q + eta * g, 0, 1)."""
    base = action_scores(x)
    g = 0.2 * (x @ WG1) + 0.1 * np.sin(x @ WG2 + 1.0)
    return np.clip(base + eta * g, 0.0, 1.0)


def run_cell(n: int, b: int, seed: int, temp_b: float, temp_e: float, eta: float, sigma: float) -> dict:
    """Run one synthetic benchmark cell and summarise it against the true value."""
    rng = np.random.default_rng(seed)
    x_true = rng.normal(0.0, 1.0, size=(TRUE_CTX, 5))
    v_true, _se_true = true_value(x_true, temp_e)
    ests = {k: [] for k in ESTIMATORS}
    ses = {k: [] for k in ESTIMATORS}
    ess_vals = []
    max_w_vals = []
    cv_vals = []
    for _ in range(b):
        x = rng.normal(0.0, 1.0, size=(n, 5))
        res = run_replicate(
            rng,
            n,
            temperature_b=temp_b,
            temperature_e=temp_e,
            reward=reward_with_error(x, eta) if eta > 0 else None,
            propensity_sigma=sigma,
            x=x,
        )
        for k in ESTIMATORS:
            ests[k].append(res[k])
            ses[k].append(res["se_" + k])
        ess_vals.append(res["ess"])
        max_w_vals.append(res["max_weight"])
        cv_vals.append(res["weight_cv"])
    summaries = {}
    for k in ESTIMATORS:
        arr = np.array(ests[k])
        se_arr = np.array(ses[k])
        summaries[k] = {
            "bias": float(np.mean(arr - v_true)),
            "std": float(np.std(arr)),
            "rmse": float(np.sqrt(np.mean((arr - v_true) ** 2))),
            "coverage": float(np.mean(np.abs(arr - v_true) <= 1.96 * se_arr)),
            "se_coverage": float(np.sqrt(0.95 * 0.05 / b)),
        }
    return {
        "n": n,
        "b": b,
        "seed": seed,
        "temp_b": temp_b,
        "temp_e": temp_e,
        "eta": eta,
        "sigma": sigma,
        "v_true": v_true,
        "summaries": summaries,
        "ess_mean": float(np.mean(ess_vals)),
        "max_weight_mean": float(np.mean(max_w_vals)),
        "weight_cv_mean": float(np.mean(cv_vals)),
    }


def write_outputs(result: dict, cell_key: str) -> Path:
    """Write one cell result as JSON and estimator summaries as CSV."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    json_path = RESULTS_DIR / f"{cell_key}.json"
    json_path.write_text(json.dumps(result, indent=2, default=float))
    csv_path = RESULTS_DIR / f"{cell_key}.csv"
    with open(csv_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["estimator", "bias", "std", "rmse", "coverage"])
        for k in ESTIMATORS:
            s = result["summaries"][k]
            w.writerow([k, s["bias"], s["std"], s["rmse"], s["coverage"]])
    return csv_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, default=5000)
    parser.add_argument("--b", type=int, default=B)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--temp-b", type=float, default=1.0)
    parser.add_argument("--temp-e", type=float, default=1.0)
    parser.add_argument("--eta", type=float, default=0.0)
    parser.add_argument("--sigma", type=float, default=0.0)
    args = parser.parse_args()
    result = run_cell(args.n, args.b, args.seed, args.temp_b, args.temp_e, args.eta, args.sigma)
    cell_key = f"{args.temp_e}_{args.eta}_{args.sigma}_{args.n}"
    csv_path = write_outputs(result, cell_key)
    best = min(ESTIMATORS, key=lambda k: result["summaries"][k]["rmse"])
    log_run(
        config={
            "n": args.n,
            "b": args.b,
            "seed": args.seed,
            "temp_b": args.temp_b,
            "temp_e": args.temp_e,
            "eta": args.eta,
            "sigma": args.sigma,
        },
        metrics={"rmse": result["summaries"][best]["rmse"], "coverage": result["summaries"][best]["coverage"]},
        artifact_paths=[str(csv_path)],
        experiment="synthetic",
    )
    print(json.dumps(result, indent=2, default=float))


if __name__ == "__main__":
    main()
