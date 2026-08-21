# Roadmap

AURUM advances by evidence gates, not by adding trading rules until a backtest
curve looks better.

## Current release

`v1.34-demo` is a research and forward-demo candidate. Real-account support is
disabled. With 525 USC, observed setups remain below HFM's minimum tradable
volume at the 0.10% risk target.

## Required gates

| Gate | Acceptance condition | Status |
| --- | --- | --- |
| HFM session mapping | Server offset and DST behavior documented across transitions | Open |
| HFM real-tick walk-forward | Fixed rules tested on multiple independent periods | Open |
| Friction robustness | Positive result survives realistic spread, commission, and delay | Failed on current combined sample |
| Capital feasibility | Broker minimum volume fits the 0.10% risk budget | Failed at 525 USC |
| Forward demo | Multi-month operation without safety or execution defects | Open |
| Live review | Independent review of code, broker conditions, and evidence | Open |

## Next milestone

1. Verify HFM server-session and DST mapping.
2. Collect independent HFM M1 real-tick periods without retuning the rules.
3. Run the fixed release profile through friction and execution-delay stress.
4. Complete a multi-month HFM Cent forward demo.
5. Reassess capital feasibility using current broker specifications.

## Out of scope

- Guaranteed daily or monthly profit.
- Martingale, grid, averaging, recovery sizing, or forced minimum volume.
- Enabling real accounts before every gate above has passed.
- Treating repository popularity, a single screenshot, or one profitable test as
  live-readiness evidence.
