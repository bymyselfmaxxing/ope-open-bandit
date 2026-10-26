"""Generate Phase 3 synthetic benchmark figures from the per-cell results."""

import json
from pathlib import Path

import matplotlib.pyplot as plt

RESULTS_DIR = Path("results/synthetic")
N_VALUES = [500, 1000, 5000, 20000]
ESTIMATORS = ("ipw", "snipw", "dm", "dr")


def _load(temp_e: float, eta: float, sigma: float, n: int) -> dict:
    key = f"{temp_e}_{eta}_{sigma}_{n}"
    return json.loads((RESULTS_DIR / f"{key}.json").read_text())


def plot_rmse_vs_n() -> Path:
    plt.figure()
    for e in ESTIMATORS:
        plt.plot(N_VALUES, [_load(1.0, 0.0, 0.0, n)["summaries"][e]["rmse"] for n in N_VALUES], marker="o", label=e)
    plt.xlabel("n")
    plt.ylabel("RMSE")
    plt.legend()
    out = RESULTS_DIR / "figures" / "rmse_vs_n.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out)
    plt.close()
    return out


def plot_coverage_vs_n() -> Path:
    plt.figure()
    plt.errorbar(
        N_VALUES,
        [_load(1.0, 0.0, 0.0, n)["summaries"]["ipw"]["coverage"] for n in N_VALUES],
        yerr=[_load(1.0, 0.0, 0.0, n)["summaries"]["ipw"]["se_coverage"] for n in N_VALUES],
        marker="o",
        label="ipw",
    )
    plt.xlabel("n")
    plt.ylabel("coverage")
    plt.legend()
    out = RESULTS_DIR / "figures" / "coverage_vs_n.png"
    plt.savefig(out)
    plt.close()
    return out


def plot_dr_vs_ipw() -> Path:
    plt.figure()
    plt.plot([0.0, 0.1, 0.2], [_load(1.0, eta, 0.0, 20000)["summaries"]["dr"]["rmse"] for eta in (0.0, 0.1, 0.2)], marker="o", label="dr")
    plt.plot([0.0, 0.1, 0.2], [_load(1.0, eta, 0.0, 20000)["summaries"]["ipw"]["rmse"] for eta in (0.0, 0.1, 0.2)], marker="o", label="ipw")
    plt.xlabel("eta")
    plt.ylabel("RMSE")
    plt.legend()
    out = RESULTS_DIR / "figures" / "dr_vs_ipw.png"
    plt.savefig(out)
    plt.close()
    return out


def main() -> None:
    plot_rmse_vs_n()
    plot_coverage_vs_n()
    plot_dr_vs_ipw()


if __name__ == "__main__":
    main()
