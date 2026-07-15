"""
TenTags
=======

Declarative Document DSL.

Write a document once.
Render it everywhere.

HTML • PDF • XLSX

Quick Start
-----------

    import tentags
    html = tentags.render('3,3,1,"black","solid",0, data(A,B,C; D,E,F; G,H,I)')

Typical Workflow
----------------

1. Define style.
2. Define data.
3. Compile into TableModel.
4. Render to HTML, PDF or XLSX.

or simply:

    html = tentags.render(formula)

API Index
---------

Main API:
  render()           Render HTML
  compile()          Build TableModel
  parse()            Parse formula
  validate()         Validate syntax

Export:
  render_html()      Render to HTML string
  render_pdf()       Export to PDF document
  render_xlsx()      Export to XLSX sheet

Multiple Tables:
  multitable_html()  Combine tables into HTML Grid
  multitable_pdf()   Combine tables into multi-page PDF
  multitable_xlsx()  Combine tables into Excel workbook

Utilities:
  demo()             Generate sample documents
  info()             Display system diagnostic info
  features()         Check available render backends

Website: https://tentags.org
Documentation: https://tentags.org/docs
GitHub: https://github.com/Jandos77/tentags

Current Version: 2.0.1
License: Apache License 2.0
"""

__version__ = "2.0.1"
__author__ = "Zhandos Mambetali"
__license__ = "Apache-2.0"
__copyright__ = "Copyright (c) 2026 Zhandos Mambetali"
__homepage__ = "https://tentags.org"
__url__ = "https://tentags.org"
version_info = (2, 0, 1)

__all__ = [
    "__version__",
    "__author__",
    "__license__",
    "__copyright__",
    "__homepage__",
    "__url__",
    "version_info",
    "parse",
    "render",
    "render_html",
    "render_xlsx",
    "render_pdf",
    "compile",
    "multitable_html",
    "multitable_xlsx",
    "multitable_pdf",
    "features",
    "info",
    "validate",
    "demo",
    "TableModel",
    "CellDesc",
    "BorderFlags"
]

import re as _re
import csv as _csv
import urllib.request as _urllib_request
import io as _io
import os as _os
from typing import Union as _Union, Any as _Any, Optional as _Optional, Dict as _Dict, List as _List
from enum import Enum as _Enum, auto as _auto
from dataclasses import dataclass as _dataclass

class _TokenType(_Enum):
    TAG_OPEN = _auto()
    TAG_CLOSE = _auto()
    COMMA = _auto()
    SEMICOLON = _auto()
    TEXT = _auto()

@_dataclass
class _Token:
    type: _TokenType
    value: str  # tag name or text value
    line: int
    column: int
    attr: str = None  # optional attribute value (e.g. tag parameter in <tag=value>)

class BorderFlags:
    NONE = 0
    HIDE_LEFT = 1
    HIDE_RIGHT = 2
    HIDE_TOP = 4
    HIDE_BOTTOM = 8

class CellDesc:
    def __init__(self):
        self.raw_expr = ""
        self.cm_block_id = None
        self.rm_block_id = None
        self.border_flags = BorderFlags.NONE
        self.text_parts = []
        self.styles = {}  # Extensible styles, e.g. {'font-weight': 'bold', 'color': '#ff0000'}

class TableModel:
    def __init__(self, rows: int, cols: int, cells: list[list[CellDesc]], border_width: int, border_color: str, border_style: str, stretch: int, cell_height: int):
        self.rows = rows
        self.cols = cols
        self.cells = cells
        self.border_width = border_width
        self.border_color = border_color
        self.border_style = border_style
        self.stretch = stretch
        self.cell_height = cell_height

def _scan_data_content(content: str):
    """
    Scans the data(...) inner string and extracts tokens.
    Returns a list of Token objects with tracking of source line and column.
    """
    tokens = []
    i = 0
    n = len(content)
    line = 1
    column = 1
    
    def advance(steps=1):
        nonlocal i, line, column
        for _ in range(steps):
            if i >= n:
                break
            if content[i] == '\n':
                line += 1
                column = 1
            else:
                column += 1
            i += 1

    while i < n:
        # Check for csv(...) calls
        csv_fn_match = _re.match(r'(?i)^csv\(', content[i:])
        if csv_fn_match:
            tok_line, tok_col = line, column
            start_i = i
            advance(len(csv_fn_match.group(0)))
            depth = 1
            in_q = False
            q_char = None
            while i < n and depth > 0:
                c = content[i]
                if not in_q:
                    if c in ('"', "'"):
                        in_q = True
                        q_char = c
                    elif c == '(':
                        depth += 1
                    elif c == ')':
                        depth -= 1
                else:
                    if c == q_char:
                        in_q = False
                advance(1)
            tokens.append(_Token(_TokenType.TEXT, content[start_i:i], tok_line, tok_col))
            continue

        # Check for generic tags: <tag_name>, <tag_name=attr_value>, or </tag_name>
        if content[i] == '<':
            # Closing tag
            tag_close_match = _re.match(r'^</([a-zA-Z_]+)>', content[i:])
            if tag_close_match:
                tok_line, tok_col = line, column
                tag_name = tag_close_match.group(1)
                advance(len(tag_close_match.group(0)))
                tokens.append(_Token(_TokenType.TAG_CLOSE, tag_name, tok_line, tok_col))
                continue
                
            # Opening tag
            tag_open_match = _re.match(r'^<([a-zA-Z_]+)(?:=([^>]+))?>', content[i:])
            if tag_open_match:
                tok_line, tok_col = line, column
                tag_name = tag_open_match.group(1)
                tag_attr = tag_open_match.group(2)
                advance(len(tag_open_match.group(0)))
                tokens.append(_Token(_TokenType.TAG_OPEN, tag_name, tok_line, tok_col, tag_attr))
                continue

        # Check for string literals (double quotes)
        if content[i] == '"':
            tok_line, tok_col = line, column
            val_chars = []
            advance(1)  # skip open quote
            while i < n and content[i] != '"':
                val_chars.append(content[i])
                advance(1)
            if i < n:
                advance(1)  # skip close quote
            tokens.append(_Token(_TokenType.TEXT, "".join(val_chars), tok_line, tok_col))
            continue

        # Check for string literals (single quotes)
        if content[i] == "'":
            tok_line, tok_col = line, column
            val_chars = []
            advance(1)
            while i < n and content[i] != "'":
                val_chars.append(content[i])
                advance(1)
            if i < n:
                advance(1)
            tokens.append(_Token(_TokenType.TEXT, "".join(val_chars), tok_line, tok_col))
            continue

        # Semicolon
        if content[i] == ';':
            tokens.append(_Token(_TokenType.SEMICOLON, ';', line, column))
            advance(1)
            continue

        # Comma
        if content[i] == ',':
            tokens.append(_Token(_TokenType.COMMA, ',', line, column))
            advance(1)
            continue

        # Text/variable identifiers
        tok_line, tok_col = line, column
        val_chars = []
        while i < n and content[i] not in (',', ';', '<', '"', "'"):
            val_chars.append(content[i])
            advance(1)
        tokens.append(_Token(_TokenType.TEXT, "".join(val_chars), tok_line, tok_col))

    # Clean and filter empty text tokens
    cleaned_tokens = []
    for tok in tokens:
        if tok.type == _TokenType.TEXT:
            cleaned_val = tok.value.strip()
            if not cleaned_val and tok.value == "":
                cleaned_tokens.append(_Token(_TokenType.TEXT, "", tok.line, tok.column))
            elif cleaned_val:
                cleaned_tokens.append(_Token(_TokenType.TEXT, cleaned_val, tok.line, tok.column))
        else:
            cleaned_tokens.append(tok)
            
    return cleaned_tokens

