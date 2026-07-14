import pytest

try:
    import django
    from django.conf import settings
    
    # Configure minimal settings for Django rendering tests
    if not settings.configured:
        settings.configure(
            TEMPLATES=[
                {
                    'BACKEND': 'django.template.backends.django.DjangoTemplates',
                    'OPTIONS': {
                        'builtins': [
                            'tentags.templatetags.tentags',
                        ],
                    },
                },
            ]
        )
    django.setup()
    from django.template import Template, Context
    HAS_DJANGO = True
except ImportError:
    HAS_DJANGO = False

@pytest.mark.skipif(not HAS_DJANGO, reason="Django is not installed")
def test_django_block_tag():
    template_str = """
    {% tt %}
    1, 1, 1, "black", "solid", 0,
    data(Hello {{ name }})
    {% endtt %}
    """
    
    t = Template(template_str)
    c = Context({"name": "Django"})
    html = t.render(c)
    
    assert "Hello Django" in html
    assert "<table" in html
    assert "&lt;" not in html


@pytest.mark.skipif(not HAS_DJANGO, reason="Django is not installed")
def test_django_inline_tag():
    template_str = """
    {% tentags_inline "1, 1, 1, 'black', 'solid', 0, data(Hello Inline)" %}
    """
    
    t = Template(template_str)
    c = Context({})
    html = t.render(c)
    
    assert "Hello Inline" in html
    assert "<table" in html
    assert "&lt;" not in html
