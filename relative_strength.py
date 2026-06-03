"""
Relative Strength rating, IBD-style.

Minervini's 8th criterion requires a Relative Strength (RS) rating of at least
70. IBD's RS rating is a 1-99 percentile rank of a stock's price performance
against the rest of the market, weighting recent quarters more heavily.

We replicate the spirit of it:
  raw score = 0.4*Q1 + 0.2*Q2 + 0.2*Q3 + 0.2*Q4   (Q1 = most recent quarter)
then percentile-rank every stock's raw score across the screened universe and
scale to 1-99.
"""

from __future__ import annotations

import pandas as pd

QUARTER = 63  # trading days


def raw_rs_score(df: pd.DataFrame) -> float | None:
    """Weighted multi-quarter performance score for one stock, or None if there
    isn't enough history to compute it."""
    close = df["Close"].dropna()
    if len(close) < QUARTER * 4 + 1:
        return None

    c = close.iloc[-1]
    p1 = close.iloc[-QUARTER]
    p2 = close.iloc[-QUARTER * 2]
    p3 = close.iloc[-QUARTER * 3]
    p4 = close.iloc[-QUARTER * 4]

    q1 = c / p1 - 1
    q2 = p1 / p2 - 1
    q3 = p2 / p3 - 1
    q4 = p3 / p4 - 1

    return 0.4 * q1 + 0.2 * q2 + 0.2 * q3 + 0.2 * q4


def rs_ratings(scores: dict[str, float]) -> dict[str, float]:
    """Convert raw RS scores into 1-99 percentile ratings across the universe."""
    if not scores:
        return {}
    s = pd.Series(scores)
    pct = s.rank(pct=True)            # 0..1
    ratings = (pct * 98 + 1).round(1)  # 1..99
    return ratings.to_dict()