def _scan_csv_cell_content(cell_val: str):
    """
    Scans a single CSV cell value, extracting tags (<tag>, <tag=val>, </tag>)
    and treating the rest of the text as a single text token.
    """
    tokens = []
    i = 0
    n = len(cell_val)
    line = 1
    column = 1
    current_text = []
    tok_line, tok_col = 1, 1

    def advance(steps=1):
        nonlocal i, line, column
        for _ in range(steps):
            if i >= n:
                break
            if cell_val[i] == '\n':
                line += 1
                column = 1
            else:
                column += 1
            i += 1

    def flush_text():
        if current_text:
            tokens.append(_Token(_TokenType.TEXT, "".join(current_text), tok_line, tok_col))
            current_text.clear()

    while i < n:
        if cell_val[i] == '<':
            # Closing tag
            tag_close_match = _re.match(r'^</([a-zA-Z_]+)>', cell_val[i:])
            if tag_close_match:
                flush_text()
                tag_line, tag_col = line, column
                tag_name = tag_close_match.group(1)
                advance(len(tag_close_match.group(0)))
                tokens.append(_Token(_TokenType.TAG_CLOSE, tag_name, tag_line, tag_col))
                tok_line, tok_col = line, column
                continue
                
            # Opening tag
            tag_open_match = _re.match(r'^<([a-zA-Z_]+)(?:=([^>]+))?>', cell_val[i:])
            if tag_open_match:
                flush_text()
                tag_line, tag_col = line, column
                tag_name = tag_open_match.group(1)
                tag_attr = tag_open_match.group(2)
                advance(len(tag_open_match.group(0)))
                tokens.append(_Token(_TokenType.TAG_OPEN, tag_name, tag_line, tag_col, tag_attr))
                tok_line, tok_col = line, column
                continue
        
        if not current_text:
            tok_line, tok_col = line, column
        current_text.append(cell_val[i])
        advance(1)
        
    flush_text()
    return tokens

def _load_csv(source_path: str):
    """
    Loads CSV data from a URL or local file path.
    Returns a list of lists of strings.
    """
    source_path = source_path.strip().strip('"\'')
    if source_path.startswith(('http://', 'https://')):
        try:
            req = _urllib_request.Request(
                source_path, 
                headers={'User-Agent': 'Mozilla/5.0 (tentags)'}
            )
            with _urllib_request.urlopen(req) as response:
                content = response.read().decode('utf-8')
            f = _io.StringIO(content)
            reader = _csv.reader(f)
            return list(reader)
        except Exception as e:
            return [[f"Error loading CSV URL: {e}"]]
    else:
        try:
            with open(source_path, mode='r', encoding='utf-8') as f:
                reader = _csv.reader(f)
                return list(reader)
        except Exception as e:
            return [[f"Error loading CSV file: {e}"]]

