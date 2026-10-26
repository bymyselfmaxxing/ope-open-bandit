"""Log loading and schema validation for OPE experiment inputs."""

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = (
    "timestamp",
    "item_id",
    "position",
    "click",
    "propensity_score",
    "user_feature_0",
    "user_feature_1",
    "user_feature_2",
    "user_feature_3",
)


def load_log(path: str | Path) -> pd.DataFrame:
    """Load a behaviour or target log CSV and validate its schema.

    Args:
        path: File path to the log CSV.

    Returns:
        Validated DataFrame.

    Raises:
        ValueError: If required columns are missing or values are out of range.
    """
    df = pd.read_csv(path)
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"missing required columns: {missing}")
    bad_click = int(((df["click"] != 0) & (df["click"] != 1)).sum())
    if bad_click:
        raise ValueError(f"click must be 0 or 1; found {bad_click} invalid rows")
    bad_prop = float((df["propensity_score"] <= 0).sum())
    if bad_prop:
        raise ValueError(f"propensity_score must be > 0; found {bad_prop} rows <= 0")
    bad_pos = int(((df["position"] < 1) | (df["position"] > 3)).sum())
    if bad_pos:
        raise ValueError(f"position must be in {{1, 2, 3}}; found {bad_pos} invalid rows")
    if df["item_id"].isna().any() or int(df["item_id"].max()) > 33:
        raise ValueError("item_id out of range")
    if df[list(REQUIRED_COLUMNS[1:])].isna().any().any():
        raise ValueError("required columns contain NaN")
    logger.info("loaded %s: %d rows", path, len(df))
    return df
