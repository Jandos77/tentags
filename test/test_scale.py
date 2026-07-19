import io
from pathlib import Path
import sys

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import tentags
from demo_paths import demo_output_path


SCALE_DEMO_PREAMBLE = (
    '5,4,1,"#1977ff","dashed-1",0,28,'
    'scale(A1=2,3;C5=2,2;D3=3,5)'
)

SCALE_DEMO_STYLE = """style(
<cm><center><bg=blue><color=green><b>, , , </b></color></bg></cm>;
<color=blue><bg=white><i>, , , </i></bg></color>;
<color=yellow><bg=#f8fafc>, , , </bg></color>;
<bg=white>, , , </bg>;
<bg=yellow>, , , </bg></center>
)"""

SCALE_DEMO_DATA = """data(
Column A x3, Column B x1, Column C x2, Column D x5;
Row 2 x1, Standard, Standard, Standard;
Row 3 x3, Tall, Tall, Tall;
Row 4 x1, Standard, Standard, Standard;
Row 5 x2, Medium, Medium, Medium
)"""


def build_scale_demo_artifacts():
    html_output = demo_output_path("scale_grid_demo.html")
    xlsx_output = demo_output_path("scale_grid_demo.xlsx")
    pdf_output = demo_output_path("scale_grid_demo.pdf")

    model = tentags.compile(
        SCALE_DEMO_PREAMBLE,
        SCALE_DEMO_STYLE,
        SCALE_DEMO_DATA,
    )

    html_output.write_text(tentags.render_html(model), encoding="utf-8")
    tentags.render_xlsx(model, xlsx_output)
    tentags.render_pdf(model, str(pdf_output))

    return html_output, xlsx_output, pdf_output


def _data(rows, cols):
    values = []
    index = 1
    for _ in range(rows):
        row = []
        for _ in range(cols):
            row.append(f"V{index}")
            index += 1
        values.append(",".join(row))
    return f"data({';'.join(values)})"


def test_scale_is_an_optional_preamble_extension_for_parse_and_compile():
    formula = (
        '5,4,1,"black","solid-1",0,28,'
        'scale(A1=1,3;C5=2,2;D4=1,5),'
        f'{_data(5, 4)}'
    )

    parsed = tentags.parse(formula)
    compiled = tentags.compile(
        '5,4,1,"black","solid-1",0,28,scale(A1=1,3;C5=2,2;D4=1,5)',
        "style()",
        _data(5, 4),
    )

    for model in (parsed, compiled):
        assert model.row_scales == {4: 2}
        assert model.col_scales == {0: 3, 2: 2, 3: 5}


def test_scale_works_with_style_data_default_height_and_trailing_semicolon():
    model = tentags.parse(
        '2,2,1,"black","solid-1",0,scale(A1=2,3;),'
        'style(<b>,</b>;,),data(A,B;C,D)'
    )

    assert model.cell_height == 30
    assert model.row_scales == {0: 2}
    assert model.col_scales == {0: 3}
    assert model.cells[0][0].styles["font-weight"] == "bold"


def test_compile_accepts_scale_inside_preamble_dict():
    model = tentags.compile(
        {
            "rows": 2,
            "cols": 2,
            "cell_height": 28,
            "scale": {"A1": (2, 3)},
        },
        "style(,;,)",
        "data(A,B;C,D)",
    )

    assert model.row_scales == {0: 2}
    assert model.col_scales == {0: 3}


def test_scale_merges_repeated_rows_and_columns_by_axis_maximum():
    model = tentags.parse(
        '4,4,1,"black","solid-1",0,28,'
        'scale(A1=1,2;A3=3,1;A4=2,5;D3=2,4),'
        f'{_data(4, 4)}'
    )

    assert model.row_scales == {2: 3, 3: 2}
    assert model.col_scales == {0: 5, 3: 4}


def test_scale_accepts_lowercase_a1_and_stores_zero_based_sparse_maps():
    model = tentags.parse(
        '3,3,1,"black","solid-1",0,28,scale(a1=1,1;c3=4,2),'
        f'{_data(3, 3)}'
    )

    assert model.row_scales == {2: 4}
    assert model.col_scales == {2: 2}


@pytest.mark.parametrize("value", ["0", "6", "-1", "1.5", "3.0", "abc"])
@pytest.mark.parametrize("entry", ["A1={value},2", "A1=2,{value}"])
def test_scale_rejects_values_outside_integer_range_1_to_5(value, entry):
    formula = f'1,1,1,"black","solid",0,28,scale({entry.format(value=value)}),data(A)'

    with pytest.raises(tentags.ScaleError, match="integer values from 1 to 5"):
        tentags.parse(formula)


