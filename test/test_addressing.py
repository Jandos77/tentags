import pytest

from tentags.addressing import (
    AddressType,
    InvalidAddressError,
    InvalidCellRefError,
    InvalidColumnNameError,
    column_to_name,
    is_cell_ref,
    is_range_ref,
    name_to_column,
    parse_address,
    parse_cell_ref,
    parse_location,
    parse_range,
)


def test_column_name_roundtrip():
    examples = {
        0: "A",
        25: "Z",
        26: "AA",
        27: "AB",
        701: "ZZ",
        702: "AAA",
    }

    for index, name in examples.items():
        assert column_to_name(index) == name
        assert name_to_column(name) == index
        assert name_to_column(name.lower()) == index


def test_invalid_column_names():
    with pytest.raises(InvalidColumnNameError):
        column_to_name(-1)
    with pytest.raises(InvalidColumnNameError):
        name_to_column("")
    with pytest.raises(InvalidColumnNameError):
        name_to_column("A1")


def test_parse_cell_ref():
    assert parse_cell_ref("A1").row == 0
    assert parse_cell_ref("A1").col == 0
    assert parse_cell_ref("AA120").row == 119
    assert parse_cell_ref("AA120").col == 26

    assert is_cell_ref("A1")
    assert is_cell_ref("aa120")
    assert not is_cell_ref("A0")
    assert not is_cell_ref("1A")


def test_invalid_cell_refs():
    for value in ("", "A0", "1A", "A", "$A$1", "A-1"):
        with pytest.raises(InvalidCellRefError):
            parse_cell_ref(value)


def test_parse_range_normalizes_reverse_ranges():
    ref = parse_range("C3:A1")

    assert ref.start.row == 0
    assert ref.start.col == 0
    assert ref.end.row == 2
    assert ref.end.col == 2
    assert ref.rows == 3
    assert ref.cols == 3
    assert [(cell.row, cell.col) for cell in ref.iter_cells()] == [
        (0, 0),
        (0, 1),
        (0, 2),
        (1, 0),
        (1, 1),
        (1, 2),
        (2, 0),
        (2, 1),
        (2, 2),
    ]

    assert is_range_ref("A1:C3")
    assert is_range_ref(" c3 : a1 ")
    assert not is_range_ref("A1:")


def test_parse_location_cell_range_and_mark():
    cell = parse_location("A1")
    range_location = parse_location("A1:C3")
    mark = parse_location("Summary")

    assert cell.type is AddressType.CELL
    assert cell.cell.row == 0
    assert cell.cell.col == 0

    assert range_location.type is AddressType.RANGE
    assert range_location.range.rows == 3
    assert range_location.range.cols == 3

    assert mark.type is AddressType.MARK
    assert mark.mark == "Summary"


def test_parse_address_right_to_left_scopes():
    local = parse_address("A1")
    list_ref = parse_address("List_1!A1")
    table_list = parse_address("Table_1!List_1!A1")
    namespace = parse_address("ERP!Table_1!List_1!A1")
    marked = parse_address("Table_1!List_1!Summary")

    assert local.location.type is AddressType.CELL
    assert local.project is None
    assert local.document is None
    assert local.table is None
    assert local.sheet is None

    assert list_ref.table == "List_1"
    assert list_ref.table_name == "List_1"
    assert list_ref.list_name == "List_1"
    assert list_ref.document is None
    assert list_ref.project is None

    assert table_list.document == "Table_1"
    assert table_list.table == "List_1"
    assert table_list.table_name == "List_1"
    assert table_list.list_name == "List_1"
    assert table_list.project is None

    assert namespace.project == "ERP"
    assert namespace.document == "Table_1"
    assert namespace.table == "List_1"
    assert namespace.location.cell.row == 0
    assert namespace.location.cell.col == 0

    assert marked.location.type is AddressType.MARK
    assert marked.location.mark == "Summary"


def test_parse_address_ranges_and_relative_placeholder():
    address = parse_address("../Table_1!List_1!A3:D7")

    assert address.relative is True
    assert address.document == "Table_1"
    assert address.table == "List_1"
    assert address.table_name == "List_1"
    assert address.list_name == "List_1"
    assert address.location.type is AddressType.RANGE
    assert address.location.range.start.row == 2
    assert address.location.range.start.col == 0
    assert address.location.range.end.row == 6
    assert address.location.range.end.col == 3
    assert address.location.range.rows == 5
    assert address.location.range.cols == 4


def test_parse_address_accepts_real_table_list_names():
    invoice_cell = parse_address("Invoice!Items!A4")
    report_range = parse_address("Report!Sales!A3:D7")
    crm_mark = parse_address("CRM!Customers!Summary")
    named_with_spaces = parse_address("Annual Report!Balance Sheet!Totals")

    assert invoice_cell.document == "Invoice"
    assert invoice_cell.list_name == "Items"
    assert invoice_cell.location.type is AddressType.CELL
    assert invoice_cell.location.cell.row == 3
    assert invoice_cell.location.cell.col == 0

    assert report_range.document == "Report"
    assert report_range.list_name == "Sales"
    assert report_range.location.type is AddressType.RANGE
    assert report_range.location.range.start.row == 2
    assert report_range.location.range.start.col == 0
    assert report_range.location.range.end.row == 6
    assert report_range.location.range.end.col == 3

    assert crm_mark.document == "CRM"
    assert crm_mark.list_name == "Customers"
    assert crm_mark.location.type is AddressType.MARK
    assert crm_mark.location.mark == "Summary"

    assert named_with_spaces.document == "Annual Report"
    assert named_with_spaces.list_name == "Balance Sheet"
    assert named_with_spaces.location.mark == "Totals"


def test_invalid_addresses():
    for value in ("", "!", "A1!", "A!B!C!D!E", "Table_1!A0", "Table_1!A1:"):
        with pytest.raises((InvalidAddressError, InvalidCellRefError)):
            parse_address(value)
