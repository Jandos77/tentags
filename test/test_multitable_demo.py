from pathlib import Path
import re
import sys

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import tentags
from demo_paths import demo_output_path

TABLE_ORDER = [
    "Dashboard!Menu",
    "Invoice!Items",
    "CRM!Customers",
    "Report!Sales",
]

TABLE_COLUMN_SETTINGS = {
    "Dashboard!Menu": ["Section", "Target", "Owner", "Status"],
    "Invoice!Items": ["Item", "Qty", "Unit Price", "Total"],
    "CRM!Customers": ["Customer", "Segment", "Revenue", "Status"],
    "Report!Sales": ["Month", "Orders", "Revenue", "Status"],
}

HTML_SETTINGS = {
    "output": demo_output_path("multitable_demo.html"),
    "table_order": TABLE_ORDER,
    "columns": TABLE_COLUMN_SETTINGS,
    "tables_per_row": 2,
    "html_title": "Multitable Demo",
    "layout": "grid",
    "cols": 2,
    "gap": "30px",
    "full_page": True,
}

XLSX_SHEETS_SETTINGS = {
    "output": demo_output_path("multitable_demo.xlsx"),
    "table_order": TABLE_ORDER,
    "columns": TABLE_COLUMN_SETTINGS,
    "mode": "sheets",
}

XLSX_STACKED_SETTINGS = {
    "output": demo_output_path("multitable_demo_stacked.xlsx"),
    "table_order": TABLE_ORDER,
    "columns": TABLE_COLUMN_SETTINGS,
    "tables_per_sheet": "all",
    "stacked_sheet_name": "Demo Report",
    "mode": "stacked",
    "gap": 2,
    "show_titles": True,
}

PDF_SETTINGS = {
    "output": demo_output_path("multitable_demo.pdf"),
    "table_order": TABLE_ORDER,
    "columns": TABLE_COLUMN_SETTINGS,
    "tables_per_row": "auto",
    "tables_per_page": "auto",
    "gap": 16,
    "page_size": "A4",
    "orientation": "landscape",
    "page_break_after_each": False,
    "margins": (24, 24, 36, 36),
}


