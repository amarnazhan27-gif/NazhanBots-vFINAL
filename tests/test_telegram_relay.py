from __future__ import annotations

from contextlib import redirect_stdout
import io
from pathlib import Path
import tempfile
import unittest

import telegram_relay


class RelayOutboxTests(unittest.TestCase):
    def test_partial_record_waits_for_newline_and_deduplicates(self) -> None:
        complete = b"2026.08.20 10:00:00\tINIT_OK\tfirst\n"
        partial = b"2026.08.20 10:01:00\tORDER_OK\tsecond"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            outbox = root / "outbox.tsv"
            state = root / "state.json"
            outbox.write_bytes(complete + partial)

            with redirect_stdout(io.StringIO()):
                sent = telegram_relay.relay_once(outbox, state, "", "", True, 1.0)
            self.assertEqual(sent, 1)
            self.assertEqual(telegram_relay.load_offset(state), len(complete))

            with redirect_stdout(io.StringIO()):
                sent = telegram_relay.relay_once(outbox, state, "", "", True, 1.0)
            self.assertEqual(sent, 0)
            self.assertEqual(telegram_relay.load_offset(state), len(complete))

            with outbox.open("ab") as target:
                target.write(b"\n")
            with redirect_stdout(io.StringIO()):
                sent = telegram_relay.relay_once(outbox, state, "", "", True, 1.0)
            self.assertEqual(sent, 1)
            self.assertEqual(telegram_relay.load_offset(state), outbox.stat().st_size)

            with redirect_stdout(io.StringIO()):
                sent = telegram_relay.relay_once(outbox, state, "", "", True, 1.0)
            self.assertEqual(sent, 0)


if __name__ == "__main__":
    unittest.main()
