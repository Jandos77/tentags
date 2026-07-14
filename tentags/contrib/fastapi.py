"""
FastAPI integration for TenTags.
Provides helper to register TenTags in FastAPI's Jinja2Templates.
"""

def register_templates(templates):
    """
    Registers the TenTags extension and global function into FastAPI Jinja2Templates.
    
    Example:
        from fastapi.templating import Jinja2Templates
        from tentags.contrib.fastapi import register_templates
        
        templates = Jinja2Templates(directory="templates")
        register_templates(templates)
    """
    from tentags.contrib.jinja import register_jinja_rules
    register_jinja_rules(templates.env)