def _parse_data_arg(content: str, context: dict = None):
    """
    Parses data block content into a 2D grid of CellDesc.
    Supports variable interpolation using context dictionary.
    Expands csv("path_or_url") links dynamically into the token stream.
    Supports generic tags and style mapping.
    """
    if context is None:
        context = {}
        
    tokens = _scan_data_content(content)
    
    # Expand CSV tokens dynamically
    expanded_tokens = []
    for tok in tokens:
        if tok.type == _TokenType.TEXT:
            csv_match = _re.match(r'(?is)^csv\((.*)\)$', tok.value)
            if csv_match:
                csv_path = csv_match.group(1).strip().strip('"\'')
                csv_data = _load_csv(csv_path)
                
                csv_tokens = []
                for r_idx, row in enumerate(csv_data):
                    if r_idx > 0:
                        csv_tokens.append(_Token(_TokenType.SEMICOLON, ';', tok.line, tok.column))
                    for c_idx, cell_val in enumerate(row):
                        if c_idx > 0:
                            csv_tokens.append(_Token(_TokenType.COMMA, ',', tok.line, tok.column))
                        csv_tokens.extend(_scan_csv_cell_content(cell_val))
                expanded_tokens.extend(csv_tokens)
                continue
        expanded_tokens.append(tok)

    cells_grid = [[]]
    current_cell = CellDesc()

    active_tags = []
    cm_counter = 0
    rm_counter = 0

    def apply_active_tags(cell):
        for active_tok in active_tags:
            tag_lower = active_tok.value.lower()
            if tag_lower == 'cm':
                cell.cm_block_id = getattr(active_tok, 'block_id', None)
            elif tag_lower == 'rm':
                cell.rm_block_id = getattr(active_tok, 'block_id', None)
            elif tag_lower == 'b':
                cell.styles['font-weight'] = 'bold'
            elif tag_lower == 'i':
                cell.styles['font-style'] = 'italic'
            elif tag_lower == 'u':
                decorations = cell.styles.get('text-decoration', '').split()
                if 'underline' not in decorations:
                    decorations.append('underline')
                cell.styles['text-decoration'] = ' '.join(decorations).strip()
            elif tag_lower == 's':
                decorations = cell.styles.get('text-decoration', '').split()
                if 'line-through' not in decorations:
                    decorations.append('line-through')
                cell.styles['text-decoration'] = ' '.join(decorations).strip()
            elif tag_lower == 'color':
                if active_tok.attr:
                    cell.styles['color'] = active_tok.attr
            elif tag_lower == 'bg':
                if active_tok.attr:
                    cell.styles['background-color'] = active_tok.attr
            elif tag_lower == 'url':
                if active_tok.attr:
                    cell.styles['href'] = active_tok.attr
            elif tag_lower == 'fs':
                if active_tok.attr:
                    cell.styles['font-size'] = active_tok.attr if any(c.isalpha() or c == '%' for c in active_tok.attr) else f"{active_tok.attr}px"
            elif tag_lower == 'left':
                cell.styles['text-align'] = 'left'
            elif tag_lower == 'center':
                cell.styles['text-align'] = 'center'
            elif tag_lower == 'right':
                cell.styles['text-align'] = 'right'

    # Apply initial active tags if any exist (though usually stack is empty at start)
    apply_active_tags(current_cell)

    def commit_cell():
        nonlocal current_cell
        raw_text = "".join(current_cell.text_parts).strip()
        
        # Apply variable interpolation context
        if raw_text in context:
            raw_text = str(context[raw_text])
            
        current_cell.raw_expr = raw_text
        
        cells_grid[-1].append(current_cell)
        current_cell = CellDesc()
        # Carry over active tags spanning cell boundaries
        apply_active_tags(current_cell)

    for tok in expanded_tokens:
        if tok.type == _TokenType.TAG_OPEN:
            tag_name = tok.value.lower()
            if tag_name == 'cm' and any(t.value.lower() == 'cm' for t in active_tags):
                raise ValueError(f"Nested <cm> blocks are not supported at line {tok.line}, column {tok.column}.")
            if tag_name == 'rm' and any(t.value.lower() == 'rm' for t in active_tags):
                raise ValueError(f"Nested <rm> blocks are not supported at line {tok.line}, column {tok.column}.")
            
            # Assign unique block IDs for merge tags
            if tag_name == 'cm':
                cm_counter += 1
                tok.block_id = cm_counter
            elif tag_name == 'rm':
                rm_counter += 1
                tok.block_id = rm_counter
                
            active_tags.append(tok)
            apply_active_tags(current_cell)
            
        elif tok.type == _TokenType.TAG_CLOSE:
            tag_name = tok.value.lower()
            # Find matching tag in stack
            match_idx = -1
            for idx in reversed(range(len(active_tags))):
                if active_tags[idx].value.lower() == tag_name:
                    match_idx = idx
                    break
            if match_idx == -1:
                raise ValueError(f"Unexpected closing tag </{tag_name}> at line {tok.line}, column {tok.column}.")
            active_tags.pop(match_idx)
            # Re-apply remaining active styles
            apply_active_tags(current_cell)
            
        elif tok.type == _TokenType.COMMA:
            commit_cell()
        elif tok.type == _TokenType.SEMICOLON:
            commit_cell()
            cells_grid.append([])
        elif tok.type == _TokenType.TEXT:
            apply_active_tags(current_cell)
            current_cell.text_parts.append(tok.value)

    # Commit final cell
    commit_cell()

    # Check for unclosed tags
    if active_tags:
        unclosed = active_tags[-1]
        raise ValueError(f"Missing closing tag </{unclosed.value}> (opened at line {unclosed.line}, column {unclosed.column}).")

    # Remove trailing empty row if created by a trailing semicolon
    if len(cells_grid) > 1:
        last_row = cells_grid[-1]
        if len(last_row) == 1 and last_row[0].raw_expr == "":
            cells_grid.pop()

    # Apply Column Merge borders
    for row in cells_grid:
        i = 0
        n = len(row)
        while i < n:
            if row[i].cm_block_id is None:
                i += 1
                continue

            start_idx = i
            while i < n and row[i].cm_block_id is not None:
                i += 1
            end_idx = i - 1

            if start_idx < end_idx:
                row[start_idx].border_flags |= BorderFlags.HIDE_RIGHT
                for mid in range(start_idx + 1, end_idx):
                    row[mid].border_flags |= (BorderFlags.HIDE_LEFT | BorderFlags.HIDE_RIGHT)
                row[end_idx].border_flags |= BorderFlags.HIDE_LEFT

    # Apply Row Merge borders
    max_cols = max(len(row) for row in cells_grid) if cells_grid else 0
    num_rows = len(cells_grid)
    for c in range(max_cols):
        r = 0
        while r < num_rows:
            if c >= len(cells_grid[r]):
                r += 1
                continue

            if cells_grid[r][c].rm_block_id is None:
                r += 1
                continue

            start_row = r
            while r < num_rows and c < len(cells_grid[r]) and cells_grid[r][c].rm_block_id is not None:
                r += 1
            end_row = r - 1

            if start_row < end_row:
                cells_grid[start_row][c].border_flags |= BorderFlags.HIDE_BOTTOM
                for mid in range(start_row + 1, end_row):
                    cells_grid[mid][c].border_flags |= (BorderFlags.HIDE_TOP | BorderFlags.HIDE_BOTTOM)
                cells_grid[end_row][c].border_flags |= BorderFlags.HIDE_TOP

    return cells_grid

def _parse_args_string(arg_str: str):
    """
    Parses the full arguments string into parameters and the raw data block.
    """
    parts = []
    current = []
    depth = 0
    in_quote = False
    quote_char = None
    i = 0
    n = len(arg_str)

    while i < n:
        c = arg_str[i]
        if not in_quote:
            if c in ('"', "'"):
                in_quote = True
                quote_char = c
                current.append(c)
            elif c == '(':
                depth += 1
                current.append(c)
            elif c == ')':
                depth -= 1
                current.append(c)
            elif c == ',' and depth == 0:
                parts.append("".join(current).strip())
                current = []
            else:
                current.append(c)
        else:
            if c == quote_char:
                in_quote = False
            current.append(c)
        i += 1
        
    if current:
        parts.append("".join(current).strip())

    return parts

def _overlay_style_and_data(style_grid: list[list[CellDesc]], data_grid: list[list[CellDesc]]) -> list[list[CellDesc]]:
    """
    Overlays a presentation style grid of cells onto a content data grid of cells.
    Returns a new merged 2D grid of CellDesc.
    """
    cells_grid = []
    max_r = max(len(style_grid), len(data_grid))
    for r in range(max_r):
        row_cells = []
        style_row_len = len(style_grid[r]) if r < len(style_grid) else 0
        data_row_len = len(data_grid[r]) if r < len(data_grid) else 0
        max_c = max(style_row_len, data_row_len)
        
        for c in range(max_c):
            merged_cell = CellDesc()
            style_cell = style_grid[r][c] if r < len(style_grid) and c < len(style_grid[r]) else None
            data_cell = data_grid[r][c] if r < len(data_grid) and c < len(data_grid[r]) else None

            if style_cell:
                merged_cell.cm_block_id = style_cell.cm_block_id
                merged_cell.rm_block_id = style_cell.rm_block_id
                merged_cell.border_flags = style_cell.border_flags
                merged_cell.styles = dict(style_cell.styles)

            if data_cell:
                merged_cell.raw_expr = data_cell.raw_expr
                merged_cell.text_parts = list(data_cell.text_parts)
                if data_cell.cm_block_id is not None:
                    merged_cell.cm_block_id = data_cell.cm_block_id
                if data_cell.rm_block_id is not None:
                    merged_cell.rm_block_id = data_cell.rm_block_id
                merged_cell.border_flags |= data_cell.border_flags
                for k, v in data_cell.styles.items():
                    merged_cell.styles[k] = v

            row_cells.append(merged_cell)
        cells_grid.append(row_cells)
    return cells_grid

