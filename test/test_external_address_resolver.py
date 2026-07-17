from pathlib import Path
import re
import sys

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import tentags
from demo_paths import demo_output_path
from tentags.addressing import AddressResolver, AddressType, parse_address


def _tables():
    return [
        {
            "document": "Table_1",
            "table_name": "List_1",
            "sheet_name": "List_1",
            "preamble": '2,1,1,"#000","solid",0,24',
            "data": "data(<url=goto:Table_1!List_2!Summary>Go to List_2 summary</url>; List_1 row)",
        },
        {
            "document": "Table_1",
            "table_name": "List_2",
            "sheet_name": "List_2",
            "preamble": '2,1,1,"#000","solid",0,24',
            "data": "data(List_2 top; <mark=Summary>List_2 summary)",
        },
    ]


def _real_name_tables():
    return [
        {
            "document": "Annual Report",
            "table_name": "Income Statement",
            "sheet_name": "Income Statement",
            "preamble": '2,1,1,"#000","solid",0,24',
            "data": "data(<url=goto:Annual Report!Balance Sheet!Totals>Go to totals</url>; Revenue)",
        },
        {
            "document": "Annual Report",
            "table_name": "Balance Sheet",
            "sheet_name": "Balance Sheet",
            "preamble": '2,1,1,"#000","solid",0,24',
            "data": "data(Assets; <mark=Totals>Balance totals)",
        },
    ]


def _multitable_address_tables():
    return [
        {
            "document": "Navigation",
            "table_name": "Links",
            "sheet_name": "Links",
            "title": "Navigation Links",
            "preamble": '3,1,1,"#0f172a","solid",0,24',
            "style": (
                "style("
                "<bg=#dbeafe><color=#1e3a8a><b></b></color></bg>; "
                "<bg=#eff6ff></bg>; "
                "<bg=#eff6ff></bg>"
                ")"
            ),
            "data": (
                "data("
                "<url=goto:Invoice!Items!A4>Open invoice item</url>; "
                "<url=goto:Report!Sales!A3:D7>Open sales range</url>; "
                "<url=goto:CRM!Customers!Summary>Open customer summary</url>"
                ")"
            ),
        },
        {
            "document": "Invoice",
            "table_name": "Items",
            "sheet_name": "Items",
            "title": "Invoice Items",
            "preamble": '4,1,2,"#7c2d12","dashed",0,26',
            "style": (
                "style("
                "<bg=#ffedd5><color=#7c2d12><b></b></color></bg>; "
                "<bg=#fff7ed></bg>; "
                "<bg=#fff7ed></bg>; "
                "<bg=#fed7aa><b></b></bg>"
                ")"
            ),
            "data": "data(Item A1; Item A2; Item A3; Invoice item A4)",
        },
        {
            "document": "Report",
            "table_name": "Sales",
            "sheet_name": "Sales",
            "title": "Sales Report",
            "preamble": '7,4,1,"#166534","solid-1",0,22',
            "style": (
                "style("
                "<bg=#dcfce7><color=#166534><b></b></color></bg>, "
                "<bg=#dcfce7><color=#166534><b></b></color></bg>, "
                "<bg=#dcfce7><color=#166534><b></b></color></bg>, "
                "<bg=#dcfce7><color=#166534><b></b></color></bg>"
                ")"
            ),
            "data": (
                "data("
                "S1A, S1B, S1C, S1D; "
                "S2A, S2B, S2C, S2D; "
                "Sales A3, S3B, S3C, S3D; "
                "S4A, S4B, S4C, S4D; "
                "S5A, S5B, S5C, S5D; "
                "S6A, S6B, S6C, S6D; "
                "S7A, S7B, S7C, S7D"
                ")"
            ),
        },
        {
            "document": "CRM",
            "table_name": "Customers",
            "sheet_name": "Customers",
            "title": "CRM Customers",
            "preamble": '2,1,1,"#581c87","dotted",0,28',
            "style": (
                "style("
                "<bg=#f3e8ff><color=#581c87><b></b></color></bg>; "
                "<bg=#faf5ff></bg>"
                ")"
            ),
            "data": "data(Customer top; <mark=Summary>Customer summary)",
        },
    ]


def build_external_resolver_artifacts():
    html_output = demo_output_path("external_resolver_navigation.html")
    xlsx_output = demo_output_path("external_resolver_navigation.xlsx")
    stacked_xlsx_output = demo_output_path("external_resolver_navigation_stacked.xlsx")
    pdf_output = demo_output_path("external_resolver_navigation.pdf")
    multitable_pdf_output = demo_output_path("multitable_addressing.pdf")

    tables = _multitable_address_tables()

    html = tentags.multitable_html(tables, full_page=True)
    html_output.write_text(html, encoding="utf-8")

    pytest.importorskip("openpyxl")
    tentags.multitable_xlsx(tables, xlsx_output, mode="sheets")
    tentags.multitable_xlsx(tables, stacked_xlsx_output, mode="stacked", gap=3)

    if tentags.features()["pdf"]:
        tentags.multitable_pdf(tables, str(pdf_output), page_break_after_each=False)
        tentags.multitable_pdf(tables, str(multitable_pdf_output), page_break_after_each=True)

    return html_output, xlsx_output, stacked_xlsx_output, pdf_output, multitable_pdf_output


