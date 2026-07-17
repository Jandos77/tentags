import pytest

import tentags


def test_value_tag_inserts_local_cell_value():
    model = tentags.parse('1,2,1,"#000","solid",0,40, data(Source, <value=A1>)')

    assert model.cells[0][1].raw_expr == "Source"
    assert "Source" in tentags.render_html(model)


def test_value_tag_can_be_inline_text():
    model = tentags.parse('1,2,1,"#000","solid",0,40, data(42, Total: <value=A1>)')

    assert model.cells[0][1].raw_expr == "Total:42"


def test_value_tag_inserts_range_row_major():
    model = tentags.parse('2,3,1,"#000","solid",0,40, data(A, B, <value=A1:B1>; C, D, E)')

    assert model.cells[0][2].raw_expr == "A, B"


def test_value_tag_can_resolve_mark_location():
    model = tentags.parse(
        '1,2,1,"#000","solid",0,40, data(<mark=Total>42, <value=Total>)'
    )

    assert model.cells[0][1].raw_expr == "42"


def test_value_tag_works_with_decoupled_compile_api():
    model = tentags.compile(
        '1,2,1,"#000","solid",0,40',
        'style(<b></b>, )',
        'data(Hello, <value=A1>)',
    )

    assert model.cells[0][1].raw_expr == "Hello"
    assert model.cells[0][0].styles["font-weight"] == "bold"


def test_value_tag_requires_address():
    with pytest.raises(ValueError, match="<value> requires an address"):
        tentags.parse('1,1,1,"#000","solid",0,40, data(<value>)')


def test_value_tag_external_addresses_are_reserved_for_future_resolution():
    with pytest.raises(ValueError, match="External <value=...> addresses are not supported yet"):
        tentags.parse('1,1,1,"#000","solid",0,40, data(<value=Table_1!List_1!A1>)')
