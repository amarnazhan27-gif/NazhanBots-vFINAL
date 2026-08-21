# Research results — MetaQuotes-Demo

## Selection discipline

The original defaults were first tested separately on 2024 and 2025. They did
not pass: 2024 had profit factor 0.734 and 2025 had profit factor 1.006.

Asia was negative in both splits, so it was disabled. ADX >= 30 plus London BUY
and New York SELL was then selected from the 2024/2025 trade audit. Before
coding it as the default, the same fixed rule was checked on untouched 2022 and
2023 data. Both were positive. No parameter sweep was accepted after looking at
the untouched results.

## Final v1.30 combined regression

Dataset: MetaQuotes-Demo XAUUSD M1, generated ticks, 2022-01-01 through
2026-01-01, USD 10,000 stand-in account, risk 0.10%, one trade per day.

| Year | Closed trades | Win rate | Net result | Profit factor | Max cash drawdown |
|---|---:|---:|---:|---:|---:|
| 2022 | 24 | 45.83% | +18.36 | 1.152 | 45.73 |
| 2023 | 24 | 58.33% | +88.52 | 1.954 | 27.28 |
| 2024 | 17 | 47.06% | +17.31 | 1.212 | 47.99 |
| 2025 | 23 | 47.83% | +26.78 | 1.278 | 28.65 |
| Combined | 88 | 50.00% | +150.97 | 1.385 | 66.38 |

The combined tester processed 134,858,768 generated ticks and 1,413,150 bars,
ending at USD 10,150.97 with `Test passed`.

Across the 48 calendar months, 40 had at least one closed trade. Of those, 25
were positive and 15 were negative; eight had no trade. Therefore this build
does not meet, and does not claim, continuous monthly profit.

## Robustness checks

The following tests used the same generated-tick stand-in dataset. They are
sensitivity checks, not independent holdouts:

| Variant | Ending balance | Interpretation |
|---|---:|---|
| ADX 28, one trade/day | 10,153.75 | Small change versus default |
| ADX 30, one trade/day | 10,150.97 | Release default |
| ADX 32, one trade/day | 10,104.97 | Edge weakens under stricter trend filter |
| ADX 30, two trades/day | 10,160.04 | Only four additional trades; some losing months worsened |
| ADX 30, random execution delay | 10,150.41 | Similar result in generated-tick delay simulation |

The two-trade cap was not promoted. The small increase in in-sample ending
balance is insufficient to justify extra exposure. The ADX 32 deterioration
also means the strategy should not be described as parameter-proof.

## Untouched older period and real-tick checks

The same fixed v1.30 defaults were tested without retuning on 2015-01-01
through 2021-12-31. Generated ticks produced 36 trades, net -32.02, profit
factor 0.848, and max cash drawdown 119.60. The 2021 subset was repeated on
v1.34 with `Every tick based on real ticks`: 27,326,856 ticks, 21 trades, net
-57.43, profit factor 0.587, max cash drawdown 98.80, and `Test passed`.

The unchanged fixed rule in binary v1.34 was run separately on every year from
2021 through 2025 with `Every tick based on real ticks` and random execution
delay. No parameter was changed between years.

| Year | Real ticks | Trades | Net | Profit factor | Max cash drawdown |
|---|---:|---:|---:|---:|---:|
| 2021 | 27,326,856 | 21 | -57.43 | 0.587 | 98.80 |
| 2022 | 30,530,718 | 24 | +20.21 | 1.171 | 44.90 |
| 2023 | 36,616,460 | 24 | +87.16 | 1.958 | 25.07 |
| 2024 | 38,094,869 | 17 | +16.64 | 1.204 | 47.57 |
| 2025 | 34,010,622 | 22 | +37.73 | 1.430 | 28.42 |
| Combined | 166,579,525 | 108 | +104.31 | 1.202 | 108.11 |

All five tests reported `Test passed`. The combined result is positive, but
the loss in 2021 and weak 2022/2024 results show substantial regime dependence.
The historical v1.30 session breakdown was unstable too: London lost 68.44 in
2022 after gaining 12.91 in 2021, while New York lost 66.09 in 2021 and gained
87.36 in 2022. There is no stable session winner that can safely be hard-coded
from this sample.

## Sequence and friction stress

`scripts/robustness.py` resamples closed-trade P/L without changing the EA.
For the 2022-2025 generated-tick sample, 100,000 bootstrap simulations gave a
6.83% probability of non-positive net result. The bootstrap drawdown p95 was
127.50. Adding 1.50 per trade reduced net from 150.97 to 18.97; adding 2.00 per
trade changed it to -25.03.

