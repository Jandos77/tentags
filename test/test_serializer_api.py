import io

import pytest

import tentags


def test_dumps_preamble_serializes_canonical_preamble():
    preamble = tentags.dumps_preamble(
        rows=9,
        cols=5,
        border_width=1,
        border_color="#64748b",
        border_style="solid-1",
        stretch=0,
        cell_height=28,
    )

    assert preamble == '9,5,1,"#64748b","solid-1",0,28'


def test_serialize_namespace_matches_top_level_serializers():
    rows = [["A", "B"], ["C", None]]
    style_rows = [["<bg=#ffffff></bg>", "<bg=#dcfce7></bg>"]]

    assert "serialize" in tentags.__all__
    assert tentags.serialize.preamble(2, 2) == tentags.dumps_preamble(2, 2)
    assert tentags.serialize.data(rows) == tentags.dumps_data(rows)
    assert tentags.serialize.style(style_rows) == tentags.dumps_style(style_rows)


def test_dumps_data_serializes_matrix_and_preserves_markup():
    data = tentags.dumps_data(
        [
            ["Name", "<right><b>Value</b></right>"],
            ["Alice", 100],
            ["Empty", None],
        ],
        expected_rows=3,
        expected_cols=2,
    )

    assert data == (
        "data(\n"
        "Name, <right><b>Value</b></right>;\n"
        "Alice, 100;\n"
        "Empty, \n"
        ")"
    )


def test_dumps_style_serializes_matrix():
    style = tentags.dumps_style(
        [
            ["<bg=#0f172a><b></b></bg>", "<bg=#0f172a><b></b></bg>"],
            ["<bg=#ffffff></bg>", "<bg=#dcfce7></bg>"],
        ],
        expected_rows=2,
        expected_cols=2,
    )

    assert style == (
        "style(\n"
        "<bg=#0f172a><b></b></bg>, <bg=#0f172a><b></b></bg>;\n"
        "<bg=#ffffff></bg>, <bg=#dcfce7></bg>\n"
        ")"
    )


def test_serializer_api_roundtrips_through_compile_and_renderers():
    openpyxl = pytest.importorskip("openpyxl")
    from reportlab.lib import colors

    rows = [
        {"period": "January", "revenue": 125000, "status": "Closed"},
        {"period": "July", "revenue": 158900, "status": "Review"},
    ]
    status_colors = {
        "Closed": {"bg": "#dcfce7", "fg": "#166534"},
        "Review": {"bg": "#fef3c7", "fg": "#92400e"},
    }

    preamble = tentags.serialize.preamble(len(rows) + 1, 3, border_color="#64748b", border_style="solid-1", cell_height=28)
    style_rows = [["<bg=#0f172a><b></b></bg>"] * 3]
    data_rows = [["<color=#ffffff>Period</color>", "<right><color=#ffffff>Revenue</color></right>", "<center><color=#ffffff>Status</color></center>"]]

    for index, row in enumerate(rows):
        base_bg = "#ffffff" if index % 2 == 0 else "#f8fafc"
        style_rows.append(
            [
                f"<bg={base_bg}></bg>",
                f"<bg={base_bg}></bg>",
                f"<bg={status_colors[row['status']]['bg']}></bg>",
            ]
        )
        data_rows.append(
            [
                row["period"],
                f"<right>{row['revenue']}</right>",
                f"<center><color={status_colors[row['status']]['fg']}>{row['status']}</color></center>",
            ]
        )

    style = tentags.serialize.style(style_rows, expected_rows=3, expected_cols=3)
    data = tentags.serialize.data(data_rows, expected_rows=3, expected_cols=3)
    model = tentags.compile(preamble, style, data)

    html = tentags.render_html(model)
    pdf = io.BytesIO()
    xlsx = io.BytesIO()
    tentags.render_pdf(model, pdf)
    tentags.render_xlsx(model, xlsx)

    assert model.rows == 3
    assert model.cols == 3
    assert model.cells[0][0].styles["color"] == "#ffffff"
    assert model.cells[1][2].styles["color"] == "#166534"
    assert model.cells[2][2].styles["color"] == "#92400e"
    assert "#dcfce7" in html
    assert "#fef3c7" in html
    assert "color:#ffffff;" in html
    assert "color:#166534;" in html
    assert "color:#92400e;" in html

    xlsx.seek(0)
    sheet = openpyxl.load_workbook(xlsx)["Table"]
    assert sheet["A1"].font.color.rgb.lower() == "ffffffff"
    assert sheet["C2"].font.color.rgb.lower() == "ff166534"
    assert sheet["C3"].font.color.rgb.lower() == "ff92400e"

    pdf_table = tentags._create_pdf_table_object(model)
    assert pdf_table._cellvalues[0][0].style.textColor == colors.white
    assert pdf_table._cellvalues[1][2].style.textColor == colors.HexColor("#166534")
    assert pdf_table._cellvalues[2][2].style.textColor == colors.HexColor("#92400e")
    assert pdf.getvalue().startswith(b"%PDF")
    assert len(xlsx.getvalue()) > 1000


