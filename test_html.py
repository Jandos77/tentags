import pytest
import tentags

def test_basic_html_rendering():
    # Test simple grid without merges or tags
    expr = '2,2,1,"#000","solid",0,30, data(A, B; C, D)'
    html = tentags.render(expr)
    
    assert "<table" in html
    assert "border:1px solid #000" in html
    assert "height:30px" in html
    assert ">A</td>" in html
    assert ">B</td>" in html
    assert ">C</td>" in html
    assert ">D</td>" in html

def test_html_column_merges():
    # Test column merge <cm> tag
    expr = '1,3,1,"#000","solid",0,30, data(<cm>Merge, </cm>, Right)'
    html = tentags.render(expr)
    
    # <cm> translates to border-right:none for the left cell
    # and border-left:none for the right cell
    assert "border-right:none;" in html
    assert "border-left:none;" in html
    assert ">Merge</td>" in html

def test_html_row_merges():
    # Test row merge <rm> tag
    expr = '3,1,1,"#000","solid",0,30, data(<rm>Top</rm>; <rm> </rm>; Bottom)'
    html = tentags.render(expr)
    
    # <rm> translates to border-bottom:none/border-top:none overrides
    assert "border-bottom:none;" in html
    assert "border-top:none;" in html
    assert ">Top</td>" in html
    assert ">Bottom</td>" in html

def test_html_variable_interpolation():
    # Test context variable substitution
    expr = '1,2,1,"#ccc","solid",0,40, data(User, StateVar)'
    context = {'StateVar': 'Active'}
    html = tentags.render(expr, context)
    
    assert ">User</td>" in html
    assert ">Active</td>" in html

def test_html_styling_tags():
    # Test bold, italic, color, bg tags
    expr = '1,3,1,"#000","solid",0,40, data(<b>Bold</b>, <color=red><i>Red Italic</i></color>, <bg=#eeeeee>Gray</bg>)'
    html = tentags.render(expr)
    
    assert "font-weight:bold;" in html
    assert ">Bold</td>" in html
    
    assert "color:red;" in html
    assert "font-style:italic;" in html
    assert ">Red Italic</td>" in html
    
    assert "background-color:#eeeeee;" in html
    assert ">Gray</td>" in html

def test_html_alignment_and_font_size():
    # Test <fs=XX>, <left>, <center>, <right> tags
    expr = '1,3,1,"#000","solid",0,40, data(<fs=16><left>Left 16</left></fs>, <center>Center</center>, <right>Right</right>)'
    html = tentags.render(expr)
    
    assert "font-size:16px;" in html
    assert "text-align:left;" in html
    assert "text-align:center;" in html
    assert "text-align:right;" in html

def test_html_unclosed_tag_error():
    # Test error when tag is not closed properly
    expr = '1,1,1,"#000","solid",0,30, data(<b>Unclosed)'
    with pytest.raises(ValueError, match="Missing closing tag </b>"):
        tentags.parse(expr)

def test_decoupled_api():
    # Test parse then render_html
    expr = '2,2,1,"blue","solid",1, data(Hello, World; One, Two)'
    table_model = tentags.parse(expr)
    
    assert table_model.rows == 2
    assert table_model.cols == 2
    assert table_model.border_color == "blue"
    
    html = tentags.render_html(table_model)
    assert '<table style="border-collapse:collapse;border:1px solid blue;' in html
    assert "width:100%;height:100%;table-layout:fixed;" in html

def test_decoupled_style_and_data():
    expr = '''2,2,1,"#000","solid",0,40,
    style(
        <fs=18><bg=#1e293b><color=white><b><cm><center></center></cm></b></color></bg></fs>, ;
        <bg=#f1f5f9><b><left></left></b></bg>, <bg=#f1f5f9><b><right></right></b></bg>
    ),
    data(
        Title, ;
        Name, Salary
    )'''
    model = tentags.parse(expr)
    assert model.rows == 2
    assert model.cols == 2
    
    # Assert merged cell properties
    cell_0_0 = model.cells[0][0]
    cell_0_1 = model.cells[0][1]
    cell_1_0 = model.cells[1][0]
    cell_1_1 = model.cells[1][1]
    
    assert cell_0_0.raw_expr == "Title"
    assert cell_0_0.styles.get('font-size') == "18px"
    assert cell_0_0.styles.get('background-color') == "#1e293b"
    assert cell_0_0.styles.get('font-weight') == "bold"
    assert cell_0_0.styles.get('text-align') == "center"
    
    assert cell_1_0.raw_expr == "Name"
    assert cell_1_0.styles.get('background-color') == "#f1f5f9"
    assert cell_1_0.styles.get('text-align') == "left"
    
    assert cell_1_1.raw_expr == "Salary"
    assert cell_1_1.styles.get('background-color') == "#f1f5f9"
    assert cell_1_1.styles.get('text-align') == "right"

    # Also test PDF and Excel generation do not fail
    tentags.render_xlsx(model, "test_decoupled_output.xlsx")
    try:
        tentags.render_pdf(model, "test_decoupled_output.pdf")
    except ImportError:
        pass

def test_load_style_and_data_api():
    style_content = '''
    <fs=16><b><center></center></b></fs>, <bg=#eee></bg>;
    <left></left>, <right></right>
    '''
    data_content = '''
    Title, Metric;
    Sales, 1000
    '''
    
    style = tentags.load_style(style_content)
    data = tentags.load_data(data_content)
    
    model = tentags.compile(style, data, preamble='1,"#ccc","solid",0,40')
    
    assert model.rows == 2
    assert model.cols == 2
    assert model.cell_height == 40
    assert model.border_color == "#ccc"
    
    assert model.cells[0][0].raw_expr == "Title"
    assert model.cells[0][0].styles.get('font-size') == "16px"
    assert model.cells[0][0].styles.get('font-weight') == "bold"
    assert model.cells[0][0].styles.get('text-align') == "center"
    
    assert model.cells[0][1].raw_expr == "Metric"
    assert model.cells[0][1].styles.get('background-color') == "#eee"
    
    # Test rendering directly
    html = tentags.render(style, data, preamble='1,"#ccc","solid",0,40')
    assert "Title" in html
    assert "background-color:#eee;" in html


