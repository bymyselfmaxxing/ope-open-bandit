"""Loading and validation of experiment configuration files."""

from pathlib import Path

import yaml

REQUIRED_KEYS = {
    "synthetic": {"n", "b", "seed"},
    "real_data": {"n", "b", "seed"},
}


def load_config(path: str) -> dict:
    """Load a YAML experiment config and check required keys.

    Args:
        path: Config file path.

    Returns:
        Parsed config mapping.

    Raises:
        ValueError: If the file is missing or required keys are absent.
    """
    with open(path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    if not isinstance(cfg, dict):
        raise TypeError(f"config {path} must be a mapping")
    group = Path(path).stem
    settings = cfg.get(group) or {}
    missing = [k for k in REQUIRED_KEYS.get(group, set()) if k not in settings]
    if missing:
        raise ValueError(f"config {path} missing required keys: {missing}")
    return {group: settings}