def parse(formula_args: str, context: dict = None) -> TableModel:
    """
    Parses formula arguments string, style and data blocks into a TableModel.
    Supports both legacy format (only data) and new format (style and data).
    """
    args = _parse_args_string(formula_args)
    if len(args) < 6:
        raise ValueError("TABLE requires at least 6 arguments (rows, cols, border_width, border_color, border_style, stretch)")

    rows = int(args[0])
    cols = int(args[1])
    border_width = int(args[2])
    border_color = args[3].strip('"\'')
    border_style = args[4].strip('"\'')
    stretch = int(args[5])

    cell_height = 30
    style_block_str = None
    data_block_str = None

    rem = args[6:]
    if len(rem) == 1:
        data_block_str = rem[0]
    elif len(rem) == 2:
        if rem[0].lower().startswith('style('):
            style_block_str = rem[0]
            data_block_str = rem[1]
        else:
            cell_height = int(rem[0])
            data_block_str = rem[1]
    elif len(rem) >= 3:
        cell_height = int(rem[0])
        style_block_str = rem[1]
        data_block_str = rem[2]

    cells_grid = []

    if style_block_str and data_block_str:
        style_inner = ""
        match_style = _re.match(r'(?is)^style\((.*)\)$', style_block_str)
        if match_style:
            style_inner = match_style.group(1).strip()
        style_grid = _parse_data_arg(style_inner, context)

        data_inner = ""
        match_data = _re.match(r'(?is)^data\((.*)\)$', data_block_str)
        if match_data:
            data_inner = match_data.group(1).strip()
        data_grid = _parse_data_arg(data_inner, context)

        cells_grid = _overlay_style_and_data(style_grid, data_grid)
    elif data_block_str:
        match = _re.match(r'(?is)^data\((.*)\)$', data_block_str)
        if match:
            data_inner = match.group(1).strip()
            cells_grid = _parse_data_arg(data_inner, context)

    return TableModel(
        rows=rows,
        cols=cols,
        cells=cells_grid,
        border_width=border_width,
        border_color=border_color,
        border_style=border_style,
        stretch=stretch,
        cell_height=cell_height
    )

def render_html(model: TableModel) -> str:
    """
    Renders a TableModel into an HTML table string.
    """
    border_style = str(model.border_style).strip().lower()
    apply_to_outer = True
    apply_to_inner = False
    if border_style.endswith("-1"):
        apply_to_inner = True
        apply_to_outer = True
        border_style = border_style[:-2]
    elif border_style.endswith("-0"):
        apply_to_inner = False
        apply_to_outer = False
        border_style = border_style[:-2]

    table_border = f"border:{model.border_width}px {border_style} {model.border_color};" if apply_to_outer else ""
    table_style = f"border-collapse:collapse;{table_border}"
    if model.stretch == 1:
        table_style += "width:100%;height:100%;table-layout:fixed;"
    else:
        table_style += "width:100%;table-layout:fixed;"

    html = [f'<table style="{table_style}">']

    row_height_style = ""
    if model.stretch == 1:
        if model.rows > 0:
            row_height_style = f"height:{100.0 / model.rows}%;"
    else:
        row_height_style = f"height:{model.cell_height}px;"

    td_border = f"border:{model.border_width}px {border_style} {model.border_color};" if apply_to_inner else ""

    for r in range(model.rows):
        html.append(f'<tr style="{row_height_style}">')
        for c in range(model.cols):
            val = ""
            border_overrides = []

            if r < len(model.cells) and c < len(model.cells[r]):
                cell = model.cells[r][c]
                val = cell.raw_expr
                if val == 'None':
                    val = ''
                
                if cell.border_flags & BorderFlags.HIDE_LEFT:
                    border_overrides.append("border-left:none;")
                if cell.border_flags & BorderFlags.HIDE_RIGHT:
                    border_overrides.append("border-right:none;")
                if cell.border_flags & BorderFlags.HIDE_TOP:
                    border_overrides.append("border-top:none;")
                if cell.border_flags & BorderFlags.HIDE_BOTTOM:
                    border_overrides.append("border-bottom:none;")

                # Serialize inline styles (excluding href which is rendered as anchor tag)
                href = None
                for prop, prop_val in cell.styles.items():
                    if prop == 'href':
                        href = prop_val
                    else:
                        border_overrides.append(f"{prop}:{prop_val};")

            overrides_css = "".join(border_overrides)
            td_style = f"{td_border}padding:0;{overrides_css}"
            
            if model.stretch == 0:
                td_style += f"height:{model.cell_height}px;"

            # Wrap with anchor if url tag was used
            if href:
                val = f'<a href="{href}" style="color:inherit;text-decoration:inherit;">{val}</a>'

            html.append(f'<td style="{td_style}">{val}</td>')
        html.append('</tr>')

    html.append('</table>')
    return "".join(html)

def _normalize_color_to_hex(color_str: str) -> str:
    color_str = color_str.strip().strip('"\'').lower()
    
    color_map = {
        'black': '000000', 'white': 'ffffff', 'red': 'ff0000',
        'green': '008000', 'blue': '0000ff', 'yellow': 'ffff00',
        'gray': '808080', 'grey': '808080', 'silver': 'c0c0c0',
        'maroon': '800000', 'purple': '800080', 'fuchsia': 'ff00ff',
        'lime': '00ff00', 'olive': '808000', 'navy': '000080',
        'teal': '008080', 'aqua': '00ffff', 'orange': 'ffa500'
    }
    
    if color_str in color_map:
        return color_map[color_str]
        
    hex_val = color_str.replace('#', '')
    if len(hex_val) == 3:
        return "".join(c * 2 for c in hex_val)
    elif len(hex_val) in (6, 8):
        return hex_val
        
    return '000000'

