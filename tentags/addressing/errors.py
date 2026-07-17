class AddressingError(ValueError):
    """Base error for TenTags addressing failures."""


class InvalidColumnNameError(AddressingError):
    """Raised when an A1 column name is invalid."""


class InvalidCellRefError(AddressingError):
    """Raised when a cell reference is not valid A1 notation."""


class InvalidRangeError(AddressingError):
    """Raised when a range reference is invalid."""


class InvalidAddressError(AddressingError):
    """Raised when a full address cannot be parsed."""


class DuplicateMarkError(AddressingError):
    """Raised when the same mark appears more than once in a scope."""
