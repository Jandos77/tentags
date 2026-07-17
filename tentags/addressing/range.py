from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator

from .address import CellRef


@dataclass(frozen=True)
class RangeRef:
    """Inclusive zero-based rectangular cell range."""

    start: CellRef
    end: CellRef

    @property
    def rows(self) -> int:
        return self.end.row - self.start.row + 1

    @property
    def cols(self) -> int:
        return self.end.col - self.start.col + 1

    def iter_cells(self) -> Iterator[CellRef]:
        for row in range(self.start.row, self.end.row + 1):
            for col in range(self.start.col, self.end.col + 1):
                yield CellRef(row=row, col=col)
