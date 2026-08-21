# Telegram notification setup

The EA never stores a Telegram bot token or chat identifier. It appends selected
events to the MetaTrader Common Files outbox. `scripts/telegram_relay.py` reads that
file and sends messages with credentials supplied only through environment
variables.

## Security first

Revoke the bot token that was pasted into chat and create a replacement with
BotFather. Do not put the replacement in `.mq5`, `.set`, `.ini`, shell history,
screenshots, or Git.

## Configuration

1. Attach EA v1.34. Keep `InpNotificationOutboxEnabled=true`.
2. Locate the MT5 Common Files folder. The EA writes:
   `AURUM_CENT_ADAPTIVE_M1_telegram_outbox.tsv`.
3. Provide the new bot token, target chat, and absolute outbox path to a process
   manager or a protected environment file:

   - `AURUM_TELEGRAM_BOT_TOKEN`
   - `AURUM_TELEGRAM_CHAT_ID`
   - `AURUM_TELEGRAM_OUTBOX`

4. Run `python3 scripts/telegram_relay.py --once --dry-run` first. Then run
   `python3 scripts/telegram_relay.py` under a supervised service.

The relay records its byte offset in `.aurum_telegram_state.json`. Failed sends
are retried without advancing the offset and with exponential backoff. A final
outbox record is not sent until its newline exists, so concurrent EA writes are
not consumed halfway. Network calls never block `OnTick`.

Local validation covers Python compilation, a two-event dry run, replay
deduplication, and an interrupted final-record write. Live Telegram delivery is
still a separate gate because credentials are intentionally not embedded here.
