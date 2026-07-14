"""
Flask integration for TenTags.
Provides automatic registration of the TenTagsExtension and global function.
"""

def init_app(app):
    """
    Registers TenTags Extension into Flask app's Jinja environment.
    """
    from tentags.contrib.jinja import TenTagsExtension, jinja_render
    
    # Add extension
    app.jinja_env.add_extension(TenTagsExtension)
    # Add global function helper
    app.jinja_env.globals['tentags'] = jinja_render