def _multitable_demo_tables():
    tables = [
        {
            "document": "Dashboard",
            "table_name": "Menu",
            "sheet_name": "Menu",
            "title": "Dashboard Menu",
            "preamble": '4,4,1,"#1e3a8a","solid-1",0,28',
            "style": """
style(

<bg=#1e3a8a><color=#ffffff><b></b></color></bg>,
<bg=#1e3a8a><color=#ffffff><b></b></color></bg>,
<bg=#1e3a8a><color=#ffffff><b></b></color></bg>,
<bg=#1e3a8a><color=#ffffff><b></b></color></bg>;

<bg=#eff6ff></bg>,
<bg=#eff6ff></bg>,
<bg=#eff6ff></bg>,
<bg=#dcfce7><b></b></bg>;

<bg=#ffffff></bg>,
<bg=#ffffff></bg>,
<bg=#ffffff></bg>,
<bg=#dcfce7><b></b></bg>;

<bg=#eff6ff></bg>,
<bg=#eff6ff></bg>,
<bg=#eff6ff></bg>,
<bg=#fef3c7><b></b></bg>

)
""",
            "data": """
data(

<center><b>Section</b></center>,
<center><b>Target</b></center>,
<center><b>Owner</b></center>,
<center><b>Status</b></center>;

Invoice,
<url=goto:Invoice!Items!A1>Invoice</url>,
Finance,
Ready;

Customers,
<url=goto:CRM!Customers!A1>Customers</url>,
Sales,
Ready;

Sales,
<url=goto:Report!Sales!A1>Sales Report</url>,
Analytics,
Review

)
""",
        },
        {
            "document": "Invoice",
            "table_name": "Items",
            "sheet_name": "Items",
            "title": "Invoice Items",
            "preamble": '5,4,1,"#92400e","solid-1",0,28',
            "style": """
style(

<bg=#92400e><color=#ffffff><b></b></color></bg>,
<bg=#92400e><color=#ffffff><b></b></color></bg>,
<bg=#92400e><color=#ffffff><b></b></color></bg>,
<bg=#92400e><color=#ffffff><b></b></color></bg>;

<bg=#fff7ed></bg>,
<bg=#fff7ed></bg>,
<bg=#fff7ed></bg>,
<bg=#fff7ed></bg>;

<bg=#ffffff></bg>,
<bg=#ffffff></bg>,
<bg=#ffffff></bg>,
<bg=#ffffff></bg>;

<bg=#fff7ed></bg>,
<bg=#fff7ed></bg>,
<bg=#fff7ed></bg>,
<bg=#fff7ed></bg>;

<bg=#ffedd5><b></b></bg>,
<bg=#ffedd5></bg>,
<bg=#ffedd5></bg>,
<bg=#ffedd5><b></b></bg>

)
""",
            "data": """
data(

<center><b>Item</b></center>,
<center><b>Qty</b></center>,
<center><b>Unit Price</b></center>,
<center><b>Total</b></center>;

Paper,
<right>10</right>,
<right>2.50</right>,
<right>25.00</right>;

Pen,
<right>5</right>,
<right>1.60</right>,
<right>8.00</right>;

Folder,
<right>3</right>,
<right>4.00</right>,
<right>12.00</right>;

<mark=InvoiceTotal><b>Total</b>,
,
,
<right><b>45.00</b></right>

)
""",
        },
        {
            "document": "CRM",
            "table_name": "Customers",
            "sheet_name": "Customers",
            "title": "CRM Customers",
            "preamble": '4,4,1,"#166534","solid-1",0,28',
            "style": """
style(

<bg=#166534><color=#ffffff><b></b></color></bg>,
<bg=#166534><color=#ffffff><b></b></color></bg>,
<bg=#166534><color=#ffffff><b></b></color></bg>,
<bg=#166534><color=#ffffff><b></b></color></bg>;

<bg=#ecfdf5></bg>,
<bg=#ecfdf5></bg>,
<bg=#ecfdf5></bg>,
<bg=#dcfce7><b></b></bg>;

<bg=#ffffff></bg>,
<bg=#ffffff></bg>,
<bg=#ffffff></bg>,
<bg=#d1fae5><b></b></bg>;

<bg=#ecfdf5></bg>,
<bg=#ecfdf5></bg>,
<bg=#ecfdf5></bg>,
<bg=#fef3c7><b></b></bg>

)
""",
            "data": """
data(

<center><b>Customer</b></center>,
<center><b>Segment</b></center>,
<center><b>Revenue</b></center>,
<center><b>Status</b></center>;

Alice,
Enterprise,
<right>125000</right>,
Active;

Bob,
SMB,
<right>42000</right>,
VIP;

<mark=Summary>Carol,
Midmarket,
<right>76000</right>,
Review

)
""",
        },
        {
            "document": "Report",
            "table_name": "Sales",
            "sheet_name": "Sales",
            "title": "Sales Report",
            "preamble": '5,4,1,"#0f766e","solid-1",0,28',
            "style": """
style(

<bg=#0f766e><color=#ffffff><b></b></color></bg>,
<bg=#0f766e><color=#ffffff><b></b></color></bg>,
<bg=#0f766e><color=#ffffff><b></b></color></bg>,
<bg=#0f766e><color=#ffffff><b></b></color></bg>;

<bg=#ecfeff></bg>,
<bg=#ecfeff></bg>,
<bg=#ecfeff></bg>,
<bg=#dcfce7><b></b></bg>;

<bg=#ffffff></bg>,
<bg=#ffffff></bg>,
<bg=#ffffff></bg>,
<bg=#dcfce7><b></b></bg>;

<bg=#ecfeff></bg>,
<bg=#ecfeff></bg>,
<bg=#ecfeff></bg>,
<bg=#dcfce7><b></b></bg>;

<bg=#ffffff></bg>,
<bg=#ffffff></bg>,
<bg=#ffffff></bg>,
<bg=#dbeafe><b></b></bg>

)
""",
            "data": """
data(

<center><b>Month</b></center>,
<center><b>Orders</b></center>,
<center><b>Revenue</b></center>,
<center><b>Status</b></center>;

January,
<right>120</right>,
<right>2500</right>,
Closed;

February,
<right>145</right>,
<right>3100</right>,
Closed;

March,
<right>160</right>,
<right>3550</right>,
Closed;

April,
<right>175</right>,
<right>3900</right>,
Forecast

)
""",
        },
    ]
    return tables


def _table_key(table):
    return f"{table['document']}!{table['table_name']}"


