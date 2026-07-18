from pathlib import Path
import sys

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import tentags
from demo_paths import demo_output_path


ALL_TAGS_FORMULA = '''
5,4,1,"#64748b","solid-1",0,30,
data(
<b>Bold</b>, <i>Italic</i>, <b><i>Bold Italic</i></b>, <u>Underline</u>;
<s>Strike</s>, <color=red>Red</color>, <bg=yellow>Yellow</bg>, <fs=18>Large</fs>;
<left>Left</left>, <center>Center</center>, <right>Right</right>, <url=https://example.com>Link</url>;
<mark=Source>Marked, <value=A4>, <img src=missing.png w=20 h=auto m=2>, Plain;
<cm>Column group, Second cell</cm>, Third cell, Fourth cell
)
'''


def build_all_tag_artifacts():
    html_output = demo_output_path("all_tags.html")
    xlsx_output = demo_output_path("all_tags.xlsx")
    pdf_output = demo_output_path("all_tags.pdf")

    model = tentags.parse(ALL_TAGS_FORMULA)
    html_output.write_text(tentags.render_html(model), encoding="utf-8")
    tentags.render_xlsx(model, xlsx_output)
    tentags.render_pdf(model, str(pdf_output))
    return model, html_output, xlsx_output, pdf_output


def test_all_content_and_presentation_tags_reach_ir():
    model = tentags.parse(ALL_TAGS_FORMULA)

    assert model.cells[0][0].styles["font-weight"] == "bold"
    assert model.cells[0][1].styles["font-style"] == "italic"
    assert model.cells[0][2].styles["font-weight"] == "bold"
    assert model.cells[0][2].styles["font-style"] == "italic"
    assert model.cells[0][3].styles["text-decoration"] == "underline"
    assert model.cells[1][0].styles["text-decoration"] == "line-through"
    assert model.cells[1][1].styles["color"] == "red"
    assert model.cells[1][2].styles["background-color"] == "yellow"
    assert model.cells[1][3].styles["font-size"] == "18px"
    assert [model.cells[2][col].styles["text-align"] for col in range(3)] == ["left", "center", "right"]
    assert model.cells[2][3].link.target == "https://example.com"
    assert model.cells[3][0].mark == "Source"
    assert model.cells[3][1].raw_expr == "Marked"
    assert model.cells[3][2].images == [{"src": "missing.png", "w": "20", "h": "auto", "m": "2"}]
    assert model.cells[4][0].cm_block_id is not None
    assert model.cells[4][0].border_flags & tentags.BorderFlags.HIDE_RIGHT
    assert model.cells[4][1].border_flags & tentags.BorderFlags.HIDE_LEFT


def test_rm_tag_spans_rows_without_losing_content():
    model = tentags.parse(
        '3,2,1,"#000","solid-1",0,28,data(<rm>A1,A2;B1,B2;C1,C2</rm>)'
    )

    assert [[cell.raw_expr for cell in row] for row in model.cells] == [
        ["A1", "A2"],
        ["B1", "B2"],
        ["C1", "C2"],
    ]
    assert model.cells[0][0].border_flags & tentags.BorderFlags.HIDE_BOTTOM
    assert model.cells[1][0].border_flags & tentags.BorderFlags.HIDE_TOP
    assert model.cells[1][0].border_flags & tentags.BorderFlags.HIDE_BOTTOM
    assert model.cells[2][0].border_flags & tentags.BorderFlags.HIDE_TOP


def test_all_tags_render_to_html_xlsx_and_pdf():
    openpyxl = pytest.importorskip("openpyxl")
    model, html_output, xlsx_output, pdf_output = build_all_tag_artifacts()

    html = html_output.read_text(encoding="utf-8")
    assert "font-weight:bold;" in html
    assert "font-style:italic;" in html
    assert "text-decoration:underline;" in html
    assert "text-decoration:line-through;" in html
    assert "color:red;" in html
    assert "background-color:yellow;" in html
    assert "font-size:18px;" in html
    assert 'href="https://example.com"' in html
    assert 'id="tt-mark-Source"' in html
    assert 'src="missing.png"' in html
    assert "margin:2px" in html

    workbook = openpyxl.load_workbook(xlsx_output)
    sheet = workbook["Table"]
    assert sheet["A1"].font.bold is True
    assert sheet["B1"].font.italic is True
    assert sheet["C1"].font.bold is True and sheet["C1"].font.italic is True
    assert sheet["D1"].font.underline == "single"
    assert sheet["A2"].font.strike is True
    assert sheet["B2"].font.color.rgb.lower().endswith("ff0000")
    assert sheet["C2"].fill.start_color.rgb.lower().endswith("ffff00")
    assert sheet["D2"].font.sz == 18
    assert [sheet.cell(3, col).alignment.horizontal for col in range(1, 4)] == ["left", "center", "right"]
    assert sheet["D3"].hyperlink.target == "https://example.com"
    assert sheet["B4"].value == "Marked"
    assert sheet["C4"].value == "missing.png"

    pdf_fonts = tentags._pdf_font_names()
    assert pdf_fonts["bold"] != pdf_fonts["regular"]
    assert pdf_fonts["italic"] != pdf_fonts["regular"]
    assert pdf_fonts["bold_italic"] not in (pdf_fonts["regular"], pdf_fonts["bold"], pdf_fonts["italic"])
    pdf_table = tentags._create_pdf_table_object(model)
    assert pdf_table._cellvalues[0][0].style.fontName == pdf_fonts["bold"]
    assert pdf_table._cellvalues[0][1].style.fontName == pdf_fonts["italic"]
    assert pdf_table._cellvalues[0][2].style.fontName == pdf_fonts["bold_italic"]
    assert pdf_output.read_bytes().startswith(b"%PDF")
    assert pdf_output.stat().st_size > 1000


if __name__ == "__main__":
    _, html_path, xlsx_path, pdf_path = build_all_tag_artifacts()
    print(f"HTML created: {html_path}")
    print(f"XLSX created: {xlsx_path}")
    print(f"PDF created: {pdf_path}")
