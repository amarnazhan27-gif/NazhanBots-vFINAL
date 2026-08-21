#!/usr/bin/env python3
"""Reproducible Monte Carlo and friction stress for AURUM tester logs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import random
import re
from statistics import mean, median


DEAL_RE = re.compile(
    r"^\S+\s+\d+\s+(?P<wall>\d{2}:\d{2}:\d{2}\.\d{3}).*?"
    r"(?P<market>20\d{2}\.\d{2}\.\d{2}\s+\d{2}:\d{2}:\d{2}).*?"
    r"AURUM\|DEAL_AUDIT\|.*?\|entry=1\|.*?\|net=(?P<net>-?\d+(?:\.\d+)?)\|"
)


def decode_log(path: Path) -> str:
    raw = path.read_bytes()
    if raw.startswith((b"\xff\xfe", b"\xfe\xff")) or raw.count(b"\x00") > len(raw) // 4:
        return raw.decode("utf-16", errors="replace")
    return raw.decode("utf-8-sig", errors="replace")


def in_wall_windows(wall: str, windows: list[tuple[str, str]]) -> bool:
    return any(start <= wall <= end for start, end in windows)


def extract_returns(
    text: str,
    wall_start: str | None,
    wall_end: str | None,
    wall_windows: list[tuple[str, str]],
) -> list[float]:
    returns: list[float] = []
    for line in text.splitlines():
        match = DEAL_RE.search(line)
        if not match:
            continue
        wall = match.group("wall")
        if wall_start and wall < wall_start:
            continue
        if wall_end and wall > wall_end:
            continue
        if wall_windows and not in_wall_windows(wall, wall_windows):
            continue
        returns.append(float(match.group("net")))
    return returns


def parse_wall_window(value: str) -> tuple[str, str]:
    try:
        start, end = (item.strip() for item in value.split(",", 1))
    except ValueError as exc:
        raise argparse.ArgumentTypeError("use START,END") from exc
    timestamp = re.compile(r"^\d{2}:\d{2}:\d{2}(?:\.\d{3})?$")
    if not timestamp.fullmatch(start) or not timestamp.fullmatch(end):
        raise argparse.ArgumentTypeError("timestamps must be HH:MM:SS or HH:MM:SS.mmm")
    if "." not in start:
        start += ".000"
    if "." not in end:
        end += ".999"
    if start > end:
        raise argparse.ArgumentTypeError("START must not be after END")
    return start, end


def max_drawdown(values: list[float]) -> float:
    equity = peak = drawdown = 0.0
    for value in values:
        equity += value
        peak = max(peak, equity)
        drawdown = max(drawdown, peak - equity)
    return drawdown


def percentile(sorted_values: list[float], fraction: float) -> float:
    if not sorted_values:
        return 0.0
    position = (len(sorted_values) - 1) * fraction
    lower = int(position)
    upper = min(lower + 1, len(sorted_values) - 1)
    weight = position - lower
    return sorted_values[lower] * (1.0 - weight) + sorted_values[upper] * weight


def profit_factor(values: list[float]) -> float | None:
    gross_profit = sum(value for value in values if value > 0)
    gross_loss = -sum(value for value in values if value < 0)
    return gross_profit / gross_loss if gross_loss > 0 else None


def monte_carlo(values: list[float], simulations: int, seed: int) -> dict[str, object]:
    rng = random.Random(seed)
    shuffled_dd: list[float] = []
    bootstrap_dd: list[float] = []
    bootstrap_net: list[float] = []
    count = len(values)
    for _ in range(simulations):
        shuffled = values.copy()
        rng.shuffle(shuffled)
        shuffled_dd.append(max_drawdown(shuffled))
        sampled = [values[rng.randrange(count)] for _ in range(count)]
        bootstrap_dd.append(max_drawdown(sampled))
        bootstrap_net.append(sum(sampled))
    shuffled_dd.sort()
    bootstrap_dd.sort()
    bootstrap_net.sort()
    return {
        "simulations": simulations,
        "seed": seed,
        "shuffle_drawdown": {
            "median": round(percentile(shuffled_dd, 0.50), 4),
            "p95": round(percentile(shuffled_dd, 0.95), 4),
            "p99": round(percentile(shuffled_dd, 0.99), 4),
        },
        "bootstrap_drawdown": {
            "median": round(percentile(bootstrap_dd, 0.50), 4),
            "p95": round(percentile(bootstrap_dd, 0.95), 4),
            "p99": round(percentile(bootstrap_dd, 0.99), 4),
        },
        "bootstrap_net": {
            "median": round(percentile(bootstrap_net, 0.50), 4),
            "p05": round(percentile(bootstrap_net, 0.05), 4),
            "p01": round(percentile(bootstrap_net, 0.01), 4),
            "probability_non_positive": round(sum(v <= 0 for v in bootstrap_net) / simulations, 6),
        },
    }


def friction_stress(values: list[float], costs: list[float]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for cost in costs:
        stressed = [value - cost for value in values]
        output.append({
            "extra_cost_per_trade": cost,
            "net": round(sum(stressed), 4),
            "profit_factor": None if profit_factor(stressed) is None else round(profit_factor(stressed) or 0.0, 4),
            "max_drawdown": round(max_drawdown(stressed), 4),
        })
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("log", type=Path)
    parser.add_argument("--wall-start")
    parser.add_argument("--wall-end")
    parser.add_argument(
        "--wall-window",
        action="append",
        default=[],
        type=parse_wall_window,
        metavar="START,END",
        help="include one wall-clock range; repeat for disjoint validated runs",
    )
    parser.add_argument("--simulations", type=int, default=100_000)
    parser.add_argument("--seed", type=int, default=260813)
    parser.add_argument("--costs", default="0,0.25,0.5,1,1.5,2")
    args = parser.parse_args()
    if args.simulations < 1:
        parser.error("--simulations must be positive")
    if args.wall_window and (args.wall_start or args.wall_end):
        parser.error("--wall-window cannot be combined with --wall-start/--wall-end")
    values = extract_returns(
        decode_log(args.log), args.wall_start, args.wall_end, args.wall_window
    )
    if len(values) < 2:
        parser.error(f"only {len(values)} closed trades matched")
    costs = [float(value) for value in args.costs.split(",")]
    report = {
        "selection": {
            "wall_start": args.wall_start,
            "wall_end": args.wall_end,
            "wall_windows": args.wall_window,
        },
        "sample": {
            "trades": len(values),
            "wins": sum(value > 0 for value in values),
            "losses": sum(value < 0 for value in values),
            "net": round(sum(values), 4),
            "average": round(mean(values), 4),
            "median": round(median(values), 4),
            "profit_factor": round(profit_factor(values) or 0.0, 4),
            "max_drawdown": round(max_drawdown(values), 4),
        },
        "monte_carlo": monte_carlo(values, args.simulations, args.seed),
        "friction_stress": friction_stress(values, costs),
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
