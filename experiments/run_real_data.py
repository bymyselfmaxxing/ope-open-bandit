"""Run the Phase 4 real-data benchmark: BTS behaviour vs uniform target (smoke)."""

import argparse
import json

import numpy as np
import pandas as pd

from ope.estimators import dm, dr, ipw, per_sample_terms, std_error
from ope.evaluation import uniform_policy
from ope.reward_model import crossfit
from ope.tracking import log_run

BEHAVIOR_LOG = "data/men_bts_10k.csv"
TARGET_LOG = "data/men_random_10k.csv"
N_ITEMS = 34


def run_replicate_real(
    n: int,
    behavior_log: str,
    target_log: str,
    n_items: int = N_ITEMS,
    seed: int = 0,
) -> dict:
    """One real-data replicate: BTS behaviour, uniform target, agreement with reference."""
    df_b = pd.read_csv(behavior_log)
    df_t = pd.read_csv(target_log)
    ref = float(df_t["click"].mean())
    se_ref = float(np.std(df_t["click"].to_numpy(), ddof=1) / np.sqrt(len(df_t)))
    pred = crossfit(df_b, np.arange(len(df_b)), k=2, seed=seed, item_ids=list(range(n_items)), n_items=n_items)
    pi_e = uniform_policy(n_items)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(df_b), size=n)
    r = df_b["click"].to_numpy()[idx]
    w = pi_e[df_b["item_id"].to_numpy()[idx]] / df_b["propensity_score"].to_numpy()[idx]
    q = pred[idx]
    q_pi = q.mean(axis=1)
    estimates = {
        "ipw": float(ipw(r, w)),
        "dm": float(dm(q)),
        "dr": float(dr(r, w, q, r)),
    }
    se = {
        "ipw": float(std_error(per_sample_terms(r, w))),
        "dm": float(np.sqrt(np.sum((q_pi - np.mean(q_pi)) ** 2)) / n),
    }
    agreement = float(
        np.mean([abs(estimates["ipw"] - ref) <= 1.96 * np.sqrt(se["ipw"] ** 2 + se_ref**2)])
    )
    return {
        "n": n,
        "estimates": estimates,
        "se": se,
        "reference": ref,
        "se_reference": se_ref,
        "agreement_ipw": agreement,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, default=200)
    parser.add_argument("--b", type=int, default=20)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--behavior-log", default=BEHAVIOR_LOG)
    parser.add_argument("--target-log", default=TARGET_LOG)
    args = parser.parse_args()
    results = [
        run_replicate_real(args.n, args.behavior_log, args.target_log, seed=args.seed + i) for i in range(args.b)
    ]
    agreements = [r["agreement_ipw"] for r in results]
    run_result = {
        "n": args.n,
        "b": args.b,
        "seed": args.seed,
        "agreement_ipw_mean": float(np.mean(agreements)),
        "references": [r["reference"] for r in results],
    }
    log_run(
        config={"n": args.n, "b": args.b, "seed": args.seed, "reward_model": "logistic"},
        metrics={"agreement_ipw": float(np.mean(agreements))},
        artifact_paths=[],
        experiment="real_data",
    )
    print(json.dumps(run_result, indent=2, default=float))


if __name__ == "__main__":
    main()