def test_address_resolver_resolves_table_list_mark():
    ops_model = tentags.parse('2,1,1,"#000","solid",0,24, data(Top; <mark=Summary>Bottom)')
    resolver = AddressResolver()
    target = resolver.register(
        ops_model,
        document="Table_1",
        list_name="List_2",
        html_prefix="Table_1-List_2",
        xlsx_sheet_name="List_2",
    )

    address = parse_address("Table_1!List_2!Summary")
    resolved = resolver.resolve(address)

    assert resolved is not None
    assert resolved.target is target
    assert resolved.address.location.type is AddressType.MARK
    assert resolved.address.document == "Table_1"
    assert resolved.address.list_name == "List_2"
    assert resolved.start_cell().row == 1
    assert resolved.start_cell().col == 0


def test_multitable_html_maps_scoped_goto_to_pycells_table_list_mark():
    html = tentags.multitable_html(_tables(), full_page=True)

    assert 'id="tt-Table_1-List_1-A1"' in html
    assert 'id="tt-Table_1-List_2-mark-Summary"' in html
    assert '<a href="#tt-Table_1-List_2-mark-Summary"' in html


def test_multitable_xlsx_maps_scoped_goto_to_pycells_table_list():
    openpyxl = pytest.importorskip("openpyxl")
    output = demo_output_path("external_resolver_navigation.xlsx")
    if output.exists():
        output.unlink()

    tentags.multitable_xlsx(_tables(), output, mode="sheets")

    wb = openpyxl.load_workbook(output)
    list_1 = wb["List_1"]
    list_2 = wb["List_2"]

    assert list_1["A1"].value == "Go to List_2 summary"
    assert list_1["A1"].hyperlink.target == "#List_2!A2"
    assert list_2["A2"].value == "List_2 summary"


def test_multitable_renderers_accept_real_table_and_list_names():
    openpyxl = pytest.importorskip("openpyxl")
    output = demo_output_path("real_name_resolver_navigation.xlsx")
    if output.exists():
        output.unlink()

    html = tentags.multitable_html(_real_name_tables(), full_page=True)
    tentags.multitable_xlsx(_real_name_tables(), output, mode="sheets")

    assert 'id="tt-Annual-Report-Income-Statement-A1"' in html
    assert 'id="tt-Annual-Report-Balance-Sheet-mark-Totals"' in html
    assert '<a href="#tt-Annual-Report-Balance-Sheet-mark-Totals"' in html

    wb = openpyxl.load_workbook(output)
    income = wb["Income Statement"]
    balance = wb["Balance Sheet"]

    assert income["A1"].value == "Go to totals"
    assert income["A1"].hyperlink.target == "#'Balance Sheet'!A2"
    assert balance["A2"].value == "Balance totals"


def test_multitable_supports_cell_range_and_mark_addresses_in_html():
    tables = _multitable_address_tables()
    html = tentags.multitable_html(tables, full_page=True)

    assert len(tables) == 4
    assert html.count("<table ") == 4
    assert 'id="tt-Invoice-Items-A4"' in html
    assert 'id="tt-Report-Sales-A3"' in html
    assert 'id="tt-CRM-Customers-mark-Summary"' in html

    assert '<a href="#tt-Invoice-Items-A4"' in html
    assert '<a href="#tt-Report-Sales-A3"' in html
    assert '<a href="#tt-CRM-Customers-mark-Summary"' in html


def test_each_multitable_list_has_own_preamble_style_and_data():
    openpyxl = pytest.importorskip("openpyxl")
    output = demo_output_path("multitable_own_preamble_style_data.xlsx")
    if output.exists():
        output.unlink()

    tables = _multitable_address_tables()
    html = tentags.multitable_html(tables, full_page=True)
    tentags.multitable_xlsx(tables, output, mode="sheets")

    assert len(tables) == 4
    assert all(table.get("preamble") for table in tables)
    assert all(table.get("style", "").startswith("style(") for table in tables)
    assert all(table.get("data", "").startswith("data(") for table in tables)
    assert len({table["preamble"] for table in tables}) == 4
    assert len({table["style"] for table in tables}) == 4
    assert len({table["data"] for table in tables}) == 4

    assert "background-color:#dbeafe;" in html
    assert "background-color:#ffedd5;" in html
    assert "background-color:#dcfce7;" in html
    assert "background-color:#f3e8ff;" in html

    wb = openpyxl.load_workbook(output)
    assert wb["Links"]["A1"].fill.start_color.rgb.lower().endswith("dbeafe")
    assert wb["Items"]["A1"].fill.start_color.rgb.lower().endswith("ffedd5")
    assert wb["Sales"]["A1"].fill.start_color.rgb.lower().endswith("dcfce7")
    assert wb["Customers"]["A1"].fill.start_color.rgb.lower().endswith("f3e8ff")
    assert wb["Links"]["A1"].font.bold is True
    assert wb["Items"]["A1"].font.bold is True


