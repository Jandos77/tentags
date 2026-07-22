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
    from reportlab.lib import colors

    model, html_output, xlsx_output, pdf_output = build_merge_content_artifacts()

    html = html_output.read_text(encoding="utf-8")
    assert 'colspan="3"' in html
    assert 'rowspan="2"' in html
    assert ">A</td>" in html
    assert ">D</td>" in html

    workbook = openpyxl.load_workbook(xlsx_output)
    sheet = workbook["Table"]
    merged_str_ranges = [str(r) for r in sheet.merged_cells.ranges]
    assert "A1:C1" in merged_str_ranges
    assert "A2:A3" in merged_str_ranges

    pdf_table = tentags._create_pdf_table_object(model, available_width=360)
    assert ('SPAN', (0, 0), (2, 0)) in pdf_table._spanCmds
    assert ('SPAN', (0, 1), (0, 2)) in pdf_table._spanCmds

    assert xlsx_output.read_bytes().startswith(b"PK")
    assert pdf_output.read_bytes().startswith(b"%PDF")
    assert pdf_output.stat().st_size > 1000


if __name__ == "__main__":
    _, html_path, xlsx_path, pdf_path = build_merge_content_artifacts()
    print(f"HTML created: {html_path}")
    print(f"XLSX created: {xlsx_path}")
    print(f"PDF created: {pdf_path}")
