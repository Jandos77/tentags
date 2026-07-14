import tentags

try:
    from jinja2 import Markup
except ImportError:
    try:
        from markupsafe import Markup
    except ImportError:
        Markup = lambda s: s

try:
    from jinja2.ext import Extension
    from jinja2 import nodes
    JINJA_AVAILABLE = True
except ImportError:
    Extension = object
    nodes = None
    JINJA_AVAILABLE = False


def jinja_render(style_or_formula, data=None, preamble=None, context=None):
    """
    Jinja-safe wrapper for tentags.render.
    Returns a Markup string so that Jinja2 does not escape the HTML output.
    """
    res = tentags.render(style_or_formula, data=data, preamble=preamble, context=context)
    return Markup(res)


if JINJA_AVAILABLE:
    class TenTagsExtension(Extension):
        """
        Jinja2 extension providing the {% tentags %} and {% tt %} block tags.
        
        Example:
            {% tt %}
            3, 3, 1, "black", "solid", 0,
            data(
                A, B;
                C, D;
            )
            {% endtt %}
        """
        tags = {'tentags', 'tt'}

        def parse(self, parser):
            # Stream points to the current tag ({% tentags %} or {% tt %})
            tag = next(parser.stream).value
            lineno = parser.stream.current.lineno

            # Parse block parameters if any (e.g., {% tt border=1 color="red" %})
            # For simplicity in 2.0.0, we parse any remaining arguments as kwargs
            kwargs = []
            while parser.stream.current.type != 'block_end':
                if parser.stream.current.type == 'name' and parser.stream.look().type == 'assign':
                    name = next(parser.stream).value
                    next(parser.stream)  # skip '='
                    value = parser.parse_expression()
                    kwargs.append(nodes.Keyword(name, value))
                else:
                    # Skip other tokens or parse expression
                    next(parser.stream)

            # Parse the body of the block up to the corresponding end tag
            end_tag = f'end{tag}'
            body = parser.parse_statements([f'name:{end_tag}'], drop_needle=True)

            # Call the helper method to render the contents
            return nodes.CallBlock(
                self.call_method('_render_block', kwargs=[nodes.Keyword('args_dict', nodes.Dict([
                    nodes.Pair(nodes.Const(kw.key), kw.value) for kw in kwargs
                ]))]),
                [], [], body
            ).set_lineno(lineno)

        def _render_block(self, args_dict=None, caller=None):
            if caller is None:
                return ""
            
            # Evaluate internal block contents (e.g. loops, print statements)
            formula_content = caller().strip()
            
            # If arguments are passed to the tag, we construct or override the preamble
            if args_dict:
                # Basic preamble building from parameters
                rows = args_dict.get('rows', 1)
                cols = args_dict.get('cols', 1)
                border_width = args_dict.get('border_width', 1)
                border_color = args_dict.get('border_color', '#cbd5e1')
                border_style = args_dict.get('border_style', 'solid')
                stretch = args_dict.get('stretch', 0)
                cell_height = args_dict.get('cell_height', 30)

                preamble = f'{rows}, {cols}, {border_width}, "{border_color}", "{border_style}", {stretch}, {cell_height}'
                
                # Check if it has a style/data block inside
                if 'data(' not in formula_content and 'style(' not in formula_content:
                    formula_content = f"data({formula_content})"
                
                full_formula = f"{preamble}, {formula_content}"
                res = tentags.render(full_formula)
                return Markup(res)
            
            return Markup(tentags.render(formula_content))
else:
    class TenTagsExtension(object):
        def __init__(self, *args, **kwargs):
            raise ImportError("Jinja2 must be installed to use TenTagsExtension.")


def register_jinja_rules(env):
    """
    Helper function to register the global `tentags` function and
    the `TenTagsExtension` into a Jinja2 Environment.
    """
    # Register global function
    env.globals['tentags'] = jinja_render
    # Register extension if available
    if JINJA_AVAILABLE:
        env.add_extension(TenTagsExtension)
