#!/usr/bin/env python3
"""Relay AURUM TSV events to Telegram without storing credentials in MQL5."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import time
from urllib import error, parse, request


def send_message(token: str, chat_id: str, text: str, timeout: float) -> None:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = parse.urlencode({"chat_id": chat_id, "text": text}).encode("utf-8")
    req = request.Request(url, data=payload, method="POST")
    try:
        with request.urlopen(req, timeout=timeout) as response:
            if response.status != 200:
                raise RuntimeError(f"Telegram returned HTTP {response.status}")
            try:
                result = json.loads(response.read().decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise RuntimeError("Telegram returned an invalid response") from exc
            if not result.get("ok"):
                raise RuntimeError("Telegram rejected the message")
    except error.HTTPError as exc:
        raise RuntimeError(f"Telegram returned HTTP {exc.code}") from exc
    except error.URLError as exc:
        raise RuntimeError(f"Telegram connection failed: {exc.reason}") from exc


def load_offset(state_path: Path) -> int:
    try:
        data = json.loads(state_path.read_text(encoding="utf-8"))
        return max(0, int(data.get("offset", 0)))
    except (FileNotFoundError, ValueError, TypeError, json.JSONDecodeError):
        return 0


def save_offset(state_path: Path, offset: int) -> None:
    state_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = state_path.with_suffix(state_path.suffix + ".tmp")
    temporary.write_text(json.dumps({"offset": offset}), encoding="utf-8")
    temporary.replace(state_path)


def relay_once(outbox: Path, state_path: Path, token: str, chat_id: str,
               dry_run: bool, timeout: float) -> int:
    if not outbox.exists():
        return 0
    offset = load_offset(state_path)
    size = outbox.stat().st_size
    if offset > size:
        offset = 0
    sent = 0
    with outbox.open("r", encoding="utf-8", errors="replace") as source:
        source.seek(offset)
        while True:
            start = source.tell()
            line = source.readline()
            if not line:
                break
            # The EA and relay may access the shared outbox concurrently. Do
            # not send or advance past a record until FileWrite completed its
            # newline; the next poll will retry the same byte offset.
            if not line.endswith(("\n", "\r")):
                source.seek(start)
                break
            fields = line.rstrip("\r\n").split("\t", 2)
            if len(fields) != 3:
                save_offset(state_path, source.tell())
                continue
            timestamp, event_name, message = fields
            text = f"AURUM | {event_name}\n{timestamp}\n{message}"
            if dry_run:
                print(text)
            else:
                try:
                    send_message(token, chat_id, text, timeout)
                except RuntimeError:
                    source.seek(start)
                    raise
            save_offset(state_path, source.tell())
            sent += 1
    return sent


def main() -> int:
    parser = argparse.ArgumentParser(description="Relay AURUM MT5 notifications to Telegram")
    parser.add_argument("--outbox", default=os.environ.get("AURUM_TELEGRAM_OUTBOX"))
    parser.add_argument("--state", default=os.environ.get("AURUM_TELEGRAM_STATE", ".aurum_telegram_state.json"))
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--poll-seconds", type=float, default=2.0)
    parser.add_argument("--timeout", type=float, default=10.0)
    args = parser.parse_args()

    if not args.outbox:
        parser.error("set --outbox or AURUM_TELEGRAM_OUTBOX")
    token = os.environ.get("AURUM_TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("AURUM_TELEGRAM_CHAT_ID", "")
    if not args.dry_run and (not token or not chat_id):
        parser.error("set AURUM_TELEGRAM_BOT_TOKEN and AURUM_TELEGRAM_CHAT_ID")

    outbox = Path(args.outbox).expanduser().resolve()
    state_path = Path(args.state).expanduser().resolve()
    normal_delay = max(0.5, args.poll_seconds)
    retry_delay = normal_delay
    while True:
        try:
            relay_once(outbox, state_path, token, chat_id, args.dry_run, args.timeout)
            retry_delay = normal_delay
        except RuntimeError as exc:
            print(str(exc), file=sys.stderr)
            if args.once:
                return 1
            time.sleep(retry_delay)
            retry_delay = min(60.0, retry_delay * 2.0)
            continue
        if args.once:
            return 0
        time.sleep(normal_delay)


if __name__ == "__main__":
    raise SystemExit(main())
