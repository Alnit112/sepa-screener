"""
Mark Minervini's Trend Template — the 8 criteria a stock must meet to be in a
confirmed Stage 2 uptrend (the core filter of his SEPA methodology).

Each function works on a price history DataFrame with a 'Close' column and
returns plain, testable results so the logic can be checked without a live
network connection.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
import pandas as pd


# Trading-day approximations
DAYS_1M = 22
DAYS_52W = 252
MIN_HISTORY = 252  # need ~1 year of data for the moving averages + RS


@dataclass
class TrendResult:
    ticker: str
    passes: bool
    price: float
    rs_rating: float
    # Individual criteria (True = met)
    above_150_200: bool
    sma150_above_200: bool
    sma200_trending_up: bool
    sma50_above_150_200: bool
    price_above_50: bool
    above_52w_low: bool
    near_52w_high: bool
    rs_above_70: bool
    # Context for display
    pct_above_52w_low: float
    pct_below_52w_high: float
    note: str = ""

    def as_dict(self) -> dict:
        return asdict(self)


def compute_indicators(df: pd.DataFrame) -> dict:
    """Return the moving averages and 52-week high/low from a price history."""
    close = df["Close"].dropna()
    return {
        "price": float(close.iloc[-1]),
        "sma50": close.rolling(50).mean(),
        "sma150": close.rolling(150).mean(),
        "sma200": close.rolling(200).mean(),
        "low_52w": float(close.iloc[-DAYS_52W:].min()),
        "high_52w": float(close.iloc[-DAYS_52W:].max()),
    }


def check_trend_template(ticker: str, df: pd.DataFrame, rs_rating: float) -> TrendResult:
    """Apply all 8 Trend Template criteria to one stock.

    rs_rating is the 1-99 relative-strength rating computed across the screened
    universe (see relative_strength.py); Minervini requires it to be >= 70.
    """
    close = df["Close"].dropna()

    if len(close) < MIN_HISTORY:
        return TrendResult(
            ticker=ticker, passes=False, price=float(close.iloc[-1]) if len(close) else 0.0,
            rs_rating=rs_rating, above_150_200=False, sma150_above_200=False,
            sma200_trending_up=False, sma50_above_150_200=False, price_above_50=False,
            above_52w_low=False, near_52w_high=False, rs_above_70=False,
            pct_above_52w_low=0.0, pct_below_52w_high=0.0,
            note="Not enough price history (need ~1 year).",
        )

    ind = compute_indicators(df)
    price = ind["price"]
    sma50 = ind["sma50"].iloc[-1]
    sma150 = ind["sma150"].iloc[-1]
    sma200 = ind["sma200"].iloc[-1]
    sma200_1m_ago = ind["sma200"].iloc[-DAYS_1M]
    low_52w = ind["low_52w"]
    high_52w = ind["high_52w"]

    # The 8 criteria (cast to native bool so output stays clean)
    c1 = bool(price > sma150 and price > sma200)
    c2 = bool(sma150 > sma200)
    c3 = bool(sma200 > sma200_1m_ago)         # 200-day MA trending up (>= 1 month)
    c4 = bool(sma50 > sma150 and sma50 > sma200)
    c5 = bool(price > sma50)
    c6 = bool(price >= low_52w * 1.30)        # at least 30% above 52-week low
    c7 = bool(price >= high_52w * 0.75)       # within 25% of 52-week high
    c8 = bool(rs_rating >= 70)

    return TrendResult(
        ticker=ticker,
        passes=all([c1, c2, c3, c4, c5, c6, c7, c8]),
        price=round(price, 2),
        rs_rating=round(rs_rating, 1),
        above_150_200=c1, sma150_above_200=c2, sma200_trending_up=c3,
        sma50_above_150_200=c4, price_above_50=c5, above_52w_low=c6,
        near_52w_high=c7, rs_above_70=c8,
        pct_above_52w_low=round((price / low_52w - 1) * 100, 1),
        pct_below_52w_high=round((1 - price / high_52w) * 100, 1),
    )


CRITERIA_LABELS = {
    "above_150_200": "Price above 150 & 200-day MA",
    "sma150_above_200": "150-day MA above 200-day MA",
    "sma200_trending_up": "200-day MA trending up (1m+)",
    "sma50_above_150_200": "50-day MA above 150 & 200-day MA",
    "price_above_50": "Price above 50-day MA",
    "above_52w_low": "30%+ above 52-week low",
    "near_52w_high": "Within 25% of 52-week high",
    "rs_above_70": "Relative Strength rating >= 70",
}
