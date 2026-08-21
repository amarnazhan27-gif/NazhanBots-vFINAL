# AURUM_CENT_ADAPTIVE_M1_DEMO

Adaptive XAUUSD Cent v1.34 research candidate for MT5. H1 supplies direction, M15 regime,
M5 setup, and M1 closed-bar entry timing. Session and historical month context
adjust score/target but cannot override safety vetoes.

## Project status

This repository is a guarded research and demo-validation project. It is not
ready for real funds. The released source is compiled with real-account support
disabled. Historical tests, compilation, and static checks are kept separate
from forward-demo and live-readiness evidence.

## Important

- The distributed preset is locked against real accounts.
- Real-account initialization requires three simultaneous gates: build support,
  `InpAllowRealAccount=true`, and an exact `InpAuthorizedRealLogin` match.
- Build support is compile-time disabled in v1.34 because the capital,
  robustness, and forward-demo gates have not passed.
- A real account also requires HFM identity, USC, `XAUUSDc`, 1-ounce contract
  size, and 0.01 minimum/step checks to pass at runtime.
- Default risk is 0.10% equity.
- Default maximum frequency is one new position per broker day. The 2022-2025
  stand-in regression produced only 88 trades, about 22 per year; the signal
  filters do not force a daily trade.
- With 525.00 USC, the expected safe behavior is still usually
  `AURUM|NO_TRADE|reason=VOLUME_BELOW_MIN`. This is not a malfunction.
- Attach only to the broker's Gold symbol on M1.
- Session hours use broker server time and require broker/DST verification.
- High-impact USD events use the MT5 economic calendar and fail closed when the
  calendar is unavailable outside the tester.
- The evidence-selected default disables Asia, requires M15 ADX >= 30, permits
  London BUY and New York SELL only. This reduced activity deliberately.
- Telegram events use a Common Files outbox and an external relay. No bot token
  or chat identifier is stored in the EA. See `TELEGRAM_SETUP.md`.

## Validation order

1. Run `./static_audit.sh`.
2. Compile in MetaEditor and inspect the decoded compile log.
3. Test on M1 with `Every tick based on real ticks` and execution delay. This
   repository now includes completed MetaQuotes real-tick evidence for 2021
   through 2025, HFM real-tick evidence for the available 2026 cache, and an
   HFM generated-tick 2023-2025 test. Longer independent HFM real-tick and
   forward-demo evidence are still required.
4. Review `AURUM|...` journal lines for init, veto, sizing and execution evidence.
5. Complete the HFM forward-demo acceptance gates before supplying an authorized
   real login. The included preset intentionally leaves both real switches off.

See `CAPITAL_FEASIBILITY.md`: 525 USC is still too small for the configured 0.10%
Gold risk under HFM's 0.01-lot minimum. The EA correctly skips those entries.
An HFM real-tick diagnostic confirmed 11 out of 11 sizing candidates were
rejected; required minimum-lot risk was approximately 0.847%-2.020% of the
corrected 525 USC capital per candidate.

Before any HFM test, run the read-only `AURUM_HFM_CENT_PREFLIGHT.ex5` script.
It has no transaction API and reports broker compatibility plus the actual
minimum-lot risk. Instructions are in `HFM_PREFLIGHT_INSTRUCTIONS.md`.

## Research status

The generated-tick MetaQuotes test from 2022 through 2025 was positive in each
calendar year after applying the default session/direction filter. Combined
results were 88 closed trades, 50% wins, profit factor 1.385, and +USD 150.97
from a USD 10,000 stand-in account. This is reproducibility evidence, not HFM
Cent performance evidence. See `RESEARCH_RESULTS.md`.

Increasing the cap to two trades per day produced 92 trades and a slightly
higher ending balance in the same in-sample environment, but worsened some
losing months. It was rejected as the release default. ADX 28, 30, and 32 plus
random execution delay were also checked; see `RESEARCH_RESULTS.md`.

The untouched 2015-2021 generated-tick period and the 2021 real-tick run were
negative. Separate v1.34 random-delay real-tick runs for 2022-2025 were positive,
but the combined 2021-2025 PF was only 1.202 and an extra 1.00 cost per trade erased
the profit. Current status is therefore `NOT READY FOR REAL`. The real-account
lock must remain closed.

Available HFM 2026 real ticks produced seven release-equivalent trades with
PF 1.826 and +0.19%, but the sample is too small and its bootstrap non-positive
probability is 21.16%. It does not override the `NOT READY FOR REAL` status.

HFM generated ticks for 2023-2025 produced only ten trades and +0.11%, with
negative 2023 and 2024 results. Bootstrap probability of non-positive net was
36.19%, and 0.02 extra cost per trade erased the result. This independently
fails the stability gate and reinforces `NOT READY FOR REAL`.

Machine-readable run identity, tester-log checksum, yearly metrics, and the
remaining blocking gates are recorded in `REAL_TICK_EVIDENCE.json`.

## Repository contents

- `AURUM_CENT_ADAPTIVE_M1_DEMO.mq5`: guarded M1 research EA.
- `AURUM_HFM_CENT_PREFLIGHT.mq5`: read-only HFM broker and capital probe.
- `*.ini` and `*.set`: reproducible tester configurations and parameter sets.
- `*_EVIDENCE.json`, `VALIDATION.md`, and `RESEARCH_RESULTS.md`: captured
  evidence and its limitations.
- `telegram_relay.py`: optional outbox relay; credentials are read only from
  protected environment variables.

## Collaboration

Development is welcome when it improves reproducibility, safety, broker
compatibility, or evidence quality. Strategy changes must start from a stated
hypothesis and pass out-of-sample validation; a better in-sample curve is not a
reason to merge a rule. See `CONTRIBUTING.md` for the required checks and pull
request format.
