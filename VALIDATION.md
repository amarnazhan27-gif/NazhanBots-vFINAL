# Validation evidence — v1.34, 2026-08-20

## Build

- Static audit: `STATIC AUDIT PASSED`.
- MetaEditor build 6063: clean compilation. See `compile.log` for the final
  elapsed time and `SHA256SUMS.txt` for source/binary identity.
- Compiled target: X64 Regular.
- The SHA-256 values are recorded in `SHA256SUMS.txt`.
- v1.34 final recompile: `0 errors, 0 warnings`, 1,158 ms, X64 Regular.
- v1.34 retains the fail-closed risk calculation helper. Its USC fallback is allowed
  only for the validated HFM cent contract: USC account currency, USD profit
  currency, HFM identity, cent symbol suffix, 1-ounce contract, and valid
  0.01 minimum/step volume. Other combinations remain rejected.
- Compile-time real-account support is disabled. On real accounts, HFM and USC
  validation also cannot be disabled through a preset.
- `OrderCheck()` must now return both `true` and `check.retcode=0`. FOK is
  preferred over IOC, unsupported Market Execution filling fails closed, and
  partial fills receive a distinct audit/notification event.
- A future real build is pinned to the validated conservative profile: 0.10%
  risk, one trade/day, Asia disabled, session-direction filter active, and the
  economic calendar enabled in fail-closed mode.

## Small-balance lifecycle smoke

This test used MetaQuotes-Demo `XAUUSD`, M1, generated ticks, one day, and a
USD 1.00 starting balance as the available stand-in for 100.00 USC.

- Initialization succeeded with risk 0.10% and broker minimum volume 0.01.
- Valid setup candidates were rejected with `VOLUME_BELOW_MIN`.
- Observed raw volumes were approximately 0.000002 to 0.000003 standard lots
  in the MetaQuotes stand-in environment.
- The EA did not round the unsafe volume up to 0.01 lot.
- 568,780 generated ticks and 1,380 bars completed with `Test passed`.
- Final balance remained USD 1.00.

This proves the small-balance safety path in the available standard-account
simulation. It does not verify HFM Cent contract specifications or USC
accounting.

## Execution-path smoke

This deliberately used a larger simulated balance so the minimum-volume gate
would not prevent exercising the order path. It used the same single-day
generated-tick MetaQuotes-Demo dataset. Its dedicated smoke preset enables Asia
to exercise the known 04:25 signal; the distributed release preset disables
Asia.

- One Asia BUY signal was approved at score 90.
- Requested volume was 0.02 lots with risk estimate USD 9.58.
- The market order was accepted with mandatory SL and TP.
- The position closed at TP in the simulation.
- `DEAL_AUDIT` recorded both entry and exit transactions.
- Final balance was USD 10,011.52 from USD 10,000.00.

This is execution smoke evidence only. One generated-tick trade is not evidence
of profitability, robustness, or expected return.

## HFM environment guard smoke

The strict HFM guard was run deliberately on MetaQuotes-Demo. Initialization
failed with `HFM_SERVER_REQUIRED`, as intended. This proves that the release
candidate does not silently accept a non-HFM server when broker validation is
enabled.

The real-account authorization path requires a separate compile-time source
change, the distributed false switch to be changed, and an exact account-login
match. The trade-capable real path was deliberately not exercised.

## Read-only HFM preflight probe

`AURUM_HFM_CENT_PREFLIGHT.mq5` was added to close the broker-evidence gap once
an HFM terminal becomes available. Its static audit found no `OrderSend`, trade
action, `CTrade`, buy/sell, close, modify, or delete transaction API. MetaEditor
compiled it with `0 errors, 0 warnings`. It checks HFM identity, USC, `XAUUSDc`,
contract size, minimum/step volume, trade mode, live spread, M1/M5 ATR, minimum
lot risk, and required equity for the 0.10% target.

The probe was subsequently run on the live HFM environment with automated
trading disabled. HFM identity, USC, `XAUUSDc`, USD profit currency, 1-ounce
contract, and 0.01 minimum/step volume were confirmed. Its v1.00 capital result
was rejected because zero calculated risk was accepted. v1.03 is now compiled
with zero errors and warnings and fails closed. The 2026-08-20 rerun measured
2.5371 USC minimum-lot risk. That was 2.5371% of the original 100 USC reference
balance and is still 0.4833% of the corrected 525 USC capital. It returned
`OVERALL=FAIL` as required.

## Unfinished external gates

- Earlier real-tick attempts stalled, but later isolated runs for every year
  from 2021 through 2025 completed. The v1.34 rerun net was +104.31 with PF
  1.202, but 2021 lost 57.43 and a 1.00-per-trade friction stress erased the combined
  profit. This fragility blocks live use.
- The main terminal now provides live HFM `XAUUSDc`/USC broker specifications,
  and an HFM real-tick sizing diagnostic is complete. The native USC attempt
  lacked 2026 `USDUSC` conversion history. The corrected 525 USC value-equivalent
  run completed and rejected all 11 candidates below broker minimum volume.
- HFM server-session offsets and DST remain unverified.
- The monthly prior had only one historical sample in the smoke environment and
  correctly withheld a bullish/bearish bias.
- A fixed-rule untouched holdout and Monte Carlo stress are now complete and
  expose fragility. HFM real-tick walk-forward and multi-month HFM forward demo
  remain required before any live-readiness conclusion.

## Status

The deliverable is a compiled demo/tester candidate whose order path has been
exercised in simulation. Real-account support is compile-time locked. It is not
a profitability proof and is not ready for real funds until the capital,
robustness, HFM real-tick walk-forward, and forward-demo gates pass.

