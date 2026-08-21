# Capital feasibility — HFM Gold Cent

## Broker facts checked on 2026-08-20

HFM's official pages specify the following for Gold on a Cent account:

- Symbol example: `XAUUSDc`.
- Account currency: USC.
- Gold contract size: 1 lot = 1 ounce.
- Minimum volume and increment: 0.01 lot.
- Gold spread advertised as low as 0.32 price units.

Sources:

- https://www.hfm.com/int/en/trading-accounts/cent-account
- https://www.hfm.com/int/en/trading-instruments/single-product?symbol=XAUUSD

## What 525 USC means

The corrected capital is 525 USC, equivalent to USD 5.25. At 0.10% risk, the
allowed loss is 0.525 USC, equivalent to USD 0.00525.

For HFM Cent Gold, 0.01 lot represents 0.01 ounce. A USD 1.00 stop therefore
risks approximately USD 0.01, or 1 USC. That is already 0.1905% of a 525 USC
account, nearly twice the configured target.

The EA requires the stop to be at least four current spreads from entry. Even
using HFM's advertised low spread of 0.32, the theoretical stop floor is 1.28.
At 0.01 lot this is approximately 1.28 USC, or 0.2438% of the account. Variable
spread and structural/ATR stops can make it larger. Even this optimistic floor
is 2.44 times the 0.10% target.

The corrected HFM value-equivalent test found raw volumes of
0.000495-0.001180 lot. At 0.01 lot, those setup stops imply approximately
4.449-10.606 USC risk, or 0.847%-2.020% of 525 USC.

## Consequence

The robot cannot both trade HFM Gold at 0.01 lot and preserve the configured
0.10% risk on a 525 USC balance. Forcing 0.01 lot would violate the risk model.

At the observed HFM setup distances, maintaining 0.10% risk would require
approximately 4,449-10,606 USC. The live read-only snapshot required about
2,537 USC. Capital is therefore a hard broker-granularity gate, not a parameter
that can be optimized away safely.

## Live HFM read-only preflight — 2026-08-13

A one-shot script with automated trading disabled ran on the HFM live account.
It confirmed USC, `XAUUSDc`, a 1-ounce contract, and 0.01 minimum/step volume.
At the observed spread 0.34 and M1 ATR 2.36571, the EA model's stop floor was
2.83886 price units.

For 0.01 lot, that distance corresponds to approximately 2.83886 USC risk, or
0.5407% of a 525 USC account. Preserving 0.10% risk would require about
2,838.86 USC under that snapshot. This is direct broker-spec evidence combined
with deterministic contract arithmetic, not a MetaQuotes stand-in estimate.

The v1.00 probe printed an incorrect capital pass because it ran before network
authorization and accepted a zero `OrderCalcProfit` result. That output is
explicitly rejected. Source v1.01 and later fail closed when calculated risk is
not positive. See `HFM_LIVE_PREFLIGHT_EVIDENCE.json`.

## Revalidated live preflight — 2026-08-20

Probe v1.03 compiled with zero errors and warnings and ran again with automated
trading disabled. It confirmed that `XAUUSDc` profit currency is USD while the
account currency is USC. `OrderCalcProfit` was still unavailable at immediate
startup, so the tightly constrained probe fallback converted USD P/L to USC at
100 cents per dollar.

At spread 0.36 and M1 ATR 2.11429, the model stop floor was 2.53714. Minimum-
lot risk was therefore 2.53714 USC, or 0.4833% of the corrected 525 USC capital.
The target 0.10% requires about 2,537.14 USC under that snapshot. The broker
checks passed, but the capital check and overall result correctly failed.

## Historical 100 USC HFM sizing test

The EA was tested on HFM `XAUUSDc` ticks from June through August 2026 with
random execution delay. Because HFM's local tester lacked 2026 `USDUSC`
conversion history, the test used USD 1.00 as the value equivalent of 100 USC
and disabled only the USC currency guard.

Across 17,210,479 ticks, 11 otherwise-valid setups reached position sizing.
Every one was rejected with `VOLUME_BELOW_MIN`. Requested raw volume ranged
from 0.000094 to 0.000225 lots, versus the broker minimum 0.01. Minimum-lot
risk was 4%-11% per candidate. No order or deal occurred.

At the configured 0.10% risk, those candidates imply roughly 4,000-11,000 USC
minimum equity. See `HFM_TESTER_SMALL_BALANCE_EVIDENCE.json`.

## Corrected 525 USC HFM sizing test

The same v1.34 binary was tested again for the corrected 525 USC capital. MT5
rounded a fractional USD 5.25 tester deposit to USD 5.00. To preserve exact
risk-money equivalence, the accepted run used USD 5.00 with 0.105% risk. Its
USD 0.00525 risk budget equals 0.525 USC, exactly 0.10% of 525 USC. The future
real profile remains pinned to 0.10%; 0.105% exists only in this tester proxy.

Across 17,210,479 ticks, all 11 valid candidates were again rejected with
`VOLUME_BELOW_MIN`. Raw volume was 0.000495-0.001180 lot. Forcing the 0.01
minimum would require approximately 0.847%-2.020% risk per setup. No order or
deal occurred and the balance remained unchanged.

The tester warned that 544 of 72,611 minute bars, or 0.7492%, had discarded or
mismatched real ticks and used generated ticks for those affected minutes.
This limitation is recorded in `HFM_TESTER_525_USC_EVIDENCE.json`; the run is
capital-safety evidence, not a profitability test or pure real-tick proof.