Across the combined 2021-2025 real-tick sequence, 100,000 bootstrap simulations
gave a 17.26% probability of non-positive net result. Bootstrap drawdown p95
was 170.47. An additional 0.50 per trade reduced net from 104.31 to 50.31;
1.00 per trade changed it to -3.69. The combined PF was only 1.202 before this
extra-cost stress.

## Rejected improvements

- A D1 EMA200 direction filter made the older-period result worse.
- A rolling per-session profit-factor lock made the older-period result worse.
- London-only was positive in both broad periods, but had only 16 and 47 trades
  and became negative with an extra 1.00 cost per trade.
- Simple ADX buckets changed sign between the older and newer periods.

These variants were rejected and removed from the release source. Keeping a
worse rule because it sounds adaptive would be curve-fitting, not progress.

## HFM XAUUSDc real-tick research — 2026

The available HFM tick cache covers 2026-06-01 through 2026-08-13. A
release-equivalent run retained the 0.10% risk, one-trade/day cap, session
direction filter, USD news window, economic calendar, and fail-closed calendar.
USD 100 was used as the value equivalent of 10,000 USC because current
`USDUSC` conversion history was missing from the local tester.

The v1.34 rerun processed 17,210,479 real ticks and 72,611 bars. It produced
seven trades: four wins, three losses, net +0.19%, PF 1.826, and max cash
drawdown 0.15%. A 100,000-run bootstrap gave a 21.16% probability of
non-positive net. An additional 0.03 cost per trade changed net to -0.02.

This is encouraging directional evidence, but seven trades over roughly two
and a half months cannot establish profitability. It also does not apply to the
user's corrected 525 USC capital, where every setup remains below minimum
volume. Machine-readable evidence is in
`evidence/hfm/research-2026.json`.

## HFM XAUUSDc generated-tick research — 2023-2025

The same release-equivalent preset was run against HFM bar history from
2023-01-01 through 2025-12-31 with generated ticks and random execution delay.
It processed 130,420,315 ticks and 1,057,530 bars and reported `Test passed`.

Only ten trades closed: three in 2023, one in 2024, and six in 2025. The v1.34
rerun was -0.09 in 2023, -0.05 in 2024, and +0.25 in 2025, for +0.11 combined.
The combined PF was 1.262 and max cash drawdown was 0.24. All ten deal results
sum exactly to the tester's +0.11 balance change.

A 100,000-run bootstrap gave a 36.19% probability of non-positive net. An
additional 0.02 cost per trade changed +0.11 to -0.09. The apparent London
advantage came from only six trades, while HFM server/DST mapping is still
unverified, so it was not promoted into a new rule. Retuning on ten trades
would be curve-fitting.

This test extends broker-history coverage but is weaker than real-tick evidence.
Its negative 2023 and 2024 results fail the stability gate. Machine-readable
evidence is in `evidence/hfm/generated-2023-2025.json`.

## External research boundary

- MQL5 documents `WebRequest()` as synchronous and unavailable in the Strategy
  Tester. Telegram therefore uses an external outbox relay instead of blocking
  the EA's trading path.
- Public GitHub projects were inspected for MT5/Telegram and EA architecture
  patterns. No third-party strategy code or profitability claim was copied.
- A public MT5 utility that clamps undersized volume up to broker minimum and
  exposes grid/martingale options was explicitly rejected; that pattern would
  violate the 525 USC risk ceiling. General EA31337/EarnForex execution helpers
  add no independent edge evidence, and a Gold ORB example is H1/server-time
  specific rather than an HFM M1 Cent validation.
- LONA supplied only a 5-minute generic XAUUSD dataset, not HFM M1 ticks or USC
  contract accounting. TradingCursor supplied one current market snapshot.
  Neither was used as backtest evidence or as a reason to retune the fixed rule.
- MetaTrader's official Strategy Tester documentation treats a test as one
  historical run and supports broker/margin/commission simulation. That is why
  tester results remain separate from forward-demo and real-readiness claims.
- Repository popularity and backtest screenshots were not treated as evidence
  that an XAUUSD EA will work on this HFM Cent account.

## Interpretation boundary

The fixed rule is profitable in the 2022-2025 MetaQuotes stand-in and in the
2025 real-tick holdout, but loses in the untouched older period and the 2021
real-tick test. HFM generated-tick history also lost in 2023 and 2024. It is
therefore not robust enough for real funds. HFM server/DST mapping and native
USC tester accounting remain unresolved.
