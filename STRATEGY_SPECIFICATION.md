# AURUM Cent Adaptive M1 — Locked Development Specification

## Status and safety boundary

This is a trade-capable candidate for MT5 Strategy Tester and HFM demo
validation. Real-account support is compile-time disabled in v1.34. A future
real build would also require a runtime switch, exact-login authorization, and
mandatory HFM Cent/USC environment checks. A clean compile or a profitable
historical run does not make it ready for real funds.

The intended chart is an HFM Gold Cent symbol such as `XAUUSDc` on M1. Symbol
names and contract values are never hard-coded. All sizing uses the broker's
runtime symbol properties plus `OrderCalcProfit()` and `OrderCalcMargin()`.

## Capital constraint

The corrected requested starting balance is 525.00 USC. At that balance, a risk-compliant
volume is below HFM's minimum 0.01 lot for realistic Gold stops. The EA must
return `VOLUME_BELOW_MIN` with the calculated minimum-lot risk percentage
instead of rounding upward. Minimum-lot override is deliberately absent.

The exact-value HFM diagnostic found raw requests of 0.000495-0.001180 lot.
Forcing 0.01 lot would risk approximately 0.847%-2.020% per setup, versus the
0.10% target. The real-account capital gate therefore remains closed.

## Decision hierarchy

1. H1 supplies direction using closed-bar EMA200 bias and slope.
2. M15 classifies regime using closed-bar EMA20/EMA50, ADX/DI and ATR expansion.
3. M5 validates a trend pullback to EMA20 and candle quality.
4. M1 supplies a closed-bar sweep/reclaim or momentum trigger.
5. The broker-server session adjusts the minimum score and reward/risk target.
6. The current calendar month's prior is computed only from earlier years. It
   contributes at most +/-5 score and can never create an entry by itself.

Only the trend-pullback engine is enabled in v1. This is intentional. Adding
range and breakout engines before this engine has independent evidence would
multiply parameters and overfitting risk.

## Session profiles (broker server time)

| Profile | Hours | Minimum score | Target |
|---|---|---:|---:|
| Asia | 01:00–07:59 | disabled by default | 1.20R |
| London | 08:00–12:59 | 82 | 1.50R |
| New York | 13:00–20:59 | 85 | 1.40R |
| Blocked | 21:00–00:59 | n/a | n/a |

These times are provisional. They must be checked against the actual HFM server
clock and DST before interpreting tester or demo results.

The v1.20 default requires M15 ADX >= 30 and applies a direction/session filter:
London accepts BUY only and New York accepts SELL only. This rule was selected
on 2024/2025 evidence, then checked on untouched 2022/2023 splits before the
combined regression. It remains provisional until HFM real-tick validation.

## Mandatory entry vetoes

The EA blocks entry for a real account, wrong symbol/timeframe, invalid tick or
indicator data, non-trend regime, conflicting H1/M15 direction, invalid M5
pullback, invalid M1 trigger, rollover/Friday/US-data proxy window, open symbol
exposure, cooldown, daily trade cap, loss locks, excessive spread, invalid
SL/TP, volume below minimum, unsafe margin, failed `OrderCheck`, or failed order
execution.

No score is allowed to override a veto.

## Risk defaults

- Risk per trade: 0.10% equity.
- Maximum actual normalized risk: requested risk + 5% tolerance.
- One position on the symbol, including manual positions.
- One new trade per day.
- 20-minute cooldown.
- Three consecutive-loss lock.
- 0.75% daily equity lock.
- 2.00% weekly equity lock.
- 6.00% peak-equity emergency lock.
- Mandatory broker-side SL and TP.
- No martingale, grid, averaging, recovery sizing, hedging basket, partial close,
  or pending-entry ladder.

## Stop and target

The initial stop is behind the M1/M5 pullback structure with an ATR buffer. It
must also be at least four current spreads from entry and inside the configured
maximum M5 ATR distance. Target distance is the session profile's fixed R
multiple. Prices are aligned to broker tick size and revalidated against broker
stop levels.

## Test gates

1. Static audit: three-gate real authorization, mandatory SL, no lot override,
   and no prohibited recovery sizing.
2. MetaEditor: 0 errors. Warnings must be reviewed, not ignored.
3. Strategy Tester M1, `Every tick based on real ticks`, variable spread and
   execution delay.
4. Verify tester start/end markers and real-tick coverage.
5. Walk-forward and untouched holdout.
6. Forward demo with broker telemetry. The real-account preset remains locked
   until every broker-specific gate is evidenced.

## Objective real-readiness thresholds

Compile-time real support must remain disabled until all of these are true:

- HFM preflight passes broker, contract, currency, symbol, and capital checks.
  The 0.01 minimum lot must not exceed 105% of the configured 0.10% risk on an
  otherwise valid entry.
- Independent HFM real-tick walk-forward is positive after adverse-cost stress,
  has no negative validation fold, and its bootstrap probability of
  non-positive net is at most 10%.
- Forward demo covers at least six months and 30 closed trades, whichever takes
  longer. Net after actual commissions/swaps is positive, PF is at least 1.20,
  maximum equity drawdown is at most 2%, and there is no safety-gate breach.
- Broker-server session mapping is verified across a DST change. Calendar
  fail-closed behavior and restart/reconnect recovery have runtime evidence.
- Telegram relay retry and deduplication pass with protected environment
  credentials. Telegram failure must never block trading or risk controls.

Passing these thresholds reduces uncertainty; it does not guarantee future
profit or profit in every day or month. Re-enabling a real build requires a
separate source change, clean compile, hash-matched regression, and explicit
account authorization.
