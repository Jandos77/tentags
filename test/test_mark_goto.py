import pytest

import tentags
from tentags.addressing import AddressType, DuplicateMarkError


def test_mark_single_tag_attaches_to_cell_metadata():
    model = tentags.parse('1,1,1,"#000","solid",0,40, data(<mark=Summary><b>Summary</b>)')
    cell = model.cells[0][0]

    assert cell.mark == "Summary"
    assert cell.raw_expr == "Summary"
    assert cell.styles["font-weight"] == "bold"


def test_url_goto_mark_uses_link_address_not_href_style():
    model = tentags.parse(
        '1,2,1,"#000","solid",0,40, '
        'data(<mark=Summary>Summary, <url=goto:Summary>Go</url>)'
    )
    link_cell = model.cells[0][1]

    assert link_cell.link.scheme == "goto"
    assert link_cell.link.target.location.type is AddressType.MARK
    assert link_cell.link.target.location.mark == "Summary"
    assert "href" not in link_cell.styles

    html = tentags.render_html(model)
    assert 'id="tt-A1"' in html
    assert 'id="tt-B1"' in html
    assert 'id="tt-mark-Summary"' in html
    assert '<a href="#tt-mark-Summary"' in html
    assert ">Go</a>" in html


def test_url_goto_a1_uses_coordinate_anchor():
    html = tentags.render('1,2,1,"#000","solid",0,40, data(Target, <url=goto:A1>Top</url>)')

    assert 'id="tt-A1"' in html
    assert '<a href="#tt-A1"' in html


def test_old_url_href_style_compatibility_stays_available():
    model = tentags.parse('1,1,1,"#000","solid",0,40, data(<url=https://example.com>Visit</url>)')
    cell = model.cells[0][0]

    assert cell.link.scheme == "https"
    assert cell.link.target == "https://example.com"
    assert cell.styles["href"] == "https://example.com"

    html = tentags.render_html(model)
    assert '<a href="https://example.com"' in html
    assert ">Visit</a>" in html


def test_duplicate_marks_are_strict_errors_in_renderers():
    model = tentags.parse(
        '1,2,1,"#000","solid",0,40, data(<mark=Summary>One, <mark=Summary>Two)'
    )

    with pytest.raises(DuplicateMarkError):
        tentags.build_mark_index(model)
    with pytest.raises(DuplicateMarkError):
        tentags.render_html(model)


def test_25x1_table_can_link_each_row_to_the_next_until_end():
    rows = []
    for row in range(1, 25):
        rows.append(f"<url=goto:A{row + 1}>Row {row} to Row {row + 1}</url>")
    rows.append("Row 25 End")

    expr = f'25,1,1,"#000","solid",0,30, data(' + "; ".join(rows) + ")"
    model = tentags.parse(expr)
    html = tentags.render_html(model)

    assert model.rows == 25
    assert model.cols == 1
    assert len(model.cells) == 25

    for row in range(1, 26):
        assert f'id="tt-A{row}"' in html

    for row in range(1, 25):
        assert f'<a href="#tt-A{row + 1}"' in html
        assert f">Row {row} to Row {row + 1}</a>" in html

    assert "Row 25 End</td>" in html
