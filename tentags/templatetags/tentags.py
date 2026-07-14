try:
    from django import template
    from django.utils.safestring import mark_safe
except ImportError:
    class MockLibrary:
        def tag(self, *args, **kwargs):
            return lambda fn: fn
        def simple_tag(self, *args, **kwargs):
            return lambda fn: fn
    template = type('MockTemplate', (), {'Library': MockLibrary})()
    mark_safe = lambda s: s

import tentags

register = template.Library()


class TenTagsNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        # Render the nodes inside the block (resolving context variables)
        content = self.nodelist.render(context)
        # Compile via TenTags and mark HTML as safe
        return mark_safe(tentags.render(content.strip()))


@register.tag(name="tentags")
def do_tentags(parser, token):
    """
    Block tag for standard Django template engine.
    
    Usage:
        {% load tentags %}
        {% tentags %}
        3,3,1,"black","solid",0,
        data(
            A, B;
            C, {{ value }}
        )
        {% endtentags %}
    """
    nodelist = parser.parse(('endtentags',))
    parser.delete_first_token()
    return TenTagsNode(nodelist)


@register.tag(name="tt")
def do_tt(parser, token):
    """
    Short alias tag for standard Django template engine.
    
    Usage:
        {% load tentags %}
        {% tt %}
        3,3,1,"black","solid",0,
        data(
            A, B;
            C, {{ value }}
        )
        {% endtt %}
    """
    nodelist = parser.parse(('endtt',))
    parser.delete_first_token()
    return TenTagsNode(nodelist)


@register.simple_tag(name="tentags_inline")
def tentags_inline(formula):
    """
    Simple tag for inline rendering of a TenTags formula.
    
    Usage:
        {% load tentags %}
        {% tentags_inline formula_string %}
    """
    return mark_safe(tentags.render(formula))
