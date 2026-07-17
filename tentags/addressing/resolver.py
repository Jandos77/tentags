from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Iterable, Optional

from .address import Address, CellRef
from .errors import DuplicateMarkError
from .location import AddressType


def _slug(value: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9_.:-]+", "-", str(value).strip())
    return safe.strip("-") or "table"


@dataclass(frozen=True, init=False)
class AddressContext:
    """Logical position used as the base for resolving relative/local addresses."""

    project: Optional[str] = None
    document: Optional[str] = None
    table: Optional[str] = None

    def __init__(
        self,
        project: str = None,
        document: str = None,
        table: str = None,
        sheet: str = None,
        list_name: str = None,
    ) -> None:
        object.__setattr__(self, "project", project)
        object.__setattr__(self, "document", document)
        object.__setattr__(self, "table", table if table is not None else list_name if list_name is not None else sheet)

    @property
    def sheet(self) -> Optional[str]:
        return self.table

    @property
    def list_name(self) -> Optional[str]:
        return self.table


@dataclass
class AddressTarget:
    """A logical List plus renderer-facing names derived from that List."""

    model: Any
    context: AddressContext = field(default_factory=AddressContext)
    html_prefix: Optional[str] = None
    xlsx_sheet_name: Optional[str] = None
    xlsx_start_row: int = 1
    pdf_prefix: Optional[str] = None
    _mark_index: Optional[dict[str, CellRef]] = field(default=None, init=False, repr=False)

    def mark_index(self) -> dict[str, CellRef]:
        if self._mark_index is not None:
            return self._mark_index

        marks: dict[str, CellRef] = {}
        for row_index, row in enumerate(getattr(self.model, "cells", [])):
            for col_index, cell in enumerate(row):
                mark = getattr(cell, "mark", None)
                if not mark:
                    continue
                mark_name = str(mark)
                if mark_name in marks:
                    raise DuplicateMarkError(f"Duplicate mark: {mark_name}")
                marks[mark_name] = CellRef(row=row_index, col=col_index)
        self._mark_index = marks
        return marks


@dataclass(frozen=True)
class ResolvedAddress:
    """Resolved logical address against a concrete table target."""

    address: Address
    target: AddressTarget

    def start_cell(self) -> Optional[CellRef]:
        location = self.address.location
        if location.type is AddressType.CELL:
            return location.cell
        if location.type is AddressType.RANGE:
            return location.range.start
        if location.type is AddressType.MARK:
            return self.target.mark_index().get(location.mark)
        return None

    @property
    def mark(self) -> Optional[str]:
        location = self.address.location
        if location.type is AddressType.MARK:
            return location.mark
        return None


class AddressResolver:
    """Resolves PyCells-compatible Table!List!Location addresses."""

    def __init__(self, targets: Iterable[AddressTarget] = ()):
        self.targets: list[AddressTarget] = list(targets)

    def register(
        self,
        model: Any,
        *,
        project: str = None,
        document: str = None,
        table: str = None,
        sheet: str = None,
        list_name: str = None,
        html_prefix: str = None,
        xlsx_sheet_name: str = None,
        xlsx_start_row: int = 1,
        pdf_prefix: str = None,
    ) -> AddressTarget:
        target = AddressTarget(
            model=model,
            context=AddressContext(
                project=project,
                document=document,
                table=table,
                sheet=sheet,
                list_name=list_name,
            ),
            html_prefix=html_prefix,
            xlsx_sheet_name=xlsx_sheet_name,
            xlsx_start_row=xlsx_start_row,
            pdf_prefix=pdf_prefix,
        )
        self.targets.append(target)
        return target

    def resolve(self, address: Address, current: AddressTarget = None) -> Optional[ResolvedAddress]:
        if not self._has_scope(address):
            if current is not None:
                return ResolvedAddress(address=address, target=current)
            if self.targets:
                return ResolvedAddress(address=address, target=self.targets[0])
            return None

        for target in self.targets:
            if self._matches(address, target.context):
                return ResolvedAddress(address=address, target=target)
        return None

    @staticmethod
    def html_prefix_for(context: AddressContext, index: int = 0) -> str:
        parts = [context.project, context.document, context.table]
        raw = "-".join(part for part in parts if part) or f"table-{index + 1}"
        return _slug(raw)

    @staticmethod
    def _has_scope(address: Address) -> bool:
        return bool(address.project or address.document or address.table)

    @staticmethod
    def _matches(address: Address, context: AddressContext) -> bool:
        if address.project is not None and address.project != context.project:
            return False
        if address.document is not None and address.document != context.document:
            return False
        if address.table is not None and address.table != context.table:
            return False
        return True
