from pathlib import Path
import sys

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import tentags
from demo_paths import demo_output_path


IMG_FORMULA = """
1,2,1,"#64748b","solid-1",1,28,
data(
<img src=D:/TenTags/tentags_logo.png w=120 h=auto m=15>,
<img src=https://pycells.com//assets/img/PyCells_mds.png w=120 h=auto m=15>
)
"""


def build_img_artifacts():
    html_output = demo_output_path("img_local_external.html")
    xlsx_output = demo_output_path("img_local_external.xlsx")
    pdf_output = demo_output_path("img_local_external.pdf")

    model = tentags.parse(IMG_FORMULA)
    html_output.write_text(tentags.render_html(model), encoding="utf-8")
    tentags.render_xlsx(model, xlsx_output)
    tentags.render_pdf(model, str(pdf_output))

    return model, html_output, xlsx_output, pdf_output


def test_local_and_external_img_render_to_html_xlsx_and_pdf():
    openpyxl = pytest.importorskip("openpyxl")
    pytest.importorskip("reportlab")
    assert Path("D:/TenTags/tentags_logo.png").is_file()

    model, html_output, xlsx_output, pdf_output = build_img_artifacts()

    assert model.cells[0][0].images == [{
        "src": "D:/TenTags/tentags_logo.png",
        "w": "120",
        "h": "auto",
        "m": "15",
    }]
    assert model.cells[0][1].images == [{
        "src": "https://pycells.com//assets/img/PyCells_mds.png",
        "w": "120",
        "h": "auto",
        "m": "15",
    }]

    html = html_output.read_text(encoding="utf-8")
    assert 'src="D:/TenTags/tentags_logo.png"' in html
    assert 'src="https://pycells.com//assets/img/PyCells_mds.png"' in html
    assert html.count('width="120"') == 2
    assert html.count("height:auto") == 2
    assert html.count("margin:15px") == 2

    sheet = openpyxl.load_workbook(xlsx_output)["Table"]
    assert len(sheet._images) == 2
    assert all(image.anchor.ext.cx / 9525 == 120 for image in sheet._images)
    assert all(image.anchor.ext.cy / 9525 > 0 for image in sheet._images)

    pdf_data = pdf_output.read_bytes()
    assert pdf_data.startswith(b"%PDF")
    assert pdf_data.count(b"/Subtype /Image") >= 2
    assert pdf_output.stat().st_size > 1000


@pytest.mark.parametrize("width", [60, 120, 180])
@pytest.mark.parametrize("margin", [0, 5, 15, 30])
def test_pdf_img_uses_variable_width_margin_and_auto_height(width, margin):
    pytest.importorskip("reportlab")
    model = tentags.parse(
        '1,1,1,"#64748b","solid-1",0,300,'
        f'data(<img src=D:/TenTags/tentags_logo.png w={width} h=auto m={margin}>)'
    )

    table = tentags._create_pdf_table_object(model)
    table.wrap(500, 700)

    assert table._rowHeights == [300]
    cell_content = table._cellvalues[0][0]
    rendered = cell_content[-1]
    image = rendered if margin == 0 else rendered._cellvalues[0][0]
    expected_height = image.imageHeight * width / image.imageWidth
    assert image.drawWidth == width
    assert image.drawHeight == expected_height
    if margin:
        assert rendered._argH == [expected_height + 2 * margin]
        assert rendered._cellStyles[0][0].leftPadding == margin
        assert rendered._cellStyles[0][0].rightPadding == margin
        assert rendered._cellStyles[0][0].topPadding == margin
        assert rendered._cellStyles[0][0].bottomPadding == margin


if __name__ == "__main__":
    _, html_path, xlsx_path, pdf_path = build_img_artifacts()
    print(f"HTML created: {html_path}")
    print(f"XLSX created: {xlsx_path}")
    print(f"PDF created: {pdf_path}")
