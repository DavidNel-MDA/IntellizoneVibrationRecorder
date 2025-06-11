import threading
import can
import copy
import json
import datetime
import os
from config import *
from message_parser import parse_message


class DailyRotatingLogger:
    """A logger that writes to a new file each day.

    The logger writes log entries as JSON objects to a file named after the
    current date in the format %Y-%m-%d.jsonl. Each log entry is a single
    line in the file, with the following structure:

        {
            "timestamp": "<ISO 8601 formatted timestamp>",
            "changes": <dictionary of changes>
        }

    The logger rotates the file every day, so the log entries for a given
    day are all stored in one file.
    """

    def __init__(self, directory="logs"):
        """Initialize the logger.

        Args:
            directory: The directory where the log files will be stored.
        """
        self.directory = directory
        os.makedirs(directory, exist_ok=True)
        self.current_date = self._get_today()
        self.file = self._open_file(self.current_date)

    def _get_today(self) -> str:
        """Return the current date as a string in the format %Y-%m-%d"""
        return datetime.date.today().isoformat()

    def _open_file(self, date_str: str):
        """Open a new file for the given date."""
        path = os.path.join(self.directory, f"{date_str}.jsonl")
        return open(path, "a", buffering=1)  # line-buffered

    def _rotate_if_needed(self) -> None:
        """Close and reopen the file if the date has changed."""
        today = self._get_today()
        if today != self.current_date:
            self.file.close()
            self.current_date = today
            self.file = self._open_file(today)

    def log(self, data: dict) -> None:
        """Log a new entry to the current file.

        Args:
            data: A dictionary of changes to log.
        """
        self._rotate_if_needed()
        timestamp = datetime.datetime.now().isoformat()  # local time
        entry = {
            "timestamp": timestamp,
            "changes": data
        }
        json.dump(entry, self.file)
        self.file.write("\n")

    def close(self) -> None:
        """Close the file."""
        if self.file:
            self.file.close()


class StatusListener(can.Listener):
    def __init__(
        self,
        node_id: int,
        expected_reply: int,
        module_type: int,
        source_module: int = 0x0,
        source_node: int = 0x0
    ) -> None:
        self.expected_arbitration_id = (
            (expected_reply << 16) |
            (source_module << 12) |
            (source_node << 8) |
            (module_type << 4) |
            node_id
        )
        self.received_event = threading.Event()
        self.status_store = {}
        self.last_printed_store = {}
        self.lock = threading.Lock()
        self.logger = DailyRotatingLogger()

    def on_message_received(self, msg: can.Message) -> None:
        message_type = (msg.arbitration_id >> 16) & 0x1FFF
        # print(f"Received status message: {msg}")
        if message_type == CONTROLLER_MESSAGE_TYPE["Device_Status_Report"]:
            data_bytes = list(msg.data)

            with self.lock:
                parse_message(data_bytes, self.status_store)

                if self.status_store != self.last_printed_store:
                    diff = {}
                    for section, values in self.status_store.items():
                        old_values = self.last_printed_store.get(section, {})
                        section_diff = {
                            k: v for k, v in values.items() if old_values.get(k) != v
                        }
                        if section_diff:
                            diff[section] = section_diff

                    if diff:
                        self.logger.log(diff)

                    self.last_printed_store = copy.deepcopy(self.status_store)

            self.received_event.set()

    def close_logger(self):
        self.logger.close()