def build_multitable_demo_artifacts():
    html_output = HTML_SETTINGS["output"]
    xlsx_output = XLSX_SHEETS_SETTINGS["output"]
    stacked_xlsx_output = XLSX_STACKED_SETTINGS["output"]
    pdf_output = PDF_SETTINGS["output"]

    assert HTML_SETTINGS["table_order"] == XLSX_SHEETS_SETTINGS["table_order"]
    assert HTML_SETTINGS["table_order"] == XLSX_STACKED_SETTINGS["table_order"]
    assert HTML_SETTINGS["table_order"] == PDF_SETTINGS["table_order"]
    assert HTML_SETTINGS["columns"] == XLSX_SHEETS_SETTINGS["columns"]
    assert HTML_SETTINGS["columns"] == XLSX_STACKED_SETTINGS["columns"]
    assert HTML_SETTINGS["columns"] == PDF_SETTINGS["columns"]
    assert HTML_SETTINGS["cols"] == HTML_SETTINGS["tables_per_row"]
    assert PDF_SETTINGS["tables_per_row"] == "auto"
    assert PDF_SETTINGS["tables_per_page"] == "auto"

    tables = _multitable_demo_tables()

    tentags.multitable_html(tables, settings=HTML_SETTINGS)

    pytest.importorskip("openpyxl")
    tentags.multitable_xlsx(tables, settings=XLSX_SHEETS_SETTINGS)
    tentags.multitable_xlsx(tables, settings=XLSX_STACKED_SETTINGS)

    if tentags.features()["pdf"]:
        tentags.multitable_pdf(tables, settings=PDF_SETTINGS)

    return html_output, xlsx_output, stacked_xlsx_output, pdf_output


def test_multitable_demo_generates_visible_artifacts():
    html_output, xlsx_output, stacked_xlsx_output, pdf_output = build_multitable_demo_artifacts()

    assert html_output.exists()
    assert xlsx_output.exists()
    assert stacked_xlsx_output.exists()
    assert html_output.read_text(encoding="utf-8").startswith("<!DOCTYPE html>")
    assert xlsx_output.read_bytes().startswith(b"PK")
    assert stacked_xlsx_output.read_bytes().startswith(b"PK")
    if pdf_output.exists():
        data = pdf_output.read_bytes()
        assert data.startswith(b"%PDF")
        assert len(data) > 1000


def test_multitable_demo_has_four_separate_tables_and_sheets():
    openpyxl = pytest.importorskip("openpyxl")
    html_output, xlsx_output, _, _ = build_multitable_demo_artifacts()

    html = html_output.read_text(encoding="utf-8")
    wb = openpyxl.load_workbook(xlsx_output)

    assert html.count("<table ") == len(HTML_SETTINGS["table_order"])
    assert wb.sheetnames == ["Menu", "Items", "Customers", "Sales"]
    assert wb["Menu"]["B2"].hyperlink.target == "#Items!A1"
    assert wb["Menu"]["B3"].hyperlink.target == "#Customers!A1"
    assert wb["Menu"]["B4"].hyperlink.target == "#Sales!A1"


def test_multitable_demo_html_and_xlsx_settings_are_applied():
    openpyxl = pytest.importorskip("openpyxl")
    html_output, _, stacked_xlsx_output, _ = build_multitable_demo_artifacts()

    html = html_output.read_text(encoding="utf-8")
    wb = openpyxl.load_workbook(stacked_xlsx_output)
    ws = wb[XLSX_STACKED_SETTINGS["stacked_sheet_name"]]

    assert "display: grid;" in html
    assert f"grid-template-columns: repeat({HTML_SETTINGS['tables_per_row']}, 1fr);" in html
    assert "gap: 30px;" in html
    assert "<title>Multitable Demo</title>" in html
    assert html.startswith("<!DOCTYPE html>")

    assert wb.sheetnames == [XLSX_STACKED_SETTINGS["stacked_sheet_name"]]
    assert ws["A1"].value == "Dashboard Menu"
    assert ws["A8"].value == "Invoice Items"
    assert ws["A16"].value == "CRM Customers"
    assert ws["A23"].value == "Sales Report"
    assert ws["B3"].hyperlink.target == "#'Demo Report'!A9"
    assert ws["B4"].hyperlink.target == "#'Demo Report'!A17"
    assert ws["B5"].hyperlink.target == "#'Demo Report'!A24"