def _write_model_to_sheet(model: TableModel, ws, start_row: int = 1):
    from openpyxl.styles import Border, Side, Alignment, Font, PatternFill
    
    # Configure borders mapping
    border_style = str(model.border_style).strip().lower()
    apply_to_outer = True
    apply_to_inner = False
    if border_style.endswith("-1"):
        apply_to_inner = True
        apply_to_outer = True
        border_style = border_style[:-2]
    elif border_style.endswith("-0"):
        apply_to_inner = False
        apply_to_outer = False
        border_style = border_style[:-2]

    excel_border_style = 'thin'
    if border_style == 'dashed':
        excel_border_style = 'dashed'
    elif border_style == 'dotted':
        excel_border_style = 'dotted'
    elif model.border_width > 1:
        excel_border_style = 'medium'
        
    excel_color = _normalize_color_to_hex(model.border_color)
    border_side = Side(style=excel_border_style, color=excel_color)
    
    # Write values, borders, alignments, and heights
    for r in range(model.rows):
        if model.stretch == 0:
            ws.row_dimensions[start_row + r].height = model.cell_height
            
        for c in range(model.cols):
            cell_ref = ws.cell(row=start_row + r, column=c + 1)
            
            val = ""
            cell_styles = {}
            if r < len(model.cells) and c < len(model.cells[r]):
                val = model.cells[r][c].raw_expr
                if val == 'None':
                    val = ''
                cell_styles = model.cells[r][c].styles
            cell_ref.value = val
            
            if apply_to_inner:
                cell_ref.border = Border(left=border_side, right=border_side, top=border_side, bottom=border_side)
            elif apply_to_outer:
                left_s = border_side if c == 0 else Side()
                right_s = border_side if c == model.cols - 1 else Side()
                top_s = border_side if r == 0 else Side()
                bottom_s = border_side if r == model.rows - 1 else Side()
                cell_ref.border = Border(left=left_s, right=right_s, top=top_s, bottom=bottom_s)
            else:
                cell_ref.border = Border()

            h_align = cell_styles.get('text-align', 'center')
            cell_ref.alignment = Alignment(horizontal=h_align, vertical='center', wrap_text=True)

            # Apply font styles (bold, italic, color, size)
            is_bold = cell_styles.get('font-weight') == 'bold'
            is_italic = cell_styles.get('font-style') == 'italic'
            font_color = None
            if 'color' in cell_styles:
                font_color = _normalize_color_to_hex(cell_styles['color'])
            font_size = None
            if 'font-size' in cell_styles:
                num_match = _re.search(r'\d+', cell_styles['font-size'])
                if num_match:
                    font_size = int(num_match.group(0))
                
            decorations = cell_styles.get('text-decoration', '').split()
            is_underline = 'underline' in decorations
            is_strike = 'line-through' in decorations
                
            if is_bold or is_italic or font_color or font_size or is_underline or is_strike:
                cell_ref.font = Font(
                    bold=is_bold, 
                    italic=is_italic, 
                    color=font_color,
                    size=font_size,
                    underline="single" if is_underline else None,
                    strike=is_strike
                )
                
            # Apply background color
            if 'background-color' in cell_styles:
                bg_color = _normalize_color_to_hex(cell_styles['background-color'])
                cell_ref.fill = PatternFill(
                    start_color=bg_color, 
                    end_color=bg_color, 
                    fill_type='solid'
                )

            # Apply hyperlink if url tag was used
            if 'href' in cell_styles:
                cell_ref.hyperlink = cell_styles['href']
                # Apply standard hyperlink styling if no color already set
                if 'color' not in cell_styles:
                    cell_ref.font = Font(
                        bold=is_bold, italic=is_italic,
                        size=font_size,
                        underline='single',
                        color='0563C1'  # Excel default hyperlink blue
                    )

    # Find connected components of merged cells to apply spreadsheet merges
    visited = set()
    for r in range(model.rows):
        for c in range(model.cols):
            if (r, c) in visited:
                continue
                
            component = []
            queue = [(r, c)]
            visited.add((r, c))
            
            while queue:
                curr_r, curr_c = queue.pop(0)
                component.append((curr_r, curr_c))
                
                # Check right neighbor
                if curr_c < model.cols - 1:
                    if curr_r < len(model.cells) and curr_c < len(model.cells[curr_r]):
                        cell = model.cells[curr_r][curr_c]
                        if cell.border_flags & BorderFlags.HIDE_RIGHT:
                            if (curr_r, curr_c + 1) not in visited:
                                visited.add((curr_r, curr_c + 1))
                                queue.append((curr_r, curr_c + 1))
                # Check left neighbor
                if curr_c > 0:
                    if curr_r < len(model.cells) and curr_c < len(model.cells[curr_r]):
                        cell = model.cells[curr_r][curr_c]
                        if cell.border_flags & BorderFlags.HIDE_LEFT:
                            if (curr_r, curr_c - 1) not in visited:
                                visited.add((curr_r, curr_c - 1))
                                queue.append((curr_r, curr_c - 1))
                # Check bottom neighbor
                if curr_r < model.rows - 1:
                    if curr_r < len(model.cells) and curr_c < len(model.cells[curr_r]):
                        cell = model.cells[curr_r][curr_c]
                        if cell.border_flags & BorderFlags.HIDE_BOTTOM:
                            if (curr_r + 1, curr_c) not in visited:
                                visited.add((curr_r + 1, curr_c))
                                queue.append((curr_r + 1, curr_c))
                # Check top neighbor
                if curr_r > 0:
                    if curr_r < len(model.cells) and curr_c < len(model.cells[curr_r]):
                        cell = model.cells[curr_r][curr_c]
                        if cell.border_flags & BorderFlags.HIDE_TOP:
                            if (curr_r - 1, curr_c) not in visited:
                                visited.add((curr_r - 1, curr_c))
                                queue.append((curr_r - 1, curr_c))
                                
            if len(component) > 1:
                min_r = min(x[0] for x in component)
                max_r = max(x[0] for x in component)
                min_c = min(x[1] for x in component)
                max_c = max(x[1] for x in component)
                ws.merge_cells(
                    start_row=start_row + min_r, 
                    start_column=min_c + 1, 
                    end_row=start_row + max_r, 
                    end_column=max_c + 1
                )

def render_xlsx(model: TableModel, filepath_or_stream):
    """
    Renders a TableModel into an Excel (.xlsx) file.
    Requires openpyxl to be installed.
    """
    try:
        import openpyxl
    except ImportError:
        raise ImportError("The 'openpyxl' package is required for Excel rendering. Please install it using 'pip install openpyxl'.")

    wb = openpyxl.Workbook()
    # Remove default active sheet
    wb.remove(wb.active)
    ws = wb.create_sheet(title="Table")
    _write_model_to_sheet(model, ws, start_row=1)
    wb.save(filepath_or_stream)

