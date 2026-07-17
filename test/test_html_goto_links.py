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


def test_html_one_column_25_rows_with_goto_links():
    model = tentags.parse(_one_column_goto_expr())
    html = tentags.render_html(model)

    assert model.rows == 25
    assert model.cols == 1
    assert html.count("<tr") == 25
    assert 'id="tt-A1"' in html
    assert 'id="tt-A25"' in html
    assert '<a href="#tt-A25"' in html
    assert '<a href="#tt-A3"' in html
    assert '<a href="#tt-A1"' in html
    assert ">Start to end</a>" in html
    assert ">End to start</a>" in html
