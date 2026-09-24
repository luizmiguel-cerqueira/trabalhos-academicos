from __future__ import annotations

import ctypes as ct
import os
import sys
from pathlib import Path
from typing import Optional, Sequence


DS_OK = 0
DS_INVALID_ARGUMENT = 1
DS_FULL = 2
DS_EMPTY = 3
DS_NOT_FOUND = 4
DS_OUT_OF_MEMORY = 5
DS_BUFFER_TOO_SMALL = 6
DS_UNSUPPORTED_OPERATION = 7
DS_OUT_OF_RANGE = 8

KIND_QUEUE = 1
KIND_STACK = 2
KIND_LIST = 3

ACTION_INSERT = 1
ACTION_REMOVE_FIRST = 2
ACTION_REMOVE_BY_VALUE = 3
ACTION_CLEAR = 4


class NativeAPIError(RuntimeError):
    pass


class NativeAPI:
    def __init__(self) -> None:
        self._lib: Optional[ct.CDLL] = None
        self._handle: Optional[int] = None
        self._load()

    @staticmethod
    def _candidate_dll_paths() -> list[Path]:
        project_root = Path(__file__).resolve().parents[1]
        roots: list[Path] = [
            project_root,
            project_root / "native" / "bin" / "x64",
        ]

        if getattr(sys, "frozen", False):
            if getattr(sys, "_MEIPASS", None):
                roots.append(Path(sys._MEIPASS))
            if getattr(sys, "executable", None):
                roots.append(Path(sys.executable).resolve().parent)
        else:
            roots.append(Path.cwd())

        candidates: list[Path] = []
        seen: set[Path] = set()
        for root in roots:
            for relative_name in (
                "native/bin/x64/datastructures.dll",
                "datastructures.dll",
                "libdatastructures.dll",
            ):
                path = (root / relative_name).resolve() if root else Path(relative_name)
                if path not in seen:
                    seen.add(path)
                    candidates.append(path)
        return candidates

    @staticmethod
    def _dll_path() -> Path:
        for dll_path in NativeAPI._candidate_dll_paths():
            if dll_path.exists():
                return dll_path
        searched = ", ".join(str(path) for path in NativeAPI._candidate_dll_paths())
        raise NativeAPIError(
            "DLL not found. Search locations: "
            f"{searched}. Build the native library before launching the app."
        )

    def _load(self) -> None:
        path = self._dll_path()
        try:
            if os.name == "nt" and str(path.parent) not in os.environ.get("PATH", ""):
                os.add_dll_directory(str(path.parent))
            lib = ct.CDLL(str(path))
        except OSError as exc:
            raise NativeAPIError(f"Could not load DLL from {path}: {exc}") from exc

        lib.ds_api_version.restype = ct.c_uint32

        lib.ds_create.argtypes = [ct.POINTER(ct.c_void_p)]
        lib.ds_create.restype = ct.c_int32

        lib.ds_destroy.argtypes = [ct.c_void_p]
        lib.ds_destroy.restype = None

        lib.ds_capacity.restype = ct.c_uint32

        lib.ds_insert.argtypes = [ct.c_void_p, ct.c_int32, ct.c_int32]
        lib.ds_insert.restype = ct.c_int32

        lib.ds_remove_first.argtypes = [ct.c_void_p, ct.c_int32, ct.POINTER(ct.c_int32)]
        lib.ds_remove_first.restype = ct.c_int32

        lib.ds_remove_value.argtypes = [ct.c_void_p, ct.c_int32, ct.c_int32]
        lib.ds_remove_value.restype = ct.c_int32

        lib.ds_clear.argtypes = [ct.c_void_p, ct.c_int32, ct.POINTER(ct.c_uint32)]
        lib.ds_clear.restype = ct.c_int32

        lib.ds_copy_values.argtypes = [
            ct.c_void_p,
            ct.c_int32,
            ct.POINTER(ct.c_int32),
            ct.c_uint32,
            ct.POINTER(ct.c_uint32),
        ]
        lib.ds_copy_values.restype = ct.c_int32

        lib.ds_log_count.argtypes = [ct.c_void_p, ct.POINTER(ct.c_uint64)]
        lib.ds_log_count.restype = ct.c_int32

        lib.ds_log_read.argtypes = [
            ct.c_void_p,
            ct.c_uint64,
            ct.c_uint32,
            ct.POINTER(ct.c_uint64),
            ct.POINTER(ct.c_int32),
            ct.POINTER(ct.c_int32),
            ct.POINTER(ct.c_int32),
            ct.POINTER(ct.c_uint32),
            ct.POINTER(ct.c_uint32),
        ]
        lib.ds_log_read.restype = ct.c_int32

        version = lib.ds_api_version()
        if version != 1:
            raise NativeAPIError(f"Unsupported DLL ABI version: {version}; expected 1.")

        handle = ct.c_void_p()
        status = lib.ds_create(ct.byref(handle))
        if status != DS_OK:
            raise NativeAPIError(f"Could not create native context. Status: {status}")

        capacity = lib.ds_capacity()
        if capacity != 10:
            raise NativeAPIError(f"Unexpected capacity from DLL: {capacity}; expected 10.")

        self._lib = lib
        self._handle = handle.value

    def close(self) -> None:
        if self._handle is not None and self._lib is not None:
            self._lib.ds_destroy(self._handle)
            self._handle = None

    def _require_handle(self) -> int:
        if self._handle is None or self._lib is None:
            raise NativeAPIError("Native API is closed or not initialized.")
        return self._handle

    def insert(self, kind: int, value: int) -> int:
        if not isinstance(value, int) or isinstance(value, bool):
            raise ValueError("Value must be a Python int, not a bool.")
        if value < -2147483648 or value > 2147483647:
            raise ValueError("Value is outside the 32-bit signed range.")
        if kind not in (KIND_QUEUE, KIND_STACK, KIND_LIST):
            raise ValueError(f"Unsupported kind: {kind}")
        status = self._lib.ds_insert(self._require_handle(), ct.c_int32(kind), ct.c_int32(value))
        return int(status)

    def remove_first(self, kind: int) -> tuple[int, Optional[int]]:
        if kind not in (KIND_QUEUE, KIND_STACK, KIND_LIST):
            raise ValueError(f"Unsupported kind: {kind}")
        out_value = ct.c_int32()
        status = self._lib.ds_remove_first(self._require_handle(), ct.c_int32(kind), ct.byref(out_value))
        removed = None if status != DS_OK else int(out_value.value)
        return int(status), removed

    def remove_value(self, kind: int, value: int) -> int:
        if kind not in (KIND_QUEUE, KIND_STACK, KIND_LIST):
            raise ValueError(f"Unsupported kind: {kind}")
        if not isinstance(value, int) or isinstance(value, bool):
            raise ValueError("Value must be a Python int, not a bool.")
        if value < -2147483648 or value > 2147483647:
            raise ValueError("Value is outside the 32-bit signed range.")
        return int(self._lib.ds_remove_value(self._require_handle(), ct.c_int32(kind), ct.c_int32(value)))

    def clear(self, kind: int) -> tuple[int, int]:
        if kind not in (KIND_QUEUE, KIND_STACK, KIND_LIST):
            raise ValueError(f"Unsupported kind: {kind}")
        removed = ct.c_uint32()
        status = self._lib.ds_clear(self._require_handle(), ct.c_int32(kind), ct.byref(removed))
        return int(status), int(removed.value)

    def copy_values(self, kind: int) -> tuple[int, list[int], int]:
        if kind not in (KIND_QUEUE, KIND_STACK, KIND_LIST):
            raise ValueError(f"Unsupported kind: {kind}")
        count = ct.c_uint32()
        status = self._lib.ds_copy_values(
            self._require_handle(),
            ct.c_int32(kind),
            None,
            0,
            ct.byref(count),
        )
        if status not in (DS_OK, DS_BUFFER_TOO_SMALL):
            return int(status), [], int(count.value)

        capacity = max(int(count.value), 0)
        if capacity == 0:
            return DS_OK, [], 0

        buffer = (ct.c_int32 * capacity)()
        result_count = ct.c_uint32()
        status = self._lib.ds_copy_values(
            self._require_handle(),
            ct.c_int32(kind),
            buffer,
            ct.c_uint32(capacity),
            ct.byref(result_count),
        )
        values = [int(buffer[i]) for i in range(int(result_count.value))]
        return int(status), values, int(result_count.value)

    def log_count(self) -> tuple[int, int]:
        count = ct.c_uint64()
        status = self._lib.ds_log_count(self._require_handle(), ct.byref(count))
        return int(status), int(count.value)

    def log_read(self, start_index: int, max_items: int = 50) -> tuple[int, list[dict[str, int]]]:
        if start_index < 0 or max_items < 1 or max_items > 100:
            raise ValueError("Invalid log page parameters.")
        sequences = (ct.c_uint64 * max_items)()
        kinds = (ct.c_int32 * max_items)()
        actions = (ct.c_int32 * max_items)()
        values = (ct.c_int32 * max_items)()
        quantities = (ct.c_uint32 * max_items)()
        out_written = ct.c_uint32()
        status = self._lib.ds_log_read(
            self._require_handle(),
            ct.c_uint64(start_index),
            ct.c_uint32(max_items),
            sequences,
            kinds,
            actions,
            values,
            quantities,
            ct.byref(out_written),
        )
        items: list[dict[str, int]] = []
        written = int(out_written.value)
        for i in range(written):
            items.append(
                {
                    "sequence": int(sequences[i]),
                    "kind": int(kinds[i]),
                    "action": int(actions[i]),
                    "value": int(values[i]),
                    "quantity": int(quantities[i]),
                }
            )
        return int(status), items

    def __enter__(self) -> "NativeAPI":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