def _create_pdf_table_object(model: TableModel):
    from reportlab.lib import colors
    from reportlab.platypus import Table, TableStyle, Paragraph
    from reportlab.lib.styles import ParagraphStyle

    # Convert border/background color to reportlab color
    def hex_to_rl_color(hex_str: str, default=colors.black):
        if not hex_str:
            return default
        hex_str = hex_str.strip().lstrip('#')
        if len(hex_str) == 3:
            hex_str = ''.join([c*2 for c in hex_str])
        try:
            return colors.HexColor('#' + hex_str)
        except Exception:
            return default

    data_matrix = []
    table_styles = []

    # Configure grid borders
    border_style = str(model.border_style).strip().lower()
    apply_to_outer = True
    apply_to_inner = False
    if border_style.endswith("-1"):
        apply_to_inner = True
        apply_to_outer = True
        border_style = border_style[:-2]
    elif border_style.endswith("-0"):
        apply_to_inner = False
        apply_to_outer = False
        border_style = border_style[:-2]

    border_w = max(0.5, float(model.border_width))
    border_c = hex_to_rl_color(model.border_color)
    if apply_to_inner:
        table_styles.append(('GRID', (0, 0), (-1, -1), border_w, border_c))
    elif apply_to_outer:
        table_styles.append(('BOX', (0, 0), (-1, -1), border_w, border_c))
        
    table_styles.append(('VALIGN', (0, 0), (-1, -1), 'MIDDLE'))

    # Calculate connected components of merged cells for SPAN commands
    visited = set()
    for r in range(model.rows):
        for c in range(model.cols):
            if (r, c) in visited:
                continue
            component = []
            queue = [(r, c)]
            visited.add((r, c))
            while queue:
                curr_r, curr_c = queue.pop(0)
                component.append((curr_r, curr_c))
                # right
                if curr_c < model.cols - 1 and curr_r < len(model.cells) and curr_c < len(model.cells[curr_r]):
                    if model.cells[curr_r][curr_c].border_flags & BorderFlags.HIDE_RIGHT:
                        if (curr_r, curr_c + 1) not in visited:
                            visited.add((curr_r, curr_c + 1))
                            queue.append((curr_r, curr_c + 1))
                # left
                if curr_c > 0 and curr_r < len(model.cells) and curr_c < len(model.cells[curr_r]):
                    if model.cells[curr_r][curr_c].border_flags & BorderFlags.HIDE_LEFT:
                        if (curr_r, curr_c - 1) not in visited:
                            visited.add((curr_r, curr_c - 1))
                            queue.append((curr_r, curr_c - 1))
                # bottom
                if curr_r < model.rows - 1 and curr_r < len(model.cells) and curr_c < len(model.cells[curr_r]):
                    if model.cells[curr_r][curr_c].border_flags & BorderFlags.HIDE_BOTTOM:
                        if (curr_r + 1, curr_c) not in visited:
                            visited.add((curr_r + 1, curr_c))
                            queue.append((curr_r + 1, curr_c))
                # top
                if curr_r > 0 and curr_r < len(model.cells) and curr_c < len(model.cells[curr_r]):
                    if model.cells[curr_r][curr_c].border_flags & BorderFlags.HIDE_TOP:
                        if (curr_r - 1, curr_c) not in visited:
                            visited.add((curr_r - 1, curr_c))
                            queue.append((curr_r - 1, curr_c))
            if len(component) > 1:
                min_r = min(x[0] for x in component)
                max_r = max(x[0] for x in component)
                min_c = min(x[1] for x in component)
                max_c = max(x[1] for x in component)
                table_styles.append(('SPAN', (min_c, min_r), (max_c, max_r)))

    for r in range(model.rows):
        row_data = []
        for c in range(model.cols):
            val = ""
            cell_styles = {}
            if r < len(model.cells) and c < len(model.cells[r]):
                val = model.cells[r][c].raw_expr
                if val == 'None':
                    val = ''
                cell_styles = model.cells[r][c].styles

            # Background fill
            if 'background-color' in cell_styles:
                bg_c = hex_to_rl_color(cell_styles['background-color'])
                table_styles.append(('BACKGROUND', (c, r), (c, r), bg_c))

            # Alignment
            h_align = cell_styles.get('text-align', 'center').upper()
            if h_align in ('LEFT', 'CENTER', 'RIGHT'):
                table_styles.append(('ALIGN', (c, r), (c, r), h_align))

            # Typography formatting
            is_bold = cell_styles.get('font-weight') == 'bold'
            is_italic = cell_styles.get('font-style') == 'italic'
            font_color = hex_to_rl_color(cell_styles.get('color', ''), default=colors.black)
            decorations_pdf = cell_styles.get('text-decoration', '').split()
            is_underline = 'underline' in decorations_pdf
            is_strike = 'line-through' in decorations_pdf
            
            font_size = 11
            if 'font-size' in cell_styles:
                num_match = _re.search(r'\d+', cell_styles['font-size'])
                if num_match:
                    font_size = int(num_match.group(0))

            font_name = 'Helvetica'
            if is_bold and is_italic:
                font_name = 'Helvetica-BoldOblique'
            elif is_bold:
                font_name = 'Helvetica-Bold'
            elif is_italic:
                font_name = 'Helvetica-Oblique'

            table_styles.append(('FONTNAME', (c, r), (c, r), font_name))
            table_styles.append(('FONTSIZE', (c, r), (c, r), font_size))
            table_styles.append(('TEXTCOLOR', (c, r), (c, r), font_color))
            if is_underline:
                table_styles.append(('UNDERLINE', (c, r), (c, r)))
            if is_strike:
                table_styles.append(('STRIKETHROUGH', (c, r), (c, r)))

            href_pdf = cell_styles.get('href')
            if href_pdf and 'color' not in cell_styles:
                # Default hyperlink blue
                table_styles.append(('TEXTCOLOR', (c, r), (c, r), colors.HexColor('#0563C1')))
                table_styles.append(('UNDERLINE', (c, r), (c, r)))

            if val != '':
                rl_align = 1 # center
                if h_align == 'LEFT':
                    rl_align = 0
                elif h_align == 'RIGHT':
                    rl_align = 2
                
                p_style = ParagraphStyle(
                    f'Cell_{r}_{c}',
                    fontName=font_name,
                    fontSize=font_size,
                    leading=font_size + 3,
                    textColor=font_color,
                    alignment=rl_align
                )
                cell_text = str(val)
                if is_underline:
                    cell_text = f'<u>{cell_text}</u>'
                if is_strike:
                    cell_text = f'<strike>{cell_text}</strike>'
                if href_pdf:
                    cell_text = f'<link href="{href_pdf}">{cell_text}</link>'
                row_data.append(Paragraph(cell_text, p_style))
            else:
                row_data.append("")
        data_matrix.append(row_data)

    row_heights = None
    if model.stretch == 0 and model.cell_height > 0:
        row_heights = [max(25, model.cell_height)] * model.rows

    return Table(data_matrix, rowHeights=row_heights, style=TableStyle(table_styles))