def test_multitable_xlsx_sheets_supports_cell_range_and_mark_addresses():
    openpyxl = pytest.importorskip("openpyxl")
    output = demo_output_path("multitable_addressing_sheets.xlsx")
    if output.exists():
        output.unlink()

    tables = _multitable_address_tables()
    tentags.multitable_xlsx(tables, output, mode="sheets")

    wb = openpyxl.load_workbook(output)
    assert len(tables) == 4
    assert wb.sheetnames == ["Links", "Items", "Sales", "Customers"]

    links = wb["Links"]
    items = wb["Items"]
    sales = wb["Sales"]
    customers = wb["Customers"]

    assert links["A1"].hyperlink.target == "#Items!A4"
    assert links["A2"].hyperlink.target == "#Sales!A3"
    assert links["A3"].hyperlink.target == "#Customers!A2"

    assert items["A4"].value == "Invoice item A4"
    assert sales["A3"].value == "Sales A3"
    assert customers["A2"].value == "Customer summary"


def test_multitable_xlsx_stacked_supports_cell_range_and_mark_addresses():
    openpyxl = pytest.importorskip("openpyxl")
    output = demo_output_path("multitable_addressing_stacked.xlsx")
    if output.exists():
        output.unlink()

    tables = _multitable_address_tables()
    tentags.multitable_xlsx(tables, output, mode="stacked", gap=3)

    wb = openpyxl.load_workbook(output)
    ws = wb["Report"]

    assert len(tables) == 4
    assert wb.sheetnames == ["Report"]
    assert ws["A1"].value == "Navigation Links"
    assert ws["A2"].value == "Open invoice item"
    assert ws["A8"].value == "Invoice Items"
    assert ws["A9"].value == "Item A1"
    assert ws["A16"].value == "Sales Report"
    assert ws["A17"].value == "S1A"
    assert ws["A27"].value == "CRM Customers"
    assert ws["A28"].value == "Customer top"

    assert ws["A2"].hyperlink.target == "#Report!A12"
    assert ws["A3"].hyperlink.target == "#Report!A19"
    assert ws["A4"].hyperlink.target == "#Report!A29"

    assert ws["A12"].value == "Invoice item A4"
    assert ws["A19"].value == "Sales A3"
    assert ws["A29"].value == "Customer summary"


def test_external_resolver_direct_script_artifacts_are_valid():
    html_output, xlsx_output, stacked_xlsx_output, pdf_output, multitable_pdf_output = build_external_resolver_artifacts()
    openpyxl = pytest.importorskip("openpyxl")

    assert html_output.exists()
    assert xlsx_output.exists()
    assert stacked_xlsx_output.exists()
    html = html_output.read_text(encoding="utf-8")
    assert html.startswith("<!DOCTYPE html>")
    assert html.count("<table ") == 4
    assert xlsx_output.read_bytes().startswith(b"PK")
    assert stacked_xlsx_output.read_bytes().startswith(b"PK")
    assert openpyxl.load_workbook(xlsx_output).sheetnames == ["Links", "Items", "Sales", "Customers"]
    assert openpyxl.load_workbook(stacked_xlsx_output).sheetnames == ["Report"]
    if pdf_output.exists():
        data = pdf_output.read_bytes()
        assert data.startswith(b"%PDF")
        assert len(data) > 1000
    if multitable_pdf_output.exists():
        data = multitable_pdf_output.read_bytes()
        assert data.startswith(b"%PDF")
        assert len(data) > 1000
        assert len(re.findall(rb"/Type\s*/Page\b", data)) >= 4


if __name__ == "__main__":
    html_path, xlsx_path, stacked_xlsx_path, pdf_path, multitable_pdf_path = build_external_resolver_artifacts()
    print(f"HTML created: {html_path}")
    print(f"XLSX created: {xlsx_path}")
    print(f"Stacked XLSX created: {stacked_xlsx_path}")
    if pdf_path.exists():
        print(f"PDF created: {pdf_path}")
    if multitable_pdf_path.exists():
        print(f"Multitable PDF created: {multitable_pdf_path}")