def test_multitable_demo_table_order_and_columns_are_explicit():
    openpyxl = pytest.importorskip("openpyxl")
    html_output, xlsx_output, stacked_xlsx_output, _ = build_multitable_demo_artifacts()

    html = html_output.read_text(encoding="utf-8")
    wb = openpyxl.load_workbook(xlsx_output)
    stacked_wb = openpyxl.load_workbook(stacked_xlsx_output)
    stacked_ws = stacked_wb[XLSX_STACKED_SETTINGS["stacked_sheet_name"]]

    html_ids_in_order = [
        html.index('id="tt-Dashboard-Menu-A1"'),
        html.index('id="tt-Invoice-Items-A1"'),
        html.index('id="tt-CRM-Customers-A1"'),
        html.index('id="tt-Report-Sales-A1"'),
    ]

    assert html_ids_in_order == sorted(html_ids_in_order)
    assert wb.sheetnames == [key.split("!", 1)[1] for key in XLSX_SHEETS_SETTINGS["table_order"]]

    assert [wb["Menu"].cell(row=1, column=col).value for col in range(1, 5)] == TABLE_COLUMN_SETTINGS["Dashboard!Menu"]
    assert [wb["Items"].cell(row=1, column=col).value for col in range(1, 5)] == TABLE_COLUMN_SETTINGS["Invoice!Items"]
    assert [wb["Customers"].cell(row=1, column=col).value for col in range(1, 5)] == TABLE_COLUMN_SETTINGS["CRM!Customers"]
    assert [wb["Sales"].cell(row=1, column=col).value for col in range(1, 5)] == TABLE_COLUMN_SETTINGS["Report!Sales"]

    assert [stacked_ws.cell(row=2, column=col).value for col in range(1, 5)] == TABLE_COLUMN_SETTINGS["Dashboard!Menu"]
    assert [stacked_ws.cell(row=9, column=col).value for col in range(1, 5)] == TABLE_COLUMN_SETTINGS["Invoice!Items"]
    assert [stacked_ws.cell(row=17, column=col).value for col in range(1, 5)] == TABLE_COLUMN_SETTINGS["CRM!Customers"]
    assert [stacked_ws.cell(row=24, column=col).value for col in range(1, 5)] == TABLE_COLUMN_SETTINGS["Report!Sales"]


def test_multitable_export_settings_are_validated_by_library():
    tables = _multitable_demo_tables()

    bad_order_settings = dict(HTML_SETTINGS)
    bad_order_settings["table_order"] = ["Missing!List"]
    with pytest.raises(ValueError, match="Unknown table_order entries"):
        tentags.multitable_html(tables, settings=bad_order_settings)

    bad_columns_settings = dict(HTML_SETTINGS)
    bad_columns = dict(TABLE_COLUMN_SETTINGS)
    bad_columns["Dashboard!Menu"] = ["Wrong", "Columns"]
    bad_columns_settings["columns"] = bad_columns
    with pytest.raises(ValueError, match="Column settings"):
        tentags.multitable_html(tables, settings=bad_columns_settings)

    bad_pdf_settings = dict(PDF_SETTINGS)
    bad_pdf_settings["tables_per_row"] = "wide"
    with pytest.raises(ValueError, match='tables_per_row must be a positive integer or "auto"'):
        tentags.multitable_pdf(tables, settings=bad_pdf_settings)

    bad_pdf_settings = dict(PDF_SETTINGS)
    bad_pdf_settings["tables_per_page"] = "many"
    with pytest.raises(ValueError, match='tables_per_page must be a positive integer or "auto"'):
        tentags.multitable_pdf(tables, settings=bad_pdf_settings)


def test_multitable_demo_marks_and_pdf_are_valid():
    html_output, _, _, pdf_output = build_multitable_demo_artifacts()
    html = html_output.read_text(encoding="utf-8")

    assert 'id="tt-Invoice-Items-mark-InvoiceTotal"' in html
    assert 'id="tt-CRM-Customers-mark-Summary"' in html

    if pdf_output.exists():
        data = pdf_output.read_bytes()
        media_boxes = re.findall(rb"/MediaBox\s*\[\s*0\s+0\s+([0-9.]+)\s+([0-9.]+)\s*\]", data)
        page_count = len(re.findall(rb"/Type\s*/Page\b", data))
        assert data.startswith(b"%PDF")
        assert page_count >= 1
        assert page_count < len(PDF_SETTINGS["table_order"])
        assert media_boxes
        width, height = (float(value) for value in media_boxes[0])
        assert width > height
        assert width > 800
        assert height > 500


if __name__ == "__main__":
    html_path, xlsx_path, stacked_xlsx_path, pdf_path = build_multitable_demo_artifacts()
    print(f"HTML created: {html_path}")
    print(f"XLSX created: {xlsx_path}")
    print(f"Stacked XLSX created: {stacked_xlsx_path}")
    if pdf_path.exists():
        print(f"PDF created: {pdf_path}")
