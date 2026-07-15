import pytest

try:
    import django
    from django.conf import settings
    
    # Configure minimal settings for Django rendering tests
    if not settings.configured:
        settings.configure(
            INSTALLED_APPS=[
                'tentags',  # enables {% load tentags %} via templatetags auto-discovery
            ],
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
    {% load tentags %}
    {% tt %}
    2, 1, 1, "black", "solid-1", 0, 50,
    data(<bg=yellow><color=blue>Hello {{ name }}</color></bg>; Yow are You ?)
    {% endtt %}
    """
    
    t = Template(template_str)
    c = Context({"name": "Django"})
    html = t.render(c)
    
    print("\n--- Django Block Tag HTML Output ---")
    print(html)
    
    assert "Hello Django" in html
    assert "<table" in html
    assert "&lt;" not in html


@pytest.mark.skipif(not HAS_DJANGO, reason="Django is not installed")
def test_django_inline_tag():
    template_str = """
    {% load tentags %}
    {% tentags_inline "1, 1, 1, 'black', 'solid', 0, 50, data(Hello Inline)" %}
    """
    
    t = Template(template_str)
    c = Context({})
    html = t.render(c)
    
    print("\n--- Django Inline Tag HTML Output ---")
    print(html)
    
    assert "Hello Inline" in html
    assert "<table" in html
    assert "&lt;" not in html


@pytest.mark.skipif(not HAS_DJANGO, reason="Django is not installed")
def test_django_decoupled_inline_tag():
    template_str = """
    {% load tentags %}
    {% tentags_inline preamble style data %}
    """
    
    t = Template(template_str)
    c = Context({
        "preamble": "1, 1, 1, 'black', 'solid', 0, 50",
        "style": "style(<center><b></b></center>)",
        "data": "data(Hello Decoupled)"
    })
    html = t.render(c)
    
    print("\n--- Django Decoupled Inline Tag HTML Output ---")
    print(html)
    
    assert "Hello Decoupled" in html
    assert "font-weight:bold" in html
    assert "<table" in html
    assert "&lt;" not in html


if __name__ == "__main__":
    if HAS_DJANGO:
        print("=== Running Django Template Tag Tests ===")
        test_django_block_tag()
        test_django_inline_tag()
        test_django_decoupled_inline_tag()
        print("\nAll Django tests passed successfully!")
    else:
        print("Django is not installed in the environment.")
