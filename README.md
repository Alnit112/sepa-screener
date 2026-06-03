# SEPA Trend Template Screener

An interactive stock screener that filters a universe of stocks against **Mark Minervini's 8-point Trend Template** — the core technical filter of his SEPA (Specific Entry Point Analysis) methodology for finding stocks in a confirmed Stage 2 uptrend.

Built with Python and Streamlit, with relative strength ranked across the universe IBD-style.

![screenshot](docs/screenshot.png)

## What it does

Give it a list of tickers and it fetches up to 2 years of price history, ranks each stock's relative strength against the rest of the universe, and reports which stocks meet all eight of Minervini's criteria — plus a full breakdown showing exactly which criteria each stock passes or fails.

## The Trend Template

A stock must satisfy all eight to qualify:

1. Price is above both the 150-day and 200-day moving averages
2. The 150-day MA is above the 200-day MA
3. The 200-day MA is trending up (at least 1 month)
4. The 50-day MA is above both the 150-day and 200-day MAs
5. Price is above the 50-day MA
6. Price is at least 30% above its 52-week low
7. Price is within 25% of its 52-week high
8. Relative Strength rating is at least 70 (1–99 scale)

## Relative strength

Criterion 8 needs a market-relative measure, so the screener computes an IBD-style weighted performance score for each stock —

```
score = 0.4·Q1 + 0.2·Q2 + 0.2·Q3 + 0.2·Q4   (Q1 = most recent quarter)
```

— then percentile-ranks every stock's score across the screened universe and scales it to 1–99. A broader universe gives a more meaningful rating.

## Run it locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Or use the command line:

```bash
python screener.py --tickers AAPL,MSFT,NVDA
python screener.py            # uses the built-in demo universe
```

## Deploy (free)

Push to GitHub and deploy on [share.streamlit.io](https://share.streamlit.io) — point it at `app.py` and it's live.

## Tests

The screening logic is covered by offline unit tests using synthetic price series, so they run without a network connection:

```bash
python test_trend_template.py
```

## Project structure

```
trend_template.py     # the 8 criteria
relative_strength.py  # IBD-style RS scoring + percentile ranking
screener.py           # data fetching (yfinance) + orchestration + CLI
app.py                # Streamlit UI
test_trend_template.py
```

## Tech

Python · Streamlit · pandas · NumPy · yfinance

---

*Educational tool only — not investment advice.*
