"""
TenTags Addressing Model.

This package owns the canonical address syntax used by future navigation,
value lookup, copy, foreach, chart, and PyCells integration features.
"""

from .address import Address
from .errors import (
    AddressingError,
    DuplicateMarkError,
    InvalidAddressError,
    InvalidCellRefError,
    InvalidColumnNameError,
    InvalidRangeError,
)
from .location import AddressType, Location
from .mark import Mark
from .parser import parse_address, parse_cell_ref, parse_location, parse_range
from .range import RangeRef
from .resolver import AddressContext, AddressResolver, AddressTarget, ResolvedAddress
from .utils import column_to_name, is_cell_ref, is_range_ref, name_to_column

__all__ = [
    "Address",
    "AddressContext",
    "AddressResolver",
    "AddressType",
    "AddressTarget",
    "AddressingError",
    "CellRef",
    "DuplicateMarkError",
    "InvalidAddressError",
    "InvalidCellRefError",
    "InvalidColumnNameError",
    "InvalidRangeError",
    "Location",
    "Mark",
    "RangeRef",
    "ResolvedAddress",
    "column_to_name",
    "is_cell_ref",
    "is_range_ref",
    "name_to_column",
    "parse_address",
    "parse_cell_ref",
    "parse_location",
    "parse_range",
]

from .address import CellRef
