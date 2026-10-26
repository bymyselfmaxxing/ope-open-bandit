"""Tests for behaviour log loading and schema validation."""

import pytest

from ope.data import load_log

FIXTURES = {
    "random_men_2k": "tests/fixtures/random_men_2k.csv",
    "bts_men_2k": "tests/fixtures/bts_men_2k.csv",
}

COLUMNS = [
    "Unnamed: 0",
    "timestamp",
    "item_id",
    "position",
    "click",
    "propensity_score",
    "user_feature_0",
    "user_feature_1",
    "user_feature_2",
    "user_feature_3",
]


@pytest.mark.parametrize("name,path", sorted(FIXTURES.items()))
def test_loads_fixture(name: str, path: str) -> None:
    df = load_log(path)
    assert len(df) == 2000
    for col in COLUMNS:
        assert col in df.columns


def test_rejects_missing_column(tmp_path) -> None:
    p = tmp_path / "bad.csv"
    p.write_text("timestamp,item_id,click\n2019-11-24,3,1\n")
    with pytest.raises(ValueError, match="missing required columns"):
        load_log(p)


def test_rejects_bad_click(tmp_path) -> None:
    p = tmp_path / "bad.csv"
    p.write_text(
        "timestamp,item_id,position,click,propensity_score,"
        "user_feature_0,user_feature_1,user_feature_2,user_feature_3\n"
        "2019-11-24,3,1,2,0.029,foo,bar,baz,qux\n"
    )
    with pytest.raises(ValueError, match="click must be 0 or 1"):
        load_log(p)


def test_rejects_zero_propensity(tmp_path) -> None:
    p = tmp_path / "bad.csv"
    p.write_text(
        "timestamp,item_id,position,click,propensity_score,"
        "user_feature_0,user_feature_1,user_feature_2,user_feature_3\n"
        "2019-11-24,3,1,1,0,foo,bar,baz,qux\n"
    )
    with pytest.raises(ValueError, match="propensity_score must be > 0"):
        load_log(p)


def test_rejects_unknown_position(tmp_path) -> None:
    p = tmp_path / "bad.csv"
    p.write_text(
        "timestamp,item_id,position,click,propensity_score,"
        "user_feature_0,user_feature_1,user_feature_2,user_feature_3\n"
        "2019-11-24,3,4,1,0.029,foo,bar,baz,qux\n"
    )
    with pytest.raises(ValueError, match="position must be in"):
        load_log(p)
