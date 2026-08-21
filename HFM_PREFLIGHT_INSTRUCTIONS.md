# HFM Cent preflight

The bundled v1.03 EX5 is the current compiled probe. It rejects zero-risk
outputs and, only when account currency is USC, profit currency is USD, and the
1-ounce contract check passes, can use deterministic USD-to-USC conversion.
Its final compile was `0 errors, 0 warnings`.

This probe is read-only. It contains no transaction API and cannot open, modify,
or close a trade.

1. Log in to an HFM Cent demo account in MT5.
2. Confirm `XAUUSDc` is visible in Market Watch.
3. Copy `HfmPreflight.ex5` into `MQL5/Scripts`.
4. Refresh Navigator, then run it once on any chart.
5. In the Experts log, locate lines beginning with `AURUM_PREFLIGHT|`.

Required pass conditions:

- `CHECK_HFM_IDENTITY=PASS`
- `CHECK_USC=PASS`
- `CHECK_CENT_SUFFIX=PASS`
- `CHECK_CONTRACT=PASS`
- `CHECK_MINIMUM_LOT=PASS`
- `CHECK_VOLUME_STEP=PASS`
- `CHECK_TRADE_MODE=PASS`
- `CHECK_TICK=PASS`
- `CHECK_CAPITAL_FOR_TARGET_RISK=PASS`
- `OVERALL=PASS`

With a 100 USC balance, the expected capital check is likely `FAIL`. That result
must not be bypassed by increasing risk or forcing 0.01 lot.

The 2026-08-20 live read-only run returned a 2.5371 USC minimum-lot risk for a
100 USC reference balance, or 2.5371%, and required about 2,537 USC for the
0.10% target. `OVERALL=FAIL` is therefore the correct result.
