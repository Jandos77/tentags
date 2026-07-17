from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from .address import CellRef


class AddressType(Enum):
    CELL = "cell"
    RANGE = "range"
    MARK = "mark"


@dataclass(frozen=True)
class Location:
    """The right-most location part of an address."""

    type: AddressType
    cell: Optional[CellRef] = None
    range: Optional["RangeRef"] = None
    mark: Optional[str] = None

    @classmethod
    def cell_ref(cls, cell: CellRef) -> "Location":
        return cls(type=AddressType.CELL, cell=cell)

    @classmethod
    def range_ref(cls, range_ref: "RangeRef") -> "Location":
        return cls(type=AddressType.RANGE, range=range_ref)

    @classmethod
    def mark_ref(cls, mark: str) -> "Location":
        return cls(type=AddressType.MARK, mark=mark)


from .range import RangeRef
