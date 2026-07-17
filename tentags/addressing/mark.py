from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Mark:
    """Named logical location attached to a cell."""

    name: str
