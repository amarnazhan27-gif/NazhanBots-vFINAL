# Contributing to AURUM

Contributions are welcome for research, testing, reliability, and documentation.
This repository is a guarded MT5 research candidate for HFM Gold Cent. It is not
an invitation to enable live trading or to claim guaranteed returns.

## Before proposing a change

- Read `STRATEGY_SPECIFICATION.md`, `VALIDATION.md`, and
  `CAPITAL_FEASIBILITY.md`.
- Keep the existing safety boundary intact: no martingale, grid, averaging,
  recovery sizing, or minimum-lot override.
- Do not change `BUILD_ALLOW_REAL_ACCOUNT` or the default real-account switches.
- Do not commit credentials, account identifiers, terminal logs containing
  personal data, or notification tokens.

## Development and validation

1. Keep the change narrow and explain the hypothesis it tests.
2. Run `./static_audit.sh`.
3. For changes to the preflight probe, also run `./preflight_static_audit.sh`.
4. Run `python3 -m unittest -v tests/test_telegram_relay.py` after relay changes.
5. Recompile in MetaEditor and record the actual compiler result for MQL5
   changes. A clean compile is not performance evidence.
6. Use M1 testing with execution delay and document the symbol, broker server,
   date range, model, costs, and every material limitation.

## Pull requests

Each pull request should state:

- the problem and the falsifiable hypothesis;
- the files and risk controls affected;
- test commands and observed results;
- whether the result is static, compile, tester, or forward-demo evidence;
- limitations and any remaining gates.

Parameter changes must be validated out of sample. A better in-sample backtest
alone is not sufficient evidence for inclusion. Changes that weaken account,
risk, execution, calendar, or broker checks will not be accepted without
independent evidence and a documented safety review.

## Reporting issues

For bugs, include the MQL5 build, symbol, timeframe, tester mode, date range,
and a minimal reproducible journal excerpt with sensitive fields removed. For
strategy ideas, describe the mechanism, data required to test it, and the
out-of-sample acceptance condition.
