from pathlib import Path
import re
import sys

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEST_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(TEST_ROOT) not in sys.path:
    sys.path.insert(0, str(TEST_ROOT))

import tentags
from demo_paths import demo_output_path
from test_external_address_resolver import _multitable_address_tables


def build_multitable_addressing_artifacts():
    html_output = demo_output_path("multitable_addressing.html")
    xlsx_output = demo_output_path("multitable_addressing_sheets.xlsx")
    stacked_xlsx_output = demo_output_path("multitable_addressing_stacked.xlsx")
    pdf_output = demo_output_path("multitable_addressing.pdf")

    tables = _multitable_address_tables()

    html = tentags.multitable_html(tables, full_page=True)
    html_output.write_text(html, encoding="utf-8")

    pytest.importorskip("openpyxl")
    tentags.multitable_xlsx(tables, xlsx_output, mode="sheets")
    tentags.multitable_xlsx(tables, stacked_xlsx_output, mode="stacked", gap=3)

    if tentags.features()["pdf"]:
        tentags.multitable_pdf(tables, str(pdf_output), page_break_after_each=True)

    return html_output, xlsx_output, stacked_xlsx_output, pdf_output


def build_multitable_format_option_artifacts():
    html_output = demo_output_path("multitable_layout_options.html")
    stacked_xlsx_output = demo_output_path("multitable_layout_options_stacked.xlsx")
    pdf_output = demo_output_path("multitable_layout_options_landscape.pdf")

    tables = _multitable_address_tables()

    html = tentags.multitable_html(
        tables,
        layout="grid",
        cols=2,
        gap="40px",
        full_page=True,
    )
    html_output.write_text(html, encoding="utf-8")

    pytest.importorskip("openpyxl")
    tentags.multitable_xlsx(
        tables,
        stacked_xlsx_output,
        mode="stacked",
        gap=1,
        show_titles=False,
    )

    if tentags.features()["pdf"]:
        tentags.multitable_pdf(
            tables,
            str(pdf_output),
            page_size="A4",
            orientation="landscape",
            page_break_after_each=True,
            margins=(18, 24, 30, 36),
        )

    return html_output, stacked_xlsx_output, pdf_output


def test_multitable_has_multiple_separate_tables_in_html():
    html_output, _, _, _ = build_multitable_addressing_artifacts()
    html = html_output.read_text(encoding="utf-8")

    assert html.startswith("<!DOCTYPE html>")
    assert html.count("<table ") == 4
    assert 'id="tt-Navigation-Links-A1"' in html
    assert 'id="tt-Invoice-Items-A4"' in html
    assert 'id="tt-Report-Sales-A3"' in html
    assert 'id="tt-CRM-Customers-mark-Summary"' in html


def test_multitable_has_multiple_separate_sheets_in_xlsx():
    openpyxl = pytest.importorskip("openpyxl")
    _, xlsx_output, _, _ = build_multitable_addressing_artifacts()

    wb = openpyxl.load_workbook(xlsx_output)

    assert wb.sheetnames == ["Links", "Items", "Sales", "Customers"]
    assert wb["Links"]["A1"].hyperlink.target == "#Items!A4"
    assert wb["Links"]["A2"].hyperlink.target == "#Sales!A3"
    assert wb["Links"]["A3"].hyperlink.target == "#Customers!A2"


def test_multitable_has_multiple_stacked_table_blocks_in_xlsx():
    openpyxl = pytest.importorskip("openpyxl")
    _, _, stacked_xlsx_output, _ = build_multitable_addressing_artifacts()

    wb = openpyxl.load_workbook(stacked_xlsx_output)
    ws = wb["Report"]

    assert wb.sheetnames == ["Report"]
    assert ws["A1"].value == "Navigation Links"
    assert ws["A8"].value == "Invoice Items"
    assert ws["A16"].value == "Sales Report"
    assert ws["A27"].value == "CRM Customers"


def test_multitable_pdf_has_separate_pages_for_separate_tables():
    _, _, _, pdf_output = build_multitable_addressing_artifacts()

    data = pdf_output.read_bytes()

    assert data.startswith(b"%PDF")
    assert len(data) > 1000
    assert len(re.findall(rb"/Type\s*/Page\b", data)) >= 4


