#!/bin/sh
set -eu

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
src="${1:-$script_dir/../src/HfmPreflight.mq5}"

test -f "$src"
grep -q 'OrderCalcProfit' "$src"
grep -q 'SYMBOL_TRADE_CONTRACT_SIZE' "$src"
grep -q 'SYMBOL_VOLUME_MIN' "$src"
grep -q 'REQUIRED_EQUITY_FOR_TARGET_RISK' "$src"

if grep -Eq 'OrderSend|TRADE_ACTION_|CTrade|\.Buy\(|\.Sell\(|PositionClose|OrderDelete' "$src"; then
  echo "PREFLIGHT AUDIT FAILED: transaction API found"
  exit 1
fi

echo "PREFLIGHT STATIC AUDIT PASSED: no transaction API"