@pytest.mark.parametrize(
    "address",
    ["E1", "A6", "Z100", "A1:B2", "Summary", "Table!List!A1", "A0"],
)
def test_scale_rejects_non_local_or_out_of_bounds_addresses(address):
    formula = f'5,4,1,"black","solid",0,28,scale({address}=2,2),{_data(5, 4)}'

    with pytest.raises(tentags.ScaleError):
        tentags.parse(formula)


def test_scale_rejects_empty_duplicate_and_post_data_extensions():
    with pytest.raises(tentags.ScaleError, match="requires at least one"):
        tentags.parse('1,1,1,"black","solid",0,28,scale(),data(A)')

    with pytest.raises(tentags.ScaleError, match="only one scale"):
        tentags.parse('1,1,1,"black","solid",0,28,scale(A1=2,2),scale(A1=3,3),data(A)')

    with pytest.raises(tentags.ScaleError, match="before style"):
        tentags.parse('1,1,1,"black","solid",0,28,data(A),scale(A1=2,2)')

    with pytest.raises(tentags.ScaleError, match="cell_height greater than 0"):
        tentags.parse('1,1,1,"black","solid",0,0,scale(A1=2,1),data(A)')

    horizontal_only = tentags.parse(
        '1,2,1,"black","solid",0,0,scale(A1=1,3),data(A,B)'
    )
    assert horizontal_only.row_scales == {}
    assert horizontal_only.col_scales == {0: 3}


def test_serializer_preamble_scale_is_canonical_and_old_output_is_unchanged():
    legacy = tentags.serialize.preamble(
        5,
        4,
        border_color="black",
        border_style="solid-1",
        cell_height=28,
    )
    scaled = tentags.serialize.preamble(
        5,
        4,
        border_color="black",
        border_style="solid-1",
        cell_height=28,
        scale={"C5": (2, 2), "a1": (1, 3)},
    )

    assert legacy == '5,4,1,"black","solid-1",0,28'
    assert scaled == '5,4,1,"black","solid-1",0,28,scale(A1=1,3;C5=2,2)'


def test_serializer_rejects_invalid_scale_mapping():
    with pytest.raises(tentags.ScaleError, match="must be a dict"):
        tentags.serialize.preamble(2, 2, scale=[("A1", (1, 2))])
    with pytest.raises(tentags.ScaleError, match="must be a pair"):
        tentags.serialize.preamble(2, 2, scale={"A1": 2})
    with pytest.raises(tentags.ScaleError, match="integers from 1 to 5"):
        tentags.serialize.preamble(2, 2, scale={"A1": (1, 6)})
    with pytest.raises(tentags.ScaleError, match="outside"):
        tentags.serialize.preamble(2, 2, scale={"C1": (1, 2)})


def test_table_model_defaults_keep_direct_constructor_compatible():
    model = tentags.TableModel(1, 1, [[]], 1, "black", "solid", 0, 28)

    assert model.row_scales == {}
    assert model.col_scales == {}


def test_html_scale_emits_column_proportions_and_scaled_fixed_rows():
    model = tentags.parse(
        '2,3,1,"black","solid-1",0,28,scale(A1=2,3;C2=1,2),'
        f'{_data(2, 3)}'
    )

    html = tentags.render_html(model)

    assert '<col style="width:50%">' in html
    assert '<col style="width:16.666667%">' in html
    assert '<col style="width:33.333333%">' in html
    assert html.count("height:56px") == 4
    assert html.count("height:28px") == 4


def test_html_scale_preserves_stretching_image_contract():
    fixed = tentags.render(
        '1,1,1,"black","solid",0,28,scale(A1=3,1),'
        'data(<img src=logo.png w=120 h=auto>)'
    )
    stretching = tentags.render(
        '2,1,1,"black","solid",1,28,scale(A1=3,1),'
        'data(<img src=logo.png w=120 h=auto>;Text)'
    )

    assert 'height="84"' in fixed
    assert "height:84px" in fixed
    assert 'width="120"' not in fixed
    assert "width:auto;table-layout:auto" in stretching
    assert '<tr style="height:84px;">' in stretching


def test_xlsx_scale_sets_rows_columns_and_stacked_column_maximum():
    openpyxl = pytest.importorskip("openpyxl")
    from openpyxl.utils.units import DEFAULT_COLUMN_WIDTH
    tables = [
        {
            "document": "Demo",
            "table_name": "First",
            "sheet_name": "First",
            "preamble": '2,2,1,"black","solid-1",0,24,scale(A1=2,3)',
            "style": "style(,;,)",
            "data": "data(A,B;C,D)",
        },
        {
            "document": "Demo",
            "table_name": "Second",
            "sheet_name": "Second",
            "preamble": '2,2,1,"black","solid-1",0,24,scale(A1=1,5;B2=3,2)',
            "style": "style(,;,)",
            "data": "data(E,F;G,H)",
        },
    ]
    output = io.BytesIO()

    tentags.multitable_xlsx(
        tables,
        output,
        settings={"mode": "stacked", "show_titles": False, "gap": 1},
    )
    output.seek(0)
    ws = openpyxl.load_workbook(output)["Report"]

    assert ws.row_dimensions[1].height == 48
    assert ws.row_dimensions[5].height == 72
    assert ws.column_dimensions["A"].width == pytest.approx(DEFAULT_COLUMN_WIDTH * 5)
    assert ws.column_dimensions["B"].width == pytest.approx(DEFAULT_COLUMN_WIDTH * 2)


