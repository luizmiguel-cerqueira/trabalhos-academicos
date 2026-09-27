from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .i18n import I18n
from .native_api import NativeAPI, KIND_LIST, KIND_QUEUE, KIND_STACK


@dataclass
class HistoryEntry:
    sequence: int
    kind: int
    action: int
    value: int
    quantity: int


class AppController:
    def __init__(self, language: str = "pt") -> None:
        self.i18n = I18n(language)
        self.api: NativeAPI | None = None
        self.data = {
            KIND_QUEUE: [],
            KIND_STACK: [],
            KIND_LIST: [],
        }
        self.history: list[HistoryEntry] = []
        self.history_page = 0
        self.status_message = self.i18n.text("status_ready")
        self.last_error = ""
        self.page_size = 50
        self._load_native()

    def _load_native(self) -> None:
        try:
            self.api = NativeAPI()
            self.refresh_all()
            total = self.history_count()
            self.history_page = max(0, (total + self.page_size - 1) // self.page_size - 1)
            self.refresh_history()
            self.status_message = self.i18n.text("status_ready")
        except Exception as exc:  # pragma: no cover - UI-level error handling
            self.api = None
            self.status_message = self.i18n.text("status_error")
            self.last_error = str(exc)

    def is_ready(self) -> bool:
        return self.api is not None

    def refresh_all(self) -> None:
        if not self.api:
            return
        for kind in (KIND_QUEUE, KIND_STACK, KIND_LIST):
            status, values, _ = self.api.copy_values(kind)
            if status == 0:
                self.data[kind] = values
            else:
                self.data[kind] = []
        self.refresh_history()

    def refresh_history(self) -> None:
        if not self.api:
            return
        status, count = self.api.log_count()
        if status != 0:
            self.history = []
            return

        start_index = self.history_page * self.page_size
        status, records = self.api.log_read(start_index, self.page_size)
        if status == 0:
            self.history = [
                HistoryEntry(
                    sequence=item["sequence"],
                    kind=item["kind"],
                    action=item["action"],
                    value=item["value"],
                    quantity=item["quantity"],
                )
                for item in records
            ]
        else:
            self.history = []

    def set_language(self, language: str) -> None:
        self.i18n.language = language

    def handle_insert(self, kind: int, value: int) -> str:
        if not self.api:
            return self.i18n.text("error_dll")
        try:
            status = self.api.insert(kind, value)
            if status == 0:
                self.status_message = self.i18n.text("status_ready")
                self.refresh_all()
                return "ok"
            return self._status_to_message(status)
        except Exception as exc:  # pragma: no cover - UI-level handling
            self.last_error = str(exc)
            return self._status_to_message(999)

    def handle_remove_first(self, kind: int) -> str:
        if not self.api:
            return self.i18n.text("error_dll")
        status, _ = self.api.remove_first(kind)
        if status == 0:
            self.refresh_all()
            return "ok"
        return self._status_to_message(status)

    def handle_remove_value(self, kind: int, value: int) -> str:
        if not self.api:
            return self.i18n.text("error_dll")
        status = self.api.remove_value(kind, value)
        if status == 0:
            self.refresh_all()
            return "ok"
        return self._status_to_message(status)

    def handle_clear(self, kind: int) -> str:
        if not self.api:
            return self.i18n.text("error_dll")
        status, _ = self.api.clear(kind)
        if status == 0:
            self.refresh_all()
            return "ok"
        return self._status_to_message(status)

    def _status_to_message(self, status: int) -> str:
        mapping = {
            0: self.i18n.text("status_ready"),
            1: "DS_INVALID_ARGUMENT",
            2: self.i18n.text("full_state"),
            3: "DS_EMPTY",
            4: "DS_NOT_FOUND",
            5: "DS_OUT_OF_MEMORY",
            6: "DS_BUFFER_TOO_SMALL",
            7: "DS_UNSUPPORTED_OPERATION",
            8: "DS_OUT_OF_RANGE",
            999: self.last_error or self.i18n.text("status_error"),
        }
        return mapping.get(status, self.i18n.text("status_error"))

    def get_tab_values(self, kind: int) -> list[int]:
        return list(self.data.get(kind, []))

    def history_count(self) -> int:
        if not self.api:
            return 0
        status, count = self.api.log_count()
        return 0 if status != 0 else int(count)

    def next_history_page(self) -> None:
        total = self.history_count()
        pages = max(1, (total + self.page_size - 1) // self.page_size)
        if self.history_page < pages - 1:
            self.history_page += 1
            self.refresh_history()

    def prev_history_page(self) -> None:
        if self.history_page > 0:
            self.history_page -= 1
            self.refresh_history()

    def set_history_page(self, index: int) -> None:
        self.history_page = max(0, index)
        self.refresh_history()