def test_serializer_api_works_inside_multitable_exports():
    menu_rows = [
        ["Section", "Target"],
        ["Invoice", "<url=goto:Invoice!Items!A1>Open</url>"],
    ]
    invoice_rows = [
        ["Item", "Total"],
        ["Paper", "<url=goto:Dashboard!Menu!A1>$25</url>"],
    ]

    tables = [
        {
            "document": "Dashboard",
            "table_name": "Menu",
            "sheet_name": "Menu",
            "title": "Dashboard Menu",
            "preamble": tentags.serialize.preamble(len(menu_rows), 2, border_color="#64748b", border_style="solid-1", cell_height=24),
            "style": tentags.serialize.style(
                [
                    ["<bg=#dbeafe><b></b></bg>", "<bg=#dbeafe><b></b></bg>"],
                    ["<bg=#ffffff></bg>", "<bg=#ffffff></bg>"],
                ],
                expected_rows=len(menu_rows),
                expected_cols=2,
            ),
            "data": tentags.serialize.data(menu_rows, expected_rows=len(menu_rows), expected_cols=2),
        },
        {
            "document": "Invoice",
            "table_name": "Items",
            "sheet_name": "Items",
            "title": "Invoice Items",
            "preamble": tentags.serialize.preamble(len(invoice_rows), 2, border_color="#64748b", border_style="solid-1", cell_height=24),
            "style": tentags.serialize.style(
                [
                    ["<bg=#ffedd5><b></b></bg>", "<bg=#ffedd5><b></b></bg>"],
                    ["<bg=#ffffff></bg>", "<bg=#ffffff></bg>"],
                ],
                expected_rows=len(invoice_rows),
                expected_cols=2,
            ),
            "data": tentags.serialize.data(invoice_rows, expected_rows=len(invoice_rows), expected_cols=2),
        },
    ]
    settings = {
        "table_order": ["Dashboard!Menu", "Invoice!Items"],
        "columns": {
            "Dashboard!Menu": ["Section", "Target"],
            "Invoice!Items": ["Item", "Total"],
        },
        "full_page": True,
        "layout": "grid",
        "cols": 2,
        "tables_per_row": 2,
    }

    html = tentags.multitable_html(tables, settings=settings)
    xlsx = io.BytesIO()
    pdf = io.BytesIO()
    tentags.multitable_xlsx(
        tables,
        xlsx,
        settings={**settings, "mode": "sheets", "tables_per_sheet": 1},
    )
    tentags.multitable_pdf(
        tables,
        pdf,
        settings={
            **settings,
            "tables_per_row": "auto",
            "tables_per_page": "auto",
            "page_break_after_each": False,
        },
    )

    assert html.count("<table ") == 2
    assert 'href="#tt-Invoice-Items-A1"' in html
    assert len(xlsx.getvalue()) > 1000
    assert pdf.getvalue().startswith(b"%PDF")


def test_serializer_api_validates_expected_dimensions():
    with pytest.raises(ValueError, match="data expected 3 rows"):
        tentags.dumps_data([["A", "B"]], expected_rows=3)

    with pytest.raises(ValueError, match="style row 2 expected 2 cells"):
        tentags.dumps_style([["A", "B"], ["C"]], expected_cols=2)


def test_dumps_preamble_validates_integer_fields():
    with pytest.raises(ValueError, match="rows must be a positive integer"):
        tentags.dumps_preamble(0, 2)

    with pytest.raises(ValueError, match="stretch must be a non-negative integer"):
        tentags.dumps_preamble(2, 2, stretch=True)

