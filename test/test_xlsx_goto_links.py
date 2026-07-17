import pytest

import tentags


def _one_column_goto_expr():
    rows = []
    for index in range(1, 26):
        if index == 1:
            rows.append("<url=goto:A25>Start to end</url>")
        elif index == 25:
            rows.append("<url=goto:A1>End to start</url>")
        else:
            rows.append(f"<url=goto:A{index + 1}>Row {index} to next</url>")
    return f'25,1,1,"#000","solid",0,24, data({"; ".join(rows)})'


def test_xlsx_one_column_25_rows_with_goto_links(tmp_path):
    openpyxl = pytest.importorskip("openpyxl")

    model = tentags.parse(_one_column_goto_expr())
    output = tmp_path / "one_column_goto_links.xlsx"
    tentags.render_xlsx(model, str(output))

    wb = openpyxl.load_workbook(output)
    ws = wb["Table"]

    assert ws.max_row == 25
    assert ws.max_column == 1
    assert ws["A1"].value == "Start to end"
    assert ws["A25"].value == "End to start"
    assert ws["A1"].hyperlink.target == "#Table!A25"
    assert ws["A2"].hyperlink.target == "#Table!A3"
    assert ws["A25"].hyperlink.target == "#Table!A1"