def test_multitable_each_sheet_has_own_preamble_style_and_data():
    openpyxl = pytest.importorskip("openpyxl")
    tables = _multitable_address_tables()
    html_output, xlsx_output, _, _ = build_multitable_addressing_artifacts()
    html = html_output.read_text(encoding="utf-8")

    assert len(tables) == 4
    assert all(table.get("preamble") for table in tables)
    assert all(table.get("style", "").strip().startswith("style(") for table in tables)
    assert all(table.get("data", "").strip().startswith("data(") for table in tables)
    assert len({table["preamble"] for table in tables}) == 4
    assert len({table["style"] for table in tables}) == 4
    assert len({table["data"] for table in tables}) == 4

    assert "background-color:#dbeafe;" in html
    assert "background-color:#ffedd5;" in html
    assert "background-color:#dcfce7;" in html
    assert "background-color:#f3e8ff;" in html

    wb = openpyxl.load_workbook(xlsx_output)
    assert wb["Links"]["A1"].fill.start_color.rgb.lower().endswith("dbeafe")
    assert wb["Items"]["A1"].fill.start_color.rgb.lower().endswith("ffedd5")
    assert wb["Sales"]["A1"].fill.start_color.rgb.lower().endswith("dcfce7")
    assert wb["Customers"]["A1"].fill.start_color.rgb.lower().endswith("f3e8ff")


def test_multitable_uses_table_list_names_not_logical_sheet_keys():
    tables = _multitable_address_tables()

    assert len(tables) == 4
    assert all("document" in table for table in tables)
    assert all("table_name" in table for table in tables)
    assert all("sheet_name" in table for table in tables)
    assert all("sheet" not in table for table in tables)

    assert tables[0]["document"] == "Navigation"
    assert tables[0]["table_name"] == "Links"
    assert tables[0]["sheet_name"] == "Links"


def test_multitable_html_format_settings_are_preserved():
    html_output, _, _ = build_multitable_format_option_artifacts()
    html = html_output.read_text(encoding="utf-8")

    assert html.startswith("<!DOCTYPE html>")
    assert html.count("<table ") == 4
    assert "display: grid;" in html
    assert "grid-template-columns: repeat(2, 1fr);" in html
    assert "gap: 40px;" in html


def test_multitable_xlsx_format_settings_are_preserved():
    openpyxl = pytest.importorskip("openpyxl")
    _, stacked_xlsx_output, _ = build_multitable_format_option_artifacts()

    wb = openpyxl.load_workbook(stacked_xlsx_output)
    ws = wb["Report"]

    assert wb.sheetnames == ["Report"]
    assert ws["A1"].value == "Open invoice item"
    assert ws["A5"].value == "Item A1"
    assert ws["A10"].value == "S1A"
    assert ws["A18"].value == "Customer top"
    assert ws["A1"].hyperlink.target == "#Report!A8"
    assert ws["A2"].hyperlink.target == "#Report!A12"
    assert ws["A3"].hyperlink.target == "#Report!A19"


def test_multitable_xlsx_stacked_accepts_shared_string_gap_setting():
    openpyxl = pytest.importorskip("openpyxl")
    output = demo_output_path("multitable_stacked_string_gap.xlsx")

    tentags.multitable_xlsx(
        _multitable_address_tables()[:2],
        output,
        settings={
            "mode": "stacked",
            "gap": "1px",
            "show_titles": True,
        },
    )

    wb = openpyxl.load_workbook(output)
    ws = wb["Report"]

    assert ws["A1"].value == "Navigation Links"
    assert ws["A6"].value == "Invoice Items"


def test_multitable_pdf_format_settings_are_preserved():
    _, _, pdf_output = build_multitable_format_option_artifacts()

    data = pdf_output.read_bytes()
    media_boxes = re.findall(rb"/MediaBox\s*\[\s*0\s+0\s+([0-9.]+)\s+([0-9.]+)\s*\]", data)

    assert data.startswith(b"%PDF")
    assert len(data) > 1000
    assert len(re.findall(rb"/Type\s*/Page\b", data)) >= 4
    assert media_boxes
    width, height = (float(value) for value in media_boxes[0])
    assert width > height
    assert width > 800
    assert height > 500


if __name__ == "__main__":
    html_path, xlsx_path, stacked_xlsx_path, pdf_path = build_multitable_addressing_artifacts()
    layout_html_path, layout_xlsx_path, layout_pdf_path = build_multitable_format_option_artifacts()
    print(f"Multitable HTML created: {html_path}")
    print(f"Multitable sheets XLSX created: {xlsx_path}")
    print(f"Multitable stacked XLSX created: {stacked_xlsx_path}")
    if pdf_path.exists():
        print(f"Multitable PDF created: {pdf_path}")
    print(f"Multitable layout HTML created: {layout_html_path}")
    print(f"Multitable layout stacked XLSX created: {layout_xlsx_path}")
    if layout_pdf_path.exists():
        print(f"Multitable layout PDF created: {layout_pdf_path}")
