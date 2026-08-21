# AURUM

AURUM is an MT5 research EA for XAUUSD Cent. It combines higher-timeframe
context with M1 closed-bar entries, then filters each setup by session, market
regime, and risk conditions.

## Current status

This is a demo and research build. It is not ready for real funds. The shipped
build has real-account support disabled, and that lock stays in place until the
capital, robustness, HFM real-tick, and forward-demo gates are met.

The most important practical result is simple: with 525 USC, a 0.10% risk target
does not meet HFM's 0.01-lot minimum for the observed Gold setups. The EA should
skip those entries with `VOLUME_BELOW_MIN`; forcing the minimum lot would break
the risk limit.

## Start here

| File | Purpose |
| --- | --- |
| `src/AurumCent.mq5` | Main M1 research EA. |
| `src/HfmPreflight.mq5` | Read-only check for HFM broker conditions and minimum-lot risk. |
| `profiles/AurumCent.set` | Default parameter set. |

Before an HFM test, run `src/HfmPreflight.ex5`. It cannot place, modify, or close a
trade. Setup details are in `docs/preflight.md`.

## Working rules

- Use the broker's Gold symbol on M1.
- Default risk is 0.10% equity, with at most one new position per broker day.
- Asia is disabled by default. The release profile allows London BUY and New
  York SELL when the M15 ADX filter is met.
- Session times follow the broker server. Verify DST and server offset before
  interpreting any session result.
- News protection uses the MT5 economic calendar and fails closed outside the
  tester when data is unavailable.
- Notifications are written to a Common Files outbox. Credentials are never
  stored in the EA; see `docs/telegram.md`.

## Validate a change

1. Run `./scripts/audit-ea.sh`.
2. Run `./scripts/audit-preflight.sh` when changing the preflight script.
3. Compile in MetaEditor and record the actual result.
4. Run M1 tests with real ticks and execution delay where the data is available.
5. Keep static checks, compile results, tester runs, and forward-demo evidence
   separate. One does not substitute for another.

## Evidence, not a profit claim

The 2022-2025 generated-tick stand-in regression was positive: 88 closed
trades, 50% wins, PF 1.385, and +USD 150.97 from a USD 10,000 account. It is
reproducibility evidence only, not HFM Cent performance evidence.

The broader record is less favorable. The untouched 2015-2021 period and the
2021 real-tick run were negative. The combined 2021-2025 real-tick PF was 1.202,
and an extra 1.00 cost per trade removed the profit. The HFM 2026 sample is also
too small. For that reason, the status remains `NOT READY FOR REAL`.

Read `docs/research.md`, `docs/validation.md`, `docs/capital.md`, and
`evidence/real-ticks.json` for the numbers, assumptions, and remaining gates.

## Repository layout

| Folder | Contents |
| --- | --- |
| `src/` | EA, preflight source, and compiled builds. |
| `profiles/` | Default, HFM, and MetaQuotes tester profiles. |
| `docs/` | Strategy, setup, research, and validation notes. |
| `evidence/` | Build logs and recorded test evidence. |
| `scripts/` | Audits, relay, and research utilities. |
| `checksums/` | Source and binary integrity records. |

Profile names stay short because the broker or environment is already identified
by its folder. Build logs preserve original compiler paths inside the file so the
record remains traceable.

Contributions should improve safety, reproducibility, or evidence quality. A
better in-sample curve alone is not enough to change the strategy. See
`CONTRIBUTING.md` for the review checklist.
