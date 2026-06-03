"""
Offline unit tests for the screening logic, using synthetic price series so
they run without a network connection.

    python -m pytest test_trend_template.py        (or: python test_trend_template.py)
"""

import numpy as np
import pandas as pd

from trend_template import check_trend_template
from relative_strength import raw_rs_score, rs_ratings


def _series(n=420, drift=0.0008, start=50, noise=0.008, seed=1) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rets = rng.normal(drift, noise, n)
    price = start * np.cumprod(1 + rets)
    return pd.DataFrame({"Close": price},
                        index=pd.date_range("2023-01-01", periods=n, freq="B"))


def _universe():
    data = {
        "STRONG": _series(drift=0.0018, noise=0.006, seed=1),
        "MILD":   _series(drift=0.0004, seed=2),
        "DOWN":   _series(drift=-0.0010, seed=3),
        "FLAT":   _series(drift=0.0000, seed=4),
    }
    raw = {t: raw_rs_score(df) for t, df in data.items()}
    ratings = rs_ratings({t: s for t, s in raw.items() if s is not None})
    return data, ratings


def test_strong_uptrend_passes_all():
    data, ratings = _universe()
    r = check_trend_template("STRONG", data["STRONG"], ratings["STRONG"])
    assert r.passes is True
    assert all([r.above_150_200, r.sma150_above_200, r.sma200_trending_up,
                r.sma50_above_150_200, r.price_above_50, r.above_52w_low,
                r.near_52w_high, r.rs_above_70])


def test_downtrend_fails():
    data, ratings = _universe()
    r = check_trend_template("DOWN", data["DOWN"], ratings["DOWN"])
    assert r.passes is False


def test_insufficient_history_fails_gracefully():
    short = _series(n=100)
    r = check_trend_template("SHORT", short, rs_rating=90)
    assert r.passes is False
    assert "history" in r.note.lower()


def test_rs_ratings_are_bounded():
    _, ratings = _universe()
    for v in ratings.values():
        assert 1 <= v <= 99


if __name__ == "__main__":
    test_strong_uptrend_passes_all()
    test_downtrend_fails()
    test_insufficient_history_fails_gracefully()
    test_rs_ratings_are_bounded()
    print("All tests passed.")
