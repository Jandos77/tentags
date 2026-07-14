import pytest

try:
    from jinja2 import Environment, DictLoader
    HAS_JINJA = True
except ImportError:
    HAS_JINJA = False

@pytest.mark.skipif(not HAS_JINJA, reason="Jinja2 is not installed")
def test_jinja_global_function():
    from tentags.contrib.jinja import TenTagsExtension
    
    env = Environment(
        loader=DictLoader({
            'index.html': '{{ tentags(formula) }}'
        })
    )
    # Register global function
    from tentags.contrib.jinja import jinja_render
    env.globals['tentags'] = jinja_render

    formula = '1,1,1,"black","solid",0, data(Cell Content)'
    template = env.get_template('index.html')
    html = template.render(formula=formula)
    
    assert "Cell Content" in html
    assert "<table" in html
    # Check that it wasn't escaped
    assert "&lt;" not in html


@pytest.mark.skipif(not HAS_JINJA, reason="Jinja2 is not installed")
def test_jinja_block_tag():
    from tentags.contrib.jinja import TenTagsExtension
    
    env = Environment(
        loader=DictLoader({
            'index.html': '{% tt %}1,1,1,"black","solid",0, data(Cell Content){% endtt %}'
        }),
        extensions=[TenTagsExtension]
    )

    template = env.get_template('index.html')
    html = template.render()
    
    assert "Cell Content" in html
    assert "<table" in html
    assert "&lt;" not in html


@pytest.mark.skipif(not HAS_JINJA, reason="Jinja2 is not installed")
def test_jinja_block_tag_parameters():
    from tentags.contrib.jinja import TenTagsExtension
    
    env = Environment(
        loader=DictLoader({
            'index.html': (
                '{% tt rows=2 cols=2 border_width=3 border_color="blue" %}'
                'A, B;'
                'C, D'
                '{% endtt %}'
            )
        }),
        extensions=[TenTagsExtension]
    )

    template = env.get_template('index.html')
    html = template.render()
    
    assert "A</td>" in html
    assert "border:3px" in html
    assert "blue" in html
    assert "<table" in html
    assert "&lt;" not in html
