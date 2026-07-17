from __future__ import annotations

import re

from .address import Address, CellRef
from .errors import InvalidAddressError, InvalidCellRefError, InvalidRangeError
from .location import Location
from .range import RangeRef
from .utils import column_to_name, is_cell_ref, is_range_ref, name_to_column

_CELL_RE = re.compile(r"^([A-Za-z]+)([1-9][0-9]*)$")
_RANGE_RE = re.compile(
    r"^\s*([A-Za-z]+[1-9][0-9]*)\s*:\s*([A-Za-z]+[1-9][0-9]*)\s*$"
)
_MARK_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_.-]*$")


def parse_cell_ref(value: str) -> CellRef:
    raw = str(value or "").strip()
    match = _CELL_RE.fullmatch(raw)
    if not match:
        raise InvalidCellRefError(f"Invalid A1 cell reference: {value!r}")

    col_name, row_text = match.groups()
    return CellRef(row=int(row_text) - 1, col=name_to_column(col_name))


def parse_range(value: str) -> RangeRef:
    raw = str(value or "").strip()
    match = _RANGE_RE.fullmatch(raw)
    if not match:
        raise InvalidRangeError(f"Invalid A1 range reference: {value!r}")

    first = parse_cell_ref(match.group(1))
    second = parse_cell_ref(match.group(2))

    top = min(first.row, second.row)
    bottom = max(first.row, second.row)
    left = min(first.col, second.col)
    right = max(first.col, second.col)
    return RangeRef(start=CellRef(row=top, col=left), end=CellRef(row=bottom, col=right))


def parse_location(value: str) -> Location:
    raw = str(value or "").strip()
    if not raw:
        raise InvalidAddressError("Address location cannot be empty.")

    if is_range_ref(raw):
        return Location.range_ref(parse_range(raw))
    if is_cell_ref(raw):
        return Location.cell_ref(parse_cell_ref(raw))
    if re.fullmatch(r"[A-Za-z]+[0-9]+", raw):
        raise InvalidCellRefError(f"Invalid A1 cell reference: {value!r}")
    if _MARK_RE.fullmatch(raw):
        return Location.mark_ref(raw)

    raise InvalidAddressError(f"Invalid address location: {value!r}")


def parse_address(value: str) -> Address:
    raw = str(value or "").strip()
    if not raw:
        raise InvalidAddressError("Address cannot be empty.")

    relative = False
    while raw.startswith("../") or raw.startswith("./"):
        relative = True
        if raw.startswith("../"):
            raw = raw[3:]
        else:
            raw = raw[2:]

    parts = [part.strip() for part in raw.split("!")]
    if any(part == "" for part in parts):
        raise InvalidAddressError(f"Invalid address: {value!r}")
    if len(parts) > 4:
        raise InvalidAddressError("Address supports at most Namespace!Table!List!Location.")

    location = parse_location(parts[-1])
    scopes = parts[:-1]
    project = document = table = None

    if len(scopes) == 1:
        table = scopes[0]
    elif len(scopes) == 2:
        # PyCells-compatible canonical form: Table!List!Location.
        document, table = scopes
    elif len(scopes) == 3:
        # Kept as a forward-compatible namespace, not the canonical form.
        project, document, table = scopes

    return Address(
        project=project,
        document=document,
        table=table,
        location=location,
        relative=relative,
    )


def cell_ref_to_name(cell: CellRef) -> str:
    return f"{column_to_name(cell.col)}{cell.row + 1}"
