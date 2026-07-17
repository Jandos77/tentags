import pytest
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import tentags
from tentags.addressing import AddressType


def build_pdf_one_column_25_rows_with_goto_links():
    pytest.importorskip("reportlab")

    rows = []
    for index in range(1, 26):
        if index == 1:
            rows.append("<url=goto:A25>Start to end</url>")
        elif index == 25:
            rows.append("<url=goto:A1>End to start</url>")
        else:
            rows.append(f"<url=goto:A{index + 1}>Row {index} to next</url>")

    expr = f'25,1,3,"#000","solid-1",0,24, data({"; ".join(rows)})'
    model = tentags.parse(expr)

    assert model.rows == 25
    assert model.cols == 1
    assert model.cells[0][0].link.scheme == "goto"
    assert model.cells[0][0].link.target.location.type is AddressType.CELL
    assert model.cells[0][0].link.target.location.cell.row == 24
    assert model.cells[24][0].link.target.location.cell.row == 0

    html = tentags.render_html(model)
    assert '<a href="#tt-A25"' in html
    assert '<a href="#tt-A1"' in html

    output = PROJECT_ROOT / "one_column_goto_links.pdf"
    if output.exists():
        output.unlink()

    tentags.render_pdf(model, str(output))

    data = output.read_bytes()
    assert data.startswith(b"%PDF")
    assert len(data) > 1000
    return output


def test_pdf_one_column_25_rows_with_goto_links():
    build_pdf_one_column_25_rows_with_goto_links()


if __name__ == "__main__":
    pdf_path = build_pdf_one_column_25_rows_with_goto_links()
    print(f"PDF created: {pdf_path}")