## Historical v1.30 regression and notification checks

- The 2022-2025 generated-tick regression repeated the v1.20 outcome exactly:
  134,858,768 ticks, 1,413,150 bars, 88 trades, final balance USD 10,150.97,
  and `Test passed`.
- A random execution-delay run ended at USD 10,150.41 and `Test passed`.
- ADX sensitivity runs ended at USD 10,153.75 for ADX 28 and USD 10,104.97
  for ADX 32.
- A two-trade/day cap ended at USD 10,160.04 with 92 trades, but did not remove
  losing months and was not selected as default.
- `telegram_relay.py` passed Python bytecode compilation and a two-event dry run.
  A second run produced no duplicate output because its offset was persisted.
- Its unit test also proved that a concurrent partial final record is withheld
  until the newline arrives, then delivered once; failures back off up to 60
  seconds without advancing the stored offset.
- Telegram live delivery remains unverified. Credentials are accepted only from
  relay environment variables and are never stored in the EA or preset.

## Real-tick robustness evidence

- 2021: 27,326,856 real ticks; 21 trades; net -57.43; PF 0.587; max cash
  drawdown 98.80.
- 2025 with random execution delay: 34,010,622 real ticks; 22 trades; net
  +37.73; PF 1.430; max cash drawdown 28.42.
- 2022: +20.21, PF 1.171; 2023: +87.16, PF 1.958; 2024: +16.64, PF 1.204.
- Combined 2021-2025: 166,579,525 real ticks; 108 trades; +104.31; PF 1.202;
  max cash drawdown 108.11; bootstrap probability of non-positive net 17.26%.
- All five runs reported `Test passed`. Their variation is strategy risk, not a
  tester lifecycle failure.

## HFM small-balance real-tick evidence

- HFM `XAUUSDc`, 2026-06-01 through 2026-08-13, random execution delay.
- 17,210,479 real ticks and 72,611 bars; `Test passed`.
- USD 1.00 tester deposit used as the value equivalent of 100 USC because the
  local HFM tester lacked current `USDUSC` conversion history.
- Broker specification: contract 1.0, minimum/step 0.01, tick size 0.01.
- 11 valid setup candidates; all 11 rejected with `VOLUME_BELOW_MIN`.
- Raw requested volume 0.000094-0.000225; required minimum-lot risk 4%-11%.
- Zero orders, zero deals, unchanged balance. This proves the safety path and
  capital infeasibility, not profitability.

## HFM corrected 525 USC capital evidence

- HFM `XAUUSDc`, 2026-06-01 through 2026-08-13, random execution delay.
- 17,210,479 ticks and 72,611 bars; `Test passed`.
- MT5 rounded a fractional USD 5.25 tester deposit to USD 5.00. The accepted
  exact-value workaround used USD 5.00 at 0.105% risk. Its USD 0.00525 risk
  budget equals 0.525 USC, exactly 0.10% of 525 USC.
- 11 valid setup candidates; all 11 rejected with `VOLUME_BELOW_MIN`.
- Raw volume was 0.000495-0.001180 lot. At HFM's 0.01 minimum, approximate
  per-trade risk would be 0.847%-2.020% of 525 USC.
- Zero orders, zero deals, unchanged balance. The approximate equity required
  to preserve 0.10% risk on these setups is 4,449-10,606 USC.
- The tester reported mismatched/discarded real ticks for 544 of 72,611 minute
  bars (0.7492%) and used generated ticks for those affected minutes. This is
  recorded as a data-quality limitation, not hidden as pure real-tick coverage.
- Evidence: `HFM_TESTER_525_USC_EVIDENCE.json` and
  `HFM_TESTER_525_USC_LOG_SNAPSHOT.txt`.

## HFM release-equivalent research

- Same HFM period and real ticks, USD 100 equivalent to 10,000 USC.
- Release calendar/news/session/risk gates retained; notification disabled.
- Seven trades: four wins, three losses, net +0.19, PF 1.826, max cash
  drawdown 0.15.
- Bootstrap probability of non-positive result: 21.16%.
- Extra friction 0.03 per trade changes net to -0.02.
- This sample is too small for a profitability or live-readiness conclusion.

## HFM generated-tick multi-year evidence

- HFM `XAUUSDc`, 2023-01-01 through 2025-12-31, generated ticks with random
  execution delay.
- 130,420,315 ticks and 1,057,530 bars; `Test passed`.
- Ten trades: five wins, five losses, net +0.11, PF 1.262, max cash drawdown
  0.24.
- Annual net: -0.09 in 2023, -0.05 in 2024, and +0.25 in 2025.
- Bootstrap probability of non-positive result: 36.19%.
- Extra friction of 0.02 per trade changes net to -0.09.
- All closed-deal P/L reconciles exactly to the final balance change. The
  earlier six-trade extraction was incomplete because its log window omitted
  four earlier trades.
- This fails the stability gate and does not justify parameter retuning.

## v1.34 HFM regression identity

- All four HFM tester reruns used the v1.34 binary recorded in
  `SHA256SUMS.txt`; all reported `Test passed`.
- Both the historical 100 USC run and the corrected 525 USC value-equivalent
  run rejected all 11 candidates below minimum volume.
- The USD-equivalent tester used native `OrderCalcProfit`; the USC fallback had
  zero hits. The fallback formula itself was exercised only by the read-only
  v1.03 live preflight, not by a trade-capable real-account run.
- No claim of native USC backtest equivalence is made while `USDUSC` conversion
  history remains unavailable in the local tester.