def test_pdf_scale_uses_available_width_and_scaled_row_heights():
    pytest.importorskip("reportlab")
    model = tentags.parse(
        '2,3,1,"black","solid-1",0,28,scale(A1=2,3;C2=1,2),'
        f'{_data(2, 3)}'
    )

    table = tentags._create_pdf_table_object(model, available_width=600)
    output = io.BytesIO()
    tentags.render_pdf(model, output)

    assert table._colWidths == pytest.approx([300, 100, 200])
    assert table._rowHeights == [56, 28]
    assert output.getvalue().startswith(b"%PDF")


def test_pdf_stretch_scale_uses_minimum_row_heights():
    pytest.importorskip("reportlab")
    model = tentags.parse(
        '2,1,1,"black","solid",1,28,scale(A1=3,1),data(Tall;Natural)'
    )

    table = tentags._create_pdf_table_object(model, available_width=200)

    assert table._rowHeights == [None, None]
    assert table._minRowHeights == [84, 0]


def test_pdf_supports_named_background_and_text_colors():
    colors = pytest.importorskip("reportlab.lib.colors")
    model = tentags.compile(
        '2,1,1,"blue","solid-1",0,28',
        "style(<bg=blue><color=white></color></bg>; <bg=yellow></bg>)",
        "data(Header; Warning)",
    )

    table = tentags._create_pdf_table_object(model, available_width=200)

    backgrounds = {
        (start, end): color
        for command, start, end, color in table._bkgrndcmds
        if command == "BACKGROUND"
    }
    assert backgrounds[((0, 0), (0, 0))] == colors.blue
    assert backgrounds[((0, 1), (0, 1))] == colors.yellow
    assert table._cellvalues[0][0].style.textColor == colors.white


def test_multitable_scale_renders_independently_to_html_and_pdf():
    tables = [
        {
            "document": "Demo",
            "table_name": "First",
            "sheet_name": "First",
            "preamble": '2,2,1,"black","solid-1",0,24,scale(A1=2,3)',
            "style": "style(,;,)",
            "data": "data(A,B;C,D)",
        },
        {
            "document": "Demo",
            "table_name": "Second",
            "sheet_name": "Second",
            "preamble": '2,2,1,"black","solid-1",0,24,scale(B1=1,4)',
            "style": "style(,;,)",
            "data": "data(E,F;G,H)",
        },
    ]

    html = tentags.multitable_html(
        tables,
        settings={"layout": "grid", "cols": 2, "tables_per_row": 2},
    )
    pdf = io.BytesIO()
    tentags.multitable_pdf(
        tables,
        pdf,
        settings={
            "tables_per_row": "auto",
            "tables_per_page": "auto",
            "page_break_after_each": False,
        },
    )

    assert html.count("<colgroup>") == 2
    assert pdf.getvalue().startswith(b"%PDF")


def test_validate_reports_scale_errors_without_raising():
    result = tentags.validate('1,1,1,"black","solid",0,28,scale(A1=1,6),data(A)')

    assert result["status"] == "error"
    assert "integer values from 1 to 5" in result["message"]


def test_scale_demo_creates_visible_html_xlsx_and_pdf_files():
    openpyxl = pytest.importorskip("openpyxl")
    pytest.importorskip("reportlab")

    html_output, xlsx_output, pdf_output = build_scale_demo_artifacts()

    assert html_output.exists()
    assert xlsx_output.exists()
    assert pdf_output.exists()
    assert "<colgroup>" in html_output.read_text(encoding="utf-8")
    assert xlsx_output.read_bytes().startswith(b"PK")
    assert pdf_output.read_bytes().startswith(b"%PDF")
    assert pdf_output.stat().st_size > 1000

    workbook = openpyxl.load_workbook(xlsx_output)
    sheet = workbook["Table"]
    assert sheet.row_dimensions[1].height == 56
    assert sheet.row_dimensions[3].height == 84
    assert sheet.row_dimensions[5].height == 56
    assert sheet.column_dimensions["A"].width > sheet.column_dimensions["B"].width
    assert sheet.column_dimensions["D"].width > sheet.column_dimensions["A"].width


if __name__ == "__main__":
    html_path, xlsx_path, pdf_path = build_scale_demo_artifacts()
    print(f"HTML created: {html_path}")
    print(f"XLSX created: {xlsx_path}")
    print(f"PDF created: {pdf_path}")