def render_pdf(model: TableModel, filepath_or_stream: _Union[str, _Any]) -> None:
    """
    Renders a TableModel directly to a PDF document using ReportLab.
    Translates IR coordinates, merged regions, background fills, fonts, and borders into native ReportLab TableStyles.
    """
    try:
        from reportlab.lib.pagesizes import letter, landscape
        from reportlab.platypus import SimpleDocTemplate
    except ImportError:
        raise ImportError(
            "The 'reportlab' package is required for PDF rendering. "
            "Install it via 'pip install tentags[pdf]' or 'pip install reportlab'."
        )

    doc = SimpleDocTemplate(
        filepath_or_stream,
        pagesize=landscape(letter) if model.cols > 4 else letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    table = _create_pdf_table_object(model)
    doc.build([table])

def _load_style(filepath_or_str: _Union[str, list], context: dict = None) -> list[list[CellDesc]]:
    if not isinstance(filepath_or_str, str):
        return filepath_or_str
    
    content = filepath_or_str
    if _os.path.exists(filepath_or_str):
        with open(filepath_or_str, 'r', encoding='utf-8') as f:
            content = f.read()
    
    content = content.strip()
    match = _re.match(r'(?is)^style\((.*)\)$', content)
    if match:
        content = match.group(1).strip()
    return _parse_data_arg(content, context)

def _load_data(filepath_or_str: _Union[str, list], context: dict = None) -> list[list[CellDesc]]:
    if not isinstance(filepath_or_str, str):
        return filepath_or_str
    
    content = filepath_or_str
    if _os.path.exists(filepath_or_str):
        with open(filepath_or_str, 'r', encoding='utf-8') as f:
            content = f.read()
    
    content = content.strip()
    match = _re.match(r'(?is)^data\((.*)\)$', content)
    if match:
        content = match.group(1).strip()
    return _parse_data_arg(content, context)

def _csv_load(filepath_or_url: str) -> list[list[CellDesc]]:
    raw_data = _load_csv(filepath_or_url)
    grid = []
    for r in raw_data:
        row = []
        for val in r:
            cell = CellDesc()
            cell.raw_expr = val.strip()
            cell.text_parts = [cell.raw_expr]
            row.append(cell)
        grid.append(row)
    return grid

def compile(preamble: _Any, style: _Any, data: _Any, context: dict = None) -> TableModel:
    """
    Compiles TenTags style and data sources into an intermediate representation (TableModel).
    
    The returned TableModel can later be rendered into HTML, PDF, or XLSX formats.
    """
    style_grid = _load_style(style, context)
    data_grid = _load_data(data, context)
    
    cells_grid = _overlay_style_and_data(style_grid, data_grid)
    
    rows = len(cells_grid)
    cols = max(len(row) for row in cells_grid) if cells_grid else 0
    border_width = 1
    border_color = "#cbd5e1"
    border_style = "solid"
    stretch = 0
    cell_height = 30

    if preamble:
        if isinstance(preamble, str):
            p_args = _parse_args_string(preamble)
            if len(p_args) >= 6:
                rows = int(p_args[0])
                cols = int(p_args[1])
                border_width = int(p_args[2])
                border_color = p_args[3].strip('"\'')
                border_style = p_args[4].strip('"\'')
                stretch = int(p_args[5])
                if len(p_args) >= 7:
                    cell_height = int(p_args[6])
            elif len(p_args) >= 3:
                border_width = int(p_args[0])
                border_color = p_args[1].strip('"\'')
                border_style = p_args[2].strip('"\'')
                if len(p_args) >= 4:
                    stretch = int(p_args[3])
                if len(p_args) >= 5:
                    cell_height = int(p_args[4])
        elif isinstance(preamble, dict):
            border_width = preamble.get('border_width', border_width)
            border_color = preamble.get('border_color', border_color)
            border_style = preamble.get('border_style', border_style)
            stretch = preamble.get('stretch', stretch)
            cell_height = preamble.get('cell_height', cell_height)
            rows = preamble.get('rows', rows)
            cols = preamble.get('cols', cols)

    return TableModel(
        rows=rows,
        cols=cols,
        cells=cells_grid,
        border_width=border_width,
        border_color=border_color,
        border_style=border_style,
        stretch=stretch,
        cell_height=cell_height
    )

def render(preamble_or_formula: _Any, style: _Any = None, data: _Any = None, context: dict = None) -> str:
    """
    Renders a TenTags table directly to an HTML string.

    Supports two calling styles:
    
    1. Render a self-contained layout formula:
       import tentags
       html = tentags.render('3,3,1,"black","solid",0, data(A,B,C; D,E,F; G,H,I)')

    2. Render with decoupled style templates, data blocks, and preambles:
       import tentags
       preamble = '3, 3, 1, "blue", "solid-1"'
       style = 'style(<bg=white><center><b><cm>Title, , </cm></b></center></bg>; A, B, C)'
       data = 'data( , , ; Value A, Value B, Value C)'
       html = tentags.render(preamble, style, data)

    Parameters:
        preamble_or_formula: Either a self-contained TenTags formula string, or a layout preamble.
        style: Optional style block (string or list of cells).
        data: Optional data block (string or list of cells).
        context: Optional dictionary of variable substitutions.

    Returns:
        A formatted <table>...</table> HTML string.
    """
    if isinstance(style, dict) and data is None and context is None:
        context = style
        style = None

    try:
        if style is not None and data is not None:
            model = compile(preamble_or_formula, style, data, context)
        else:
            model = parse(preamble_or_formula, context)
        return render_html(model)
    except Exception as e:
        return str(e)

def multitable_html(
    tables: list, 
    layout: str = "vertical", 
    cols: int = 1, 
    gap: str = "24px", 
    full_page: bool = False, 
    context: dict = None
) -> str:
    """
    Assembles and renders multiple tables into a single HTML string.
    """
    rendered_tables = []
    for item in tables:
        if isinstance(item, TableModel):
            model = item
            title = None
        elif isinstance(item, dict):
            model = compile(
                style=item.get("style"),
                data=item.get("data"),
                preamble=item.get("preamble"),
                context=context
            )
            title = item.get("title")
        else:
            raise TypeError("Each table in 'tables' must be a TableModel or a dict.")
        
        table_html = render_html(model)
        if title:
            table_html = f"<div><h3>{title}</h3>{table_html}</div>"
        rendered_tables.append(table_html)

    if layout == "grid":
        style_container = f"display: grid; grid-template-columns: repeat({cols}, 1fr); gap: {gap};"
    else:
        style_container = f"display: flex; flex-direction: column; gap: {gap};"

    container = f'<div style="{style_container}">\n' + "\n".join(rendered_tables) + '\n</div>'

    if full_page:
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Multi-Table Report</title>
</head>
<body>
    {container}
</body>
</html>"""
    return container

def multitable_xlsx(
    tables: list, 
    filepath_or_stream, 
    mode: str = "sheets", 
    gap: int = 3, 
    show_titles: bool = True, 
    context: dict = None
) -> None:
    """
    Assembles and renders multiple tables into a single Excel (.xlsx) workbook.
    """
    try:
        import openpyxl
        from openpyxl.styles import Font
    except ImportError:
        raise ImportError("The 'openpyxl' package is required for Excel rendering. Please install it using 'pip install openpyxl'.")

    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    if mode == "sheets":
        for i, item in enumerate(tables):
            if isinstance(item, TableModel):
                model = item
                sheet_name = f"Table {i + 1}"
            elif isinstance(item, dict):
                model = compile(
                    style=item.get("style"),
                    data=item.get("data"),
                    preamble=item.get("preamble"),
                    context=context
                )
                sheet_name = item.get("sheet_name") or f"Table {i + 1}"
            else:
                raise TypeError("Each table in 'tables' must be a TableModel or a dict.")
            
            ws = wb.create_sheet(title=sheet_name)
            _write_model_to_sheet(model, ws, start_row=1)
    else: # stacked
        ws = wb.create_sheet(title="Report")
        current_row = 1
        for i, item in enumerate(tables):
            if isinstance(item, TableModel):
                model = item
                title = None
            elif isinstance(item, dict):
                model = compile(
                    style=item.get("style"),
                    data=item.get("data"),
                    preamble=item.get("preamble"),
                    context=context
                )
                title = item.get("title")
            else:
                raise TypeError("Each table in 'tables' must be a TableModel or a dict.")
            
            if show_titles and title:
                cell = ws.cell(row=current_row, column=1)
                cell.value = title
                cell.font = Font(bold=True, size=14)
                current_row += 1
            
            _write_model_to_sheet(model, ws, start_row=current_row)
            current_row += model.rows + gap

    wb.save(filepath_or_stream)

def multitable_pdf(
    tables: list, 
    filepath_or_stream, 
    page_size: str = "letter", 
    orientation: str = "portrait", 
    page_break_after_each: bool = True, 
    margins: tuple = (36, 36, 36, 36), 
    context: dict = None
) -> None:
    """
    Assembles and renders multiple tables into a single PDF document.
    """
    try:
        from reportlab.lib.pagesizes import letter, landscape
        from reportlab.platypus import SimpleDocTemplate, PageBreak, Paragraph
        from reportlab.lib.styles import ParagraphStyle
    except ImportError:
        raise ImportError(
            "The 'reportlab' package is required for PDF rendering. "
            "Install it via 'pip install tentags[pdf]' or 'pip install reportlab'."
        )

    # Resolve page size
    base_page_size = letter
    if page_size.lower() == "a4":
        from reportlab.lib.pagesizes import A4
        base_page_size = A4

    actual_page_size = landscape(base_page_size) if orientation.lower() == "landscape" else base_page_size

    doc = SimpleDocTemplate(
        filepath_or_stream,
        pagesize=actual_page_size,
        leftMargin=margins[0],
        rightMargin=margins[1],
        topMargin=margins[2],
        bottomMargin=margins[3]
    )

    story = []
    for i, item in enumerate(tables):
        if isinstance(item, TableModel):
            model = item
            title = None
        elif isinstance(item, dict):
            model = compile(
                style=item.get("style"),
                data=item.get("data"),
                preamble=item.get("preamble"),
                context=context
            )
            title = item.get("title")
        else:
            raise TypeError("Each table in 'tables' must be a TableModel or a dict.")

        if title:
            p_style = ParagraphStyle(
                f"Title_{i}", 
                fontName="Helvetica-Bold", 
                fontSize=14, 
                leading=18, 
                spaceAfter=10
            )
            story.append(Paragraph(title, p_style))

        table_obj = _create_pdf_table_object(model)
        story.append(table_obj)

        if page_break_after_each and i < len(tables) - 1:
            story.append(PageBreak())

    doc.build(story)

def features() -> dict:
    """
    Returns the availability of optional render backends depending on local dependencies.

    Example output:
    {
        "html": True,
        "pdf": True,
        "xlsx": False
    }
    """
    has_pdf = False
    try:
        from reportlab.platypus import SimpleDocTemplate
        has_pdf = True
    except ImportError:
        pass

    has_xlsx = False
    try:
        import openpyxl
        has_xlsx = True
    except ImportError:
        pass

    return {
        "html": True,
        "pdf": has_pdf,
        "xlsx": has_xlsx
    }

def info() -> None:
    """
    Prints package version, available renderers, optional dependencies,
    and system diagnostic information to the console.
    """
    import sys
    feats = features()
    
    print(f"TenTags {__version__}\n")
    print(f"Author       {__author__}")
    print(f"License      {__license__}")
    print(f"Website      {__homepage__}\n")
    
    print(f"Python       {sys.version.split()[0]}\n")
    
    print("Features")
    print("────────")
    print(f"{'✓' if feats['html'] else '✗'} HTML")
    print(f"{'✓' if feats['pdf'] else '✗'} PDF")
    print(f"{'✓' if feats['xlsx'] else '✗'} XLSX")
    print("✓ Validation")
    print("✓ Demo")

def validate(formula: str) -> dict:
    """
    Validates a TenTags formula's syntax and tag balance.
    Returns a dict with 'status' ('ok' or 'error') and a descriptive message.
    """
    if not isinstance(formula, str):
        return {"status": "error", "message": "Formula must be a string."}
        
    try:
        parse(formula)
        return {"status": "ok", "message": "Syntax OK"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def demo(name: str = "dashboard", filepath_prefix: str = "demo") -> None:
    """
    Generates a demonstration report to showcase TenTags output formats.
    Supported names: 'dashboard', 'invoice', 'table'.
    """
    name = name.lower()
    if name == "dashboard":
        preamble = '4, 4, 1, "#cbd5e1", "solid", 0, 45'
        style = 'style(<fs=18><bg=#1e293b><color=white><b><cm>Q3 Financial Performance Dashboard, , , , </cm></b></color></bg></fs>; <bg=#f1f5f9><b><left>Department</left></b></bg>, <bg=#f1f5f9><b><center>Revenue</center></b></bg>, <bg=#f1f5f9><b><center>Expenses</center></b></bg>, <bg=#f1f5f9><b><center>Net Profit</center></b></bg>; <left>Engineering</left>, <right>"$240,000"</right>, <right>"$180,000"</right>, <bg=#dcfce7><color=#166534><b><right>"+$60,000"</right></b></color></bg>; <left>Sales & Marketing</left>, <right>"$310,000"</right>, <right>"$210,000"</right>, <bg=#dcfce7><color=#166534><b><right>"+$100,000"</right></b></color></bg>)'
        data = 'data()'
    elif name == "invoice":
        preamble = '7, 4, 1, "#e2e8f0", "solid-1", 1, 30'
        style = 'style(<fs=16><b><left><cm>INVOICE #1024, , , </cm></left></b></fs>; <left><cm>Date: 2026-07-14, , , </cm></left>; <bg=#3b82f6><color=white><b>Item</b></color></bg>, <bg=#3b82f6><color=white><b>Quantity</b></color></bg>, <bg=#3b82f6><color=white><b>Price</b></color></bg>, <bg=#3b82f6><color=white><b>Total</b></color></bg>; ; ; ; <right><b><cm>Grand Total: , , </cm></b></right>, <b>$1,650</b>)'
        data = 'data( , , , ; , , , ; Premium Wood Logs, 10, $150, $1,500; Steel Beams, 5, $30, $150; , , , )'
    else:
        preamble = '3, 3, 1, "green", "solid-1", 1'
        style = 'style(<bg=white><center><b><cm>Test Table, , </cm></b></center></bg>; <center><b>Header 1</b></center>, <center><b>Header 2</b></center>, <center><b>Header 3</b></center>; <left>A1</left>, <center>B1</center>, <right>C1</right>)'
        data = 'data()'

    model = compile(style=style, data=data, preamble=preamble)
    
    html_content = render_html(model)
    with open(f"{filepath_prefix}_{name}.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Generated HTML demo: {filepath_prefix}_{name}.html")

    feats = features()
    if feats["xlsx"]:
        render_xlsx(model, f"{filepath_prefix}_{name}.xlsx")
        print(f"Generated Excel demo: {filepath_prefix}_{name}.xlsx")
        
    if feats["pdf"]:
        render_pdf(model, f"{filepath_prefix}_{name}.pdf")
        print(f"Generated PDF demo: {filepath_prefix}_{name}.pdf")
