"""Thin MLflow wrapper for experiment run tracking."""

import os
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import mlflow

os.environ.setdefault("MLFLOW_ALLOW_FILE_STORE", "true")

DEFAULT_STORE_PATH = "mlruns"


def log_run(
    config: Mapping[str, Any],
    metrics: Mapping[str, float],
    artifact_paths: list[str],
    experiment: str = "ope",
    store_path: str = DEFAULT_STORE_PATH,
) -> str:
    """Log one experiment run to a local MLflow file store.

    Args:
        config: Run settings; persisted alongside metrics and artifacts.
        metrics: Metric name to float value.
        artifact_paths: Files to log as artifacts.
        experiment: MLflow experiment name.
        store_path: Local directory for the MLflow file store.

    Returns:
        The MLflow run ID.
    """
    mlflow.set_tracking_uri(f"file:{Path(store_path).resolve()}")
    exp = mlflow.get_experiment_by_name(experiment)
    exp_id = exp.experiment_id if exp is not None else mlflow.create_experiment(experiment)
    with mlflow.start_run(experiment_id=exp_id) as run:
        mlflow.log_params({str(k): str(v) for k, v in config.items()})
        mlflow.log_metrics(dict(metrics))
        for p in artifact_paths:
            mlflow.log_artifact(p)
    return run.info.run_id
