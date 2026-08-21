#!/bin/sh
set -eu

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
src="${1:-$script_dir/AurumCent.mq5}"

test -f "$src"
grep -q 'BUILD_ALLOW_REAL_ACCOUNT = false' "$src"
grep -q 'ACCOUNT_TRADE_MODE_REAL' "$src"
grep -q 'InpAllowRealAccount.*= false' "$src"
grep -q 'InpAuthorizedRealLogin.*= 0' "$src"
grep -q 'REAL_ACCOUNT_LOGIN_NOT_AUTHORIZED' "$src"
grep -q 'HFM_VALIDATION_MANDATORY_ON_REAL' "$src"
grep -q 'CENT_CURRENCY_VALIDATION_MANDATORY_ON_REAL' "$src"
grep -q 'CALENDAR_FAIL_CLOSED_MANDATORY_ON_REAL' "$src"
grep -q 'RELEASE_PROFILE_REQUIRED_ON_REAL' "$src"
grep -q 'ValidateHfmCentEnvironment' "$src"
grep -q 'CalendarValueHistory' "$src"
grep -q 'OrderCalcProfit' "$src"
grep -q 'OrderCalcMargin' "$src"
grep -q 'OrderCheck' "$src"
grep -q 'check.retcode != 0' "$src"
grep -q 'SYMBOL_FILLING_FOK' "$src"
grep -q 'SYMBOL_TRADE_EXECUTION_MARKET' "$src"
grep -q 'DIRECTION_NOT_ALLOWED' "$src"
grep -Eq 'request\.sl[[:space:]]*=[[:space:]]*sl' "$src"
grep -Eq 'request\.tp[[:space:]]*=[[:space:]]*tp' "$src"
grep -q 'VOLUME_BELOW_MIN' "$src"
grep -q 'InpM15MinimumAdx.*= 30.0' "$src"
grep -q 'InpEnableAsiaSession.*= false' "$src"
grep -q 'InpUseSessionDirectionFilter.*= true' "$src"
grep -q 'SESSION_DIRECTION_FILTER' "$src"
grep -q 'InpNotificationOutboxEnabled.*= true' "$src"
grep -q 'FILE_COMMON' "$src"

if grep -Eqi 'api\.telegram\.org|bot[0-9]{8,}:[A-Za-z0-9_-]{20,}|WebRequest[[:space:]]*\(' "$src"; then
  echo "STATIC AUDIT FAILED: direct network call or embedded Telegram credential found"
  exit 1
fi

if grep -Eqi 'martingale|grid|averaging|recovery[ _-]?lot' "$src"; then
  echo "STATIC AUDIT FAILED: prohibited strategy term found in source"
  exit 1
fi

echo "STATIC AUDIT PASSED"
