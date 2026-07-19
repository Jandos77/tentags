from io import BytesIO
from pathlib import Path
import sys

import pytest

import tentags
from demo_paths import demo_output_path


BORDER_CASES = [
    ("Solid Outer", "solid", "medium", None, "outer"),
    ("Solid Grid", "solid-1", "medium", None, "grid"),
    ("Solid None", "solid-0", "medium", None, "none"),
    ("Dashed Outer", "dashed", "dashed", [4, 3], "outer"),
    ("Dashed Grid", "dashed-1", "dashed", [4, 3], "grid"),
    ("Dashed None", "dashed-0", "dashed", [4, 3], "none"),
    ("Dotted Outer", "dotted", "dotted", [1, 2], "outer"),
    ("Dotted Grid", "dotted-1", "dotted", [1, 2], "grid"),
    ("Dotted None", "dotted-0", "dotted", [1, 2], "none"),
]


def _formula(border_style):
    return (
        f'3,3,1,"#334155","{border_style}",0,32,'
        'style(<bg=#dbeafe><color=red><b>, , </b></bg>; <bg=white>, , </bg>; <bg=#f8fafc>, , </color></bg>),'
        'data(<cm>A, B, C</cm>; <rm>D</rm>, E, F; <rm>G</rm>, H, I)'
    )


def _tables():
    return [
        {
            "document": "Border Styles",
            "table_name": name,
            "sheet_name": name,
            "title": f"{name} borders",
            "preamble": f'3,3,2,"#334155","{border_style}",0,32',
            "style": "style(<color=blue><bg=#dbeafe><b>, , </b></bg>; <bg=white>, , </bg>; <bg=#f8fafc>, , </color></bg>)",
            "data": "data(<cm>A, B, C</cm>; <rm>D</rm>, E, F; <rm>G</rm>, H, I)",
        }
        for name, border_style, _, _, _ in BORDER_CASES
    ]


def build_border_style_artifacts():
    html_output = demo_output_path("border_styles_demo.html")
    xlsx_output = demo_output_path("border_styles_demo.xlsx")
    pdf_output = demo_output_path("border_styles_demo.pdf")
    tables = _tables()

    html = tentags.multitable_html(
        tables,
        settings={"layout": "vertical", "gap": "24px", "full_page": True},
    )
    html_output.write_text(html, encoding="utf-8")
    tentags.multitable_xlsx(
        tables,
        xlsx_output,
        settings={"mode": "sheets", "show_titles": True},
    )
    tentags.multitable_pdf(
        tables,
        str(pdf_output),
        settings={
            "tables_per_row": 1,
            "tables_per_page": "auto",
            "page_break_after_each": False,
            "gap": 18,
        },
    )

    return html_output, xlsx_output, pdf_output


@pytest.mark.parametrize(
    "name,border_style,xlsx_style,pdf_dash,mode",
    BORDER_CASES,
)
def test_border_styles_are_preserved_in_html_xlsx_and_pdf(
    name,
    border_style,
    xlsx_style,
    pdf_dash,
    mode,
):
    openpyxl = pytest.importorskip("openpyxl")
    pytest.importorskip("reportlab")
    model = tentags.parse(_formula(border_style))
    css_style = border_style.split("-", 1)[0]
    expected_xlsx_style = "thin" if css_style == "solid" and model.border_width == 1 else xlsx_style

    html = tentags.render_html(model)
    css_border = f"border:{model.border_width}px {css_style} #334155;"
    if mode == "none":
        assert css_border not in html
    elif mode == "outer":
        assert html.count(css_border) == 1
    else:
        assert html.count(css_border) > 1

    xlsx = BytesIO()
    tentags.render_xlsx(model, xlsx)
    xlsx.seek(0)
    sheet = openpyxl.load_workbook(xlsx).active
    assert [sheet.cell(1, col).value for col in range(1, 4)] == ["A", "B", "C"]
    assert [sheet.cell(2, col).value for col in range(1, 4)] == ["D", "E", "F"]
    assert [sheet.cell(3, col).value for col in range(1, 4)] == ["G", "H", "I"]
    assert list(sheet.merged_cells.ranges) == []

    if mode == "none":
        for row in sheet.iter_rows(min_row=1, max_row=3, min_col=1, max_col=3):
            for cell in row:
                assert cell.border.left.style is None
                assert cell.border.right.style is None
                assert cell.border.top.style is None
                assert cell.border.bottom.style is None
    else:
        assert sheet["A1"].border.top.style == expected_xlsx_style
        assert sheet["A1"].border.left.style == expected_xlsx_style
        assert sheet["C3"].border.right.style == expected_xlsx_style
        assert sheet["C3"].border.bottom.style == expected_xlsx_style
        if mode == "outer":
            assert sheet["A1"].border.right.style is None
            assert sheet["A1"].border.bottom.style is None
            assert sheet["B2"].border.left.style is None
            assert sheet["B2"].border.top.style is None
        else:
            assert sheet["A1"].border.right.style is None
            assert sheet["B1"].border.left.style is None
            assert sheet["A2"].border.bottom.style is None
            assert sheet["A3"].border.top.style is None
            assert sheet["A2"].border.right.style == expected_xlsx_style
            assert sheet["B2"].border.left.style == expected_xlsx_style
            assert sheet["B2"].border.bottom.style == expected_xlsx_style
            assert sheet["B3"].border.top.style == expected_xlsx_style

    pdf_table = tentags._create_pdf_table_object(model, available_width=360)
    if mode == "none":
        assert pdf_table._linecmds == []
    else:
        assert pdf_table._linecmds
        assert all(command[6] == pdf_dash for command in pdf_table._linecmds)
        assert pdf_table._linecmds[0][0] == "BOX"
        if mode == "outer":
            assert len(pdf_table._linecmds) == 1
        else:
            assert not any(
                command[0] == "LINEBEFORE" and command[1] in ((1, 0), (2, 0))
                for command in pdf_table._linecmds
            )
            assert not any(
                command[0] == "LINEABOVE" and command[1] == (0, 2)
                for command in pdf_table._linecmds
            )
            assert any(
                command[0] == "LINEBEFORE" and command[1] == (1, 1)
                for command in pdf_table._linecmds
            )
            assert any(
                command[0] == "LINEABOVE" and command[1] == (1, 2)
                for command in pdf_table._linecmds
            )


def test_border_style_demo_creates_html_xlsx_and_pdf_files():
    openpyxl = pytest.importorskip("openpyxl")
    pytest.importorskip("reportlab")
    html_output, xlsx_output, pdf_output = build_border_style_artifacts()

    html = html_output.read_text(encoding="utf-8")
    assert html.startswith("<!DOCTYPE html>")
    assert html.count("<table ") == len(BORDER_CASES)
    for name, _, _, _, _ in BORDER_CASES:
        assert f"{name} borders" in html

    assert xlsx_output.read_bytes().startswith(b"PK")
    workbook = openpyxl.load_workbook(xlsx_output)
    assert workbook.sheetnames == [name for name, _, _, _, _ in BORDER_CASES]

    assert pdf_output.read_bytes().startswith(b"%PDF")
    assert pdf_output.stat().st_size > 1000


if __name__ == "__main__":
    html_path, xlsx_path, pdf_path = build_border_style_artifacts()
    print(f"HTML created: {html_path}")
    print(f"XLSX created: {xlsx_path}")
    print(f"PDF created: {pdf_path}")
