"""Tests for the MLflow run-tracking wrapper."""

import pytest
from mlflow.tracking import MlflowClient

from ope.tracking import log_run


def test_log_run_creates_run_in_temp_store(tmp_path) -> None:
    store = tmp_path / "mlruns"
    run_id = log_run(
        config={"n": 5, "seed": 0},
        metrics={"rmse": 0.1},
        artifact_paths=[],
        experiment="test_exp",
        store_path=str(store),
    )
    client = MlflowClient(tracking_uri=f"file:{store.resolve()}")
    exp = client.get_experiment_by_name("test_exp")
    assert exp is not None
    runs = client.search_runs([exp.experiment_id])
    assert len(runs) == 1
    run = runs[0]
    assert run.info.run_id == run_id
    assert run.data.params.get("n") == "5"
    assert run.data.metrics.get("rmse") == pytest.approx(0.1)
