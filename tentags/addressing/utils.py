from __future__ import annotations

import re

from .errors import InvalidColumnNameError

_CELL_RE = re.compile(r"^[A-Za-z]+[1-9][0-9]*$")
_RANGE_RE = re.compile(
    r"^\s*[A-Za-z]+[1-9][0-9]*\s*:\s*[A-Za-z]+[1-9][0-9]*\s*$"
)


def column_to_name(index: int) -> str:
    if not isinstance(index, int) or index < 0:
        raise InvalidColumnNameError("Column index must be a zero-based positive integer.")

    result = ""
    value = index + 1
    while value > 0:
        value, remainder = divmod(value - 1, 26)
        result = chr(65 + remainder) + result
    return result


def name_to_column(name: str) -> int:
    raw = str(name or "").strip().upper()
    if not raw or not raw.isalpha():
        raise InvalidColumnNameError(f"Invalid column name: {name!r}")

    value = 0
    for char in raw:
        if not ("A" <= char <= "Z"):
            raise InvalidColumnNameError(f"Invalid column name: {name!r}")
        value = value * 26 + (ord(char) - 64)
    return value - 1


def is_cell_ref(value: str) -> bool:
    return bool(_CELL_RE.fullmatch(str(value or "").strip()))


def is_range_ref(value: str) -> bool:
    return bool(_RANGE_RE.fullmatch(str(value or "").strip()))
