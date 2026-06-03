"""
SEPA screener — fetch price data and run Mark Minervini's Trend Template
across a universe of stocks.

Usage (CLI):
    python screener.py --tickers AAPL,MSFT,NVDA
    python screener.py            # uses the default demo universe
"""

from __future__ import annotations

import argparse
import pandas as pd
import yfinance as yf

from trend_template import check_trend_template, CRITERIA_LABELS
from relative_strength import raw_rs_score, rs_ratings


# A small demo universe so the tool does something out of the box.
DEFAULT_UNIVERSE = [
    "AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA", "AVGO",
    "JPM", "V", "MA", "COST", "LLY", "UNH", "HD", "NFLX", "AMD",
    "CRM", "ADBE", "ORCL", "PLTR", "SMCI", "CAT", "GE", "BA",
]


def fetch_close(ticker: str, period: str = "2y") -> pd.DataFrame | None:
    """Return a DataFrame with a single 'Close' column, or None on failure."""
    try:
        hist = yf.Ticker(ticker).history(period=period, auto_adjust=True)
        if hist.empty or "Close" not in hist:
            return None
        return hist[["Close"]].copy()
    except Exception:
        return None


def run_screen(tickers: list[str], period: str = "2y",
               progress=None) -> pd.DataFrame:
    """Fetch every ticker, compute relative strength across the universe, then
    apply the Trend Template. Returns a results DataFrame sorted by RS rating.

    `progress` is an optional callback(fraction, label) for UI progress bars.
    """
    data: dict[str, pd.DataFrame] = {}
    n = len(tickers)
    for i, t in enumerate(tickers):
        t = t.strip().upper()
        if not t:
            continue
        df = fetch_close(t, period)
        if df is not None:
            data[t] = df
        if progress:
            progress((i + 1) / n, f"Fetching {t}")

    # Relative strength is ranked across the whole fetched universe.
    raw = {t: raw_rs_score(df) for t, df in data.items()}
    ratings = rs_ratings({t: s for t, s in raw.items() if s is not None})

    rows = []
    for t, df in data.items():
        res = check_trend_template(t, df, ratings.get(t, 0.0))
        rows.append(res.as_dict())

    if not rows:
        return pd.DataFrame()

    out = pd.DataFrame(rows).sort_values(
        ["passes", "rs_rating"], ascending=[False, False]
    ).reset_index(drop=True)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Minervini Trend Template screener")
    ap.add_argument("--tickers", help="Comma-separated tickers (default: demo universe)")
    ap.add_argument("--period", default="2y", help="History window (e.g. 1y, 2y)")
    args = ap.parse_args()

    tickers = args.tickers.split(",") if args.tickers else DEFAULT_UNIVERSE
    print(f"Screening {len(tickers)} tickers...\n")
    results = run_screen(tickers, args.period,
                         progress=lambda f, l: print(f"  {l}", end="\r"))
    print("\n")

    if results.empty:
        print("No data returned (check ticker symbols / network).")
        return

    passing = results[results["passes"]]
    cols = ["ticker", "price", "rs_rating", "pct_above_52w_low", "pct_below_52w_high"]
    print(f"PASSED ({len(passing)}/{len(results)}):")
    print(passing[cols].to_string(index=False) if not passing.empty else "  none")
    print(f"\nFull list:")
    print(results[cols].to_string(index=False))


if __name__ == "__main__":
    main()
