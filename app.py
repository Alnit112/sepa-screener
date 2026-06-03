"""
Streamlit front end for the Minervini Trend Template screener.

Run locally:   streamlit run app.py
Deploy free:   push to GitHub, then deploy on share.streamlit.io
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from screener import run_screen, DEFAULT_UNIVERSE
from trend_template import CRITERIA_LABELS

st.set_page_config(page_title="SEPA Trend Screener", page_icon="📈", layout="wide")

st.title("Minervini Trend Template Screener")
st.caption(
    "Screens stocks against Mark Minervini's 8-point Trend Template — the core "
    "filter of his SEPA methodology for identifying stocks in a confirmed "
    "Stage 2 uptrend."
)

with st.sidebar:
    st.header("Universe")
    tickers_text = st.text_area(
        "Tickers (comma or newline separated)",
        value=", ".join(DEFAULT_UNIVERSE),
        height=160,
    )
    period = st.selectbox("History window", ["1y", "2y", "3y"], index=1)
    run = st.button("Run screen", type="primary", use_container_width=True)
    st.markdown("---")
    st.markdown(
        "**The 8 criteria**\n\n" +
        "\n".join(f"- {label}" for label in CRITERIA_LABELS.values())
    )


@st.cache_data(show_spinner=False)
def cached_screen(tickers_tuple: tuple[str, ...], period: str) -> pd.DataFrame:
    return run_screen(list(tickers_tuple), period)


def parse_tickers(text: str) -> list[str]:
    raw = text.replace("\n", ",").split(",")
    seen, out = set(), []
    for t in (x.strip().upper() for x in raw):
        if t and t not in seen:
            seen.add(t)
            out.append(t)
    return out


if run:
    tickers = parse_tickers(tickers_text)
    if not tickers:
        st.warning("Add at least one ticker.")
        st.stop()

    bar = st.progress(0.0, text="Starting...")
    results = run_screen(tickers, period, progress=lambda f, l: bar.progress(f, text=l))
    bar.empty()

    if results.empty:
        st.error("No data returned. Check the ticker symbols or try again.")
        st.stop()

    passing = results[results["passes"]]
    c1, c2, c3 = st.columns(3)
    c1.metric("Scanned", len(results))
    c2.metric("Passed all 8", len(passing))
    c3.metric("Pass rate", f"{round(len(passing) / len(results) * 100)}%")

    st.subheader("Stocks passing the Trend Template")
    if passing.empty:
        st.info("No stocks in this universe currently pass all 8 criteria.")
    else:
        view = passing[["ticker", "price", "rs_rating",
                        "pct_above_52w_low", "pct_below_52w_high"]].copy()
        view.columns = ["Ticker", "Price", "RS rating",
                        "% above 52w low", "% below 52w high"]
        st.dataframe(view, hide_index=True, use_container_width=True)

    st.subheader("Full results")
    flag_cols = list(CRITERIA_LABELS.keys())
    detail = results[["ticker", "passes", "price", "rs_rating"] + flag_cols].copy()
    st.dataframe(
        detail.rename(columns={"ticker": "Ticker", "passes": "Passes",
                               "price": "Price", "rs_rating": "RS",
                               **CRITERIA_LABELS}),
        hide_index=True, use_container_width=True,
    )

    st.caption(
        "Educational tool, not investment advice. Relative Strength is ranked "
        "within the universe you screen, so a broader universe gives a more "
        "meaningful RS rating."
    )
else:
    st.info("Set your universe in the sidebar and hit **Run screen**.")
