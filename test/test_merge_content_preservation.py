from pathlib import Path
import sys

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import tentags
from demo_paths import demo_output_path


MERGE_FORMULA = '''
3,3,1,"black","solid-1",0,34,
style(
<center><bg=blue><color=white><b>, , </b></color></bg>;
<bg=white></bg>, <bg=#f8fafc></bg>, <bg=white></bg>;
<bg=yellow></bg>, <bg=#f8fafc></bg>, <bg=yellow></bg></center>
),
data(
<cm>A, B, C</cm>;
<rm>D</rm>, E, F;
<rm>G</rm>, H, I
)
'''


def build_merge_content_artifacts():
    html_output = demo_output_path("merge_content_preservation.html")
    xlsx_output = demo_output_path("merge_content_preservation.xlsx")
    pdf_output = demo_output_path("merge_content_preservation.pdf")

    model = tentags.parse(MERGE_FORMULA)
    html_output.write_text(tentags.render_html(model), encoding="utf-8")
    tentags.render_xlsx(model, xlsx_output)
    tentags.render_pdf(model, str(pdf_output))

    return model, html_output, xlsx_output, pdf_output


def test_cm_rm_preserve_all_cell_values_in_html_xlsx_and_pdf():
    openpyxl = pytest.importorskip("openpyxl")
    pytest.importorskip("reportlab")

    model, html_output, xlsx_output, pdf_output = build_merge_content_artifacts()
    expected = [["A", "B", "C"], ["D", "E", "F"], ["G", "H", "I"]]

    html = html_output.read_text(encoding="utf-8")
    for value in "ABCDEFGHI":
        assert f">{value}</td>" in html

    workbook = openpyxl.load_workbook(xlsx_output)
    sheet = workbook["Table"]
    actual_xlsx = [
        [sheet.cell(row=row, column=col).value for col in range(1, 4)]
        for row in range(1, 4)
    ]
    assert actual_xlsx == expected
    assert list(sheet.merged_cells.ranges) == []
    assert sheet["A1"].border.right.style is None
    assert sheet["B1"].border.left.style is None
    assert sheet["B1"].border.right.style is None
    assert sheet["C1"].border.left.style is None
    assert sheet["A2"].border.bottom.style is None
    assert sheet["A3"].border.top.style is None

    pdf_table = tentags._create_pdf_table_object(model, available_width=360)
    actual_pdf = [
        [cell.getPlainText() if hasattr(cell, "getPlainText") else cell for cell in row]
        for row in pdf_table._cellvalues
    ]
    assert actual_pdf == expected
    assert pdf_table._spanCmds == []
    assert not any(
        command[0] == "LINEBEFORE" and command[1] in ((1, 0), (2, 0))
        for command in pdf_table._linecmds
    )
    assert not any(
        command[0] == "LINEABOVE" and command[1] == (0, 2)
        for command in pdf_table._linecmds
    )

    assert xlsx_output.read_bytes().startswith(b"PK")
    assert pdf_output.read_bytes().startswith(b"%PDF")
    assert pdf_output.stat().st_size > 1000


if __name__ == "__main__":
    _, html_path, xlsx_path, pdf_path = build_merge_content_artifacts()
    print(f"HTML created: {html_path}")
    print(f"XLSX created: {xlsx_path}")
    print(f"PDF created: {pdf_path}")
