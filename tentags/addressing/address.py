from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CellRef:
    """Zero-based logical cell coordinate."""

    row: int
    col: int

    def __post_init__(self) -> None:
        if self.row < 0 or self.col < 0:
            raise ValueError("CellRef row and col must be zero or positive.")


@dataclass(frozen=True)
class Address:
    """Universal logical address.

    Canonical syntax is Table!List!Location, for example
    Table_1!List_1!A4 or Table_1!List_1!A3:D7.
    """

    location: "Location"
    project: Optional[str] = None
    document: Optional[str] = None
    table: Optional[str] = None
    relative: bool = False

    @property
    def sheet(self) -> Optional[str]:
        """Backward-compatible alias for the table/list scope."""

        return self.table

    @property
    def table_name(self) -> Optional[str]:
        """Logical List name inside the PyCells Table."""

        return self.table

    @property
    def list_name(self) -> Optional[str]:
        """Logical List name inside the PyCells Table."""

        return self.table
