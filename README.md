# Factor Forge Public

Factor Forge Public is a small, research-oriented toolkit for building and
testing quantitative market hypotheses. It focuses on transparent data models,
causal feature calculation, event studies, and forward-return analysis.

The repository is intentionally separated from any private trading system. It
does not contain production strategies, exchange credentials, proprietary
datasets, deployment configuration, notification targets, or live order
execution code.

## Research principles

- Use only information available at the decision timestamp.
- Keep raw candles separate from derived candles and features.
- Treat a research event as a hypothesis, not an order instruction.
- Include fees, slippage, and funding before claiming practical profitability.
- Validate on unseen periods and inspect parameter sensitivity.
- Record failed hypotheses instead of hiding them.

## Included

- Normalized OHLCV candle and research-event models
- Causal Heikin-Ashi transformation
- Basic candle-shape and trailing-window event detectors
- Forward-return and excursion analysis
- Summary statistics suitable for early-stage hypothesis screening
- Synthetic-data examples and tests

## Not included

- Live trading or exchange adapters
- Private strategy versions or optimized parameter sets
- Broker identifiers, API keys, local paths, or runtime service definitions
- Historical market databases or third-party API responses
- Claims of profitability or investment advice

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

## Run the example

```bash
python examples/synthetic_event_study.py
```

## Run tests

```bash
pytest
```

## Disclaimer

This project is for research and education only. Backtests and event studies do
not predict future performance. You are responsible for validating data quality,
execution assumptions, legal requirements, and financial risk before using any
research output.

## License

MIT
