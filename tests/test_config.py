"""Tests for experiment configuration loading and validation."""

import pytest
from ope.config import load_config

VALID = """
synthetic:
  n: 5000
  b: 1000
  seed: 0
"""


def test_loads_valid_config(tmp_path) -> None:
    p = tmp_path / "synthetic.yaml"
    p.write_text(VALID)
    cfg = load_config(p)
    assert cfg["synthetic"]["n"] == 5000


def test_rejects_missing_key(tmp_path) -> None:
    p = tmp_path / "synthetic.yaml"
    p.write_text("synthetic:\n  n: 5000\n")
    with pytest.raises(ValueError, match="missing required keys"):
        load_config(p)
