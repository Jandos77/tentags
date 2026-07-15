# TenTags — Examples & Reference Guide

A complete guide to TenTags: all tags, template engine integrations, and passing arguments from backend to templates.

---

## Table of Contents

1. [Formula Structure](#1-formula-structure)
2. [Tag Reference](#2-tag-reference)
3. [Python API](#3-python-api)
4. [Django — Template Tags](#4-django--template-tags)
5. [Flask — Jinja2](#5-flask--jinja2)
6. [FastAPI — Jinja2](#6-fastapi--jinja2)
7. [Decoupled API: preamble + style + data](#7-decoupled-api-preamble--style--data)
8. [Real-World Examples](#8-real-world-examples)

---

## 1. Formula Structure

Every TenTags formula has three parts:

```
ROWS, COLS, BORDER_WIDTH, "BORDER_COLOR", "BORDER_STYLE", STRETCH, CELL_HEIGHT, data(...)
```

| Parameter | Type | Description |
|---|---|---|
| `ROWS` | int | Number of rows |
| `COLS` | int | Number of columns |
| `BORDER_WIDTH` | int | Border thickness (px) |
| `BORDER_COLOR` | string | Border color (`"black"`, `"#ccc"`) |
| `BORDER_STYLE` | string | Border style (`"solid"`, `"solid-1"`, `"none"`) |
| `STRETCH` | int | `0` = fixed height, `1` = auto-stretch |
| `CELL_HEIGHT` | int | Cell height in px |
| `data(...)` | block | Cell contents |

**Separators inside `data()`:**
- `,` — next cell (next column)
- `;` — next row

```python
import tentags

html = tentags.render('2, 3, 1, "black", "solid", 0, 40, data(A, B, C; D, E, F)')
```

---

## 2. Tag Reference

Tags are applied **inside cells** within `style()` or `data()` blocks.
All tags must be **closed**: `<tag>content</tag>`.

### Typography

| Tag | Effect | CSS |
|---|---|---|
| `<b>text</b>` | **Bold** | `font-weight: bold` |
| `<i>text</i>` | *Italic* | `font-style: italic` |
| `<u>text</u>` | Underline | `text-decoration: underline` |
| `<s>text</s>` | Strikethrough | `text-decoration: line-through` |
| `<fs=18>text</fs>` | Font size 18px | `font-size: 18px` |

```python
# Bold + italic
tentags.render('1,1,1,"black","solid",0,40, data(<b><i>Important!</i></b>)')

# Underline
tentags.render('1,1,1,"black","solid",0,40, data(<u>Terms and Conditions</u>)')

# Strikethrough old price + new price
tentags.render('1,2,1,"black","solid",0,40, data(<s>"$199"</s>, "$99"))')

# Large font
tentags.render('1,1,1,"black","solid",0,60, data(<fs=24><b>TOTAL</b></fs>)')

# Combine all
tentags.render('1,1,1,"black","solid",0,40, data(<b><u><s>Bold + underlined + struck</s></u></b>)')
```

---

### Color & Background

| Tag | Description |
|---|---|
| `<color=red>text</color>` | Text color (name or hex) |
| `<bg=#f0f0f0>text</bg>` | Cell background color |

```python
# Named colors
tentags.render('1,3,1,"black","solid",0,40, data(<color=red>Loss</color>, <color=green>Profit</color>, <color=blue>Neutral</color>)')

# Hex colors
tentags.render('1,2,1,"#ccc","solid",0,40, data(<bg=#1e293b><color=white>Header</color></bg>, <bg=#f8fafc>Data</bg>)')

# Colored badge
tentags.render('1,1,1,"black","solid",0,50, data(<bg=#dcfce7><color=#166534><b>+$60,000</b></color></bg>)')
```

---

### Alignment

| Tag | Description |
|---|---|
| `<left>text</left>` | Align left |
| `<center>text</center>` | Align center |
| `<right>text</right>` | Align right |

```python
tentags.render('1,3,1,"black","solid",0,40, data(<left>Left</left>, <center>Center</center>, <right>Right</right>)')
```

---

### Cell Merging

| Tag | Description |
|---|---|
| `<cm>text, , </cm>` | Colspan: merge N columns (one `,` per extra cell) |
| `<rm>text</rm>` | Rowspan: merge cells vertically |

```python
# Merge 3 columns
tentags.render('2,3,1,"black","solid",0,40, data(<cm>Header across 3 columns, , </cm>; A, B, C)')

# Merge 2 rows
tentags.render('2,2,1,"black","solid",0,40, data(<rm>Merged cell</rm>, Right 1; <rm> </rm>, Right 2)')
```

---

### Links

| Tag | Description |
|---|---|
| `<url=https://...>text</url>` | Clickable hyperlink |

> **Best practice:** Write `<url>` inside `data()`, not `style()`.
> This keeps your style template reusable across different links.

```python
# Simple link
tentags.render('1,1,1,"black","solid",0,40, data(<url=https://example.com>Visit Site</url>)')

# Bold link
tentags.render('1,1,1,"black","solid",0,40, data(<url=https://example.com><b>Download PDF</b></url>)')

# Decoupled: URL in data(), formatting in style()
tentags.render(
    '1,1,1,"black","solid",0,40',
    'style(<b><left></left></b>)',
    'data(<url=https://example.com>Visit Site</url>)'
)
```

**Rendering per target:**
- **HTML** — `<a href="...">text</a>` inside the `<td>`
- **Excel (XLSX)** — native hyperlink + blue underline font
- **PDF** — clickable `<link href="...">` via ReportLab

---

### CSV Import

```python
# From a local file
tentags.render('5,3,1,"black","solid",0,40, data(csv("data/sales.csv")))')

# From a URL
tentags.render('5,3,1,"black","solid",0,40, data(csv("https://example.com/data.csv")))')
```

---

## 3. Python API

### Simple Rendering

```python
import tentags

# Full formula in one string
html = tentags.render('2,2,1,"black","solid",0,40, data(A, B; C, D)')

# With context variables
context = {'name': 'Alice', 'role': 'Admin'}
html = tentags.render('1,2,1,"black","solid",0,40, data(name, role)', context)
```

### Compile once, render to multiple formats

```python
import tentags

model = tentags.parse('2,2,1,"black","solid",0,40, data(A, B; C, D)')

html = tentags.render_html(model)           # HTML string
tentags.render_xlsx(model, 'out.xlsx')      # Excel file
tentags.render_pdf(model,  'out.pdf')       # PDF file
```

### Decoupled API

```python
import tentags

preamble = '2, 3, 1, "#ccc", "solid", 0, 40'
style    = 'style(<bg=#1e293b><color=white><b><cm>Title, , </cm></b></color></bg>; <left></left>, <center></center>, <right></right>)'
data     = 'data(Department, Employees, Budget; Engineering, 12, "$500,000")'

html  = tentags.render(preamble, style, data)

# Same style template, different data
html2 = tentags.render(preamble, style, 'data(Marketing, 8, "$200,000")')
```

---

## 4. Django — Template Tags

### Setup

```python
# settings.py
INSTALLED_APPS = [
    ...
    'tentags',
]
```

After this, tags are available via `{% load tentags %}`.

---

### `{% tt %}` — formula directly in the template

```python
# views.py
def report_view(request):
    return render(request, 'report.html', {
        'dept':     'Engineering',
        'revenue':  '$240,000',
        'expenses': '$180,000',
        'profit':   '+$60,000',
    })
```

```html
{# report.html #}
{% load tentags %}

{% tt %}
4, 4, 1, "#cbd5e1", "solid", 0, 45,
style(
    <fs=18><bg=#1e293b><color=white><b><cm>Financial Report, , , </cm></b></color></bg></fs>;
    <bg=#f1f5f9><b><left>Department</left></b></bg>,
    <bg=#f1f5f9><b><center>Revenue</center></b></bg>,
    <bg=#f1f5f9><b><center>Expenses</center></b></bg>,
    <bg=#f1f5f9><b><center>Net Profit</center></b></bg>
),
data(
    , , , ;
    {{ dept }}, {{ revenue }}, {{ expenses }},
    <bg=#dcfce7><color=#166534><b><right>{{ profit }}</right></b></color></bg>
)
{% endtt %}
```

---

### `{% tentags_inline %}` — formula passed from backend

```python
# views.py
def badge_view(request):
    user_name = "Alice Johnson"
    formula = (
        f"1, 2, 1, '#38bdf8', 'solid', 0, 50, "
        f"data(<b>User:</b> {user_name}, Role: Admin)"
    )
    return render(request, 'badge.html', {'formula': formula})
```

```html
{# badge.html #}
{% load tentags %}

{% tentags_inline formula %}
```

---

### `{% tentags_inline %}` — decoupled mode (3 arguments)

Pass `preamble`, `style`, and `data` as separate variables — one style template reused for multiple rows:

```python
# views.py
def user_table_view(request):
    preamble    = "1, 2, 1, '#10b981', 'solid', 0, 50"
    style_block = "style(<b><left></left></b>, <right></right>)"
    users = [("Alice", "Admin"), ("Bob", "Editor"), ("Charlie", "Viewer")]

    return render(request, 'users.html', {
        'preamble':    preamble,
        'style_block': style_block,
        'data_blocks': [f"data({name}, {role})" for name, role in users],
    })
```

```html
{# users.html #}
{% load tentags %}

{% for data_block in data_blocks %}
    {# Same style template — different data each iteration #}
    {% tentags_inline preamble style_block data_block %}
{% endfor %}
```

---

### All tags in a single `{% tt %}`

```html
{% load tentags %}

{% tt %}
2, 6, 1, "#e2e8f0", "solid", 0, 50,
style(
    <left></left>, <center></center>, <center></center>,
    <center></center>, <center></center>, <right></right>
),
data(
    <b>Bold</b>,
    <i>Italic</i>,
    <u>Underline</u>,
    <s>Strikethrough</s>,
    <url=https://example.com><b>Link</b></url>,
    <color=green><b>+500</b></color>;
    <fs=14><left>{{ user_name }}</left></fs>,
    <bg=#f0f9ff><center>{{ user_role }}</center></bg>,
    <u><center>{{ join_date }}</center></u>,
    <s><right>{{ old_price }}</right></s>,
    <url={{ profile_url }}><color=blue><center>Profile</center></color></url>,
    <bg=#dcfce7><color=#166534><b><right>{{ balance }}</right></b></color></bg>
)
{% endtt %}
```

---

## 5. Flask — Jinja2

### Setup

```python
from flask import Flask, render_template
from tentags.contrib.flask import init_app

app = Flask(__name__)
init_app(app)  # registers {% tt %}, {% tentags %} and {{ tentags(...) }}
```

---

### `{% tt %}` with Jinja2 variables and loops

```python
@app.route('/products')
def products():
    return render_template('products.html', items=[
        {'name': 'Laptop Pro',     'price': '$1,200', 'stock': 45},
        {'name': 'Wireless Mouse', 'price': '$29',    'stock': 200},
        {'name': 'USB-C Hub',      'price': '$49',    'stock': 0},
    ])
```

```html
{# templates/products.html #}

{% tt %}
{{ items|length + 1 }}, 3, 1, "#e2e8f0", "solid", 0, 40,
style(
    <bg=#0f172a><color=white><b><left>Product</left></b></color></bg>,
    <bg=#0f172a><color=white><b><center>Price</center></b></color></bg>,
    <bg=#0f172a><color=white><b><center>Stock</center></b></color></bg>
),
data(
    , , ;
    {% for p in items %}
    <left>{{ p.name }}</left>,
    <center>{{ p.price }}</center>,
    {% if p.stock == 0 %}
        <bg=#fee2e2><color=#991b1b><center>Out of Stock</center></color></bg>
    {% elif p.stock < 50 %}
        <bg=#fef9c3><color=#92400e><center>{{ p.stock }} pcs</center></color></bg>
    {% else %}
        <bg=#dcfce7><color=#166534><center>{{ p.stock }} pcs</center></color></bg>
    {% endif %}
    {% if not loop.last %};{% endif %}
    {% endfor %}
)
{% endtt %}
```

---

### `{{ tentags(...) }}` — global function in template

```python
@app.route('/user/<username>')
def user_profile(username):
    return render_template('profile.html',
        preamble    = '1, 2, 1, "#38bdf8", "solid", 0, 50',
        style_block = 'style(<b><left></left></b>, <right></right>)',
        data_block  = f'data(User: {username}, Role: Admin)'
    )
```

```html
{# templates/profile.html #}

{# Decoupled: 3 arguments from backend #}
{{ tentags(preamble, style_block, data_block) }}

{# Or inline in the template #}
{{ tentags('1,1,1,"black","solid",0,40, data(Welcome, ' ~ username ~ ')') }}
```

---

### Pricing table with links and strikethrough

```python
@app.route('/pricing')
def pricing():
    return render_template('pricing.html', plans=[
        {'name': 'Starter',    'old': '$29',  'price': '$19',  'url': '/buy/starter'},
        {'name': 'Pro',        'old': '$79',  'price': '$49',  'url': '/buy/pro'},
        {'name': 'Enterprise', 'old': None,   'price': '$199', 'url': '/buy/enterprise'},
    ])
```

```html
{# templates/pricing.html #}

{% tt %}
{{ plans|length }}, 2, 1, "#e2e8f0", "solid", 0, 55,
data(
    {% for p in plans %}
    <url={{ p.url }}><b><left>{{ p.name }}</left></b></url>,
    <center>
        {% if p.old %}<s>{{ p.old }}</s>  {% endif %}<b>{{ p.price }}</b>
    </center>
    {% if not loop.last %};{% endif %}
    {% endfor %}
)
{% endtt %}
```

---

## 6. FastAPI — Jinja2

### Setup

```python
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from tentags.contrib.fastapi import register_templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")
register_templates(templates)  # registers tags and functions
```

---

### `{% tt %}` in FastAPI

```python
@app.get('/dashboard')
async def dashboard(request: Request):
    return templates.TemplateResponse('dashboard.html', {
        'request': request,
        'kpi': [
            {'metric': 'Revenue',    'value': '$1,200,000', 'change': '+12%',  'up': True},
            {'metric': 'Users',      'value': '45,230',     'change': '+8%',   'up': True},
            {'metric': 'Conversion', 'value': '3.4%',       'change': '-0.2%', 'up': False},
        ]
    })
```

```html
{# templates/dashboard.html #}

{% tt %}
{{ kpi|length + 1 }}, 3, 1, "#e2e8f0", "solid", 0, 50,
style(
    <bg=#0f172a><color=white><b><left></left></b></color></bg>,
    <bg=#0f172a><color=white><b><center></center></b></color></bg>,
    <bg=#0f172a><color=white><b><right></right></b></color></bg>
),
data(
    Metric, Value, Change;
    {% for row in kpi %}
    <left>{{ row.metric }}</left>,
    <b><center>{{ row.value }}</center></b>,
    {% if row.up %}
        <bg=#dcfce7><color=#166534><b><right>{{ row.change }}</right></b></color></bg>
    {% else %}
        <bg=#fee2e2><color=#991b1b><b><right>{{ row.change }}</right></b></color></bg>
    {% endif %}
    {% if not loop.last %};{% endif %}
    {% endfor %}
)
{% endtt %}
```

---

### Invoice via decoupled API

```python
@app.get('/invoice/{invoice_id}')
async def invoice(request: Request, invoice_id: int):
    items = [
        ('Backend Development', 40, '$150/hr', '$6,000'),
        ('UI/UX Design',        20, '$100/hr', '$2,000'),
        ('QA Testing',          15, '$80/hr',  '$1,200'),
    ]
    rows = '; '.join(
        f'<left>{n}</left>, <center>{q}</center>, <center>{p}</center>, <b><right>{t}</right></b>'
        for n, q, p, t in items
    )
    return templates.TemplateResponse('invoice.html', {
        'request':     request,
        'preamble':    f'{len(items) + 2}, 4, 1, "#e2e8f0", "solid", 0, 42',
        'style_block': 'style(<fs=16><b><cm>Invoice, , , </cm></b></fs>; <bg=#3b82f6><color=white><b></b></color></bg>, <bg=#3b82f6><color=white><b><center></center></b></color></bg>, <bg=#3b82f6><color=white><b><center></center></b></color></bg>, <bg=#3b82f6><color=white><b><right></right></b></color></bg>)',
        'data_block':  f'data(Invoice #{invoice_id}, , , ; Description, Qty, Rate, Total; {rows})',
    })
```

```html
{# templates/invoice.html #}
{{ tentags(preamble, style_block, data_block) }}
```

---

## 7. Decoupled API: preamble + style + data

### The Principle

```
preamble → table dimensions, border, cell height
style()  → cell formatting (style tags)
data()   → actual cell content (text, numbers, links)
```

**Key advantage:** `style()` becomes a **reusable template** — define it once, apply with any data.

### One template — three months

```python
import tentags

preamble = '3, 3, 1, "#cbd5e1", "solid", 0, 45'
style = '''style(
    <bg=#0f172a><color=white><b><cm>Report, , </cm></b></color></bg>;
    <bg=#f8fafc><b><left></left></b></bg>,
    <bg=#f8fafc><b><center></center></b></bg>,
    <bg=#f8fafc><b><right></right></b></bg>
)'''

html_jan = tentags.render(preamble, style, 'data(January, , ; Sales, 1200, "$36,000")')
html_feb = tentags.render(preamble, style, 'data(February, , ; Sales, 1450, "$43,500")')
html_mar = tentags.render(preamble, style, 'data(March, , ; Sales, 1800, "$54,000")')
```

---

### URL in decoupled mode

`<url>` is the one tag recommended in `data()` rather than `style()`,
because each row has a different link while the visual formatting stays the same:

```python
# style stays generic — no URL baked in
preamble = '1, 2, 1, "#e2e8f0", "solid", 0, 40'
style    = 'style(<b><left></left></b>, <right></right>)'

# URL lives in data() — unique per row
links = [
    'data(<url=https://github.com>GitHub</url>, Repository)',
    'data(<url=https://docs.example.com>Documentation</url>, API Reference)',
    'data(<url=mailto:support@example.com>Support</url>, Send an email)',
]
for data in links:
    html = tentags.render(preamble, style, data)
```

```html
{# Django #}
{% load tentags %}
{% for item in items %}
    {% tentags_inline preamble style_template item.data_block %}
{% endfor %}

{# Flask / FastAPI (Jinja2) #}
{% for item in items %}
    {{ tentags(preamble, style_template, item.data_block) }}
{% endfor %}
```

---

### data() overrides style()

```python
style = 'style(<color=gray></color>)'       # gray by default
data  = 'data(<color=red>CRITICAL</color>)' # data wins

html = tentags.render(preamble, style, data)
# → text will be red
```

---

## 8. Real-World Examples

### Financial Dashboard (all formats)

```python
import tentags

preamble = '5, 4, 1, "#e2e8f0", "solid", 0, 45'
style = '''style(
    <fs=18><bg=#1e293b><color=white><b><cm>Q3 Financial Dashboard, , , </cm></b></color></bg></fs>;
    <bg=#f1f5f9><b><left>Department</left></b></bg>,
    <bg=#f1f5f9><b><center>Revenue</center></b></bg>,
    <bg=#f1f5f9><b><center>Expenses</center></b></bg>,
    <bg=#f1f5f9><b><center>Net Profit</center></b></bg>
)'''
data = '''data(
    , , , ;
    <left>Engineering</left>, <right>"$240,000"</right>, <right>"$180,000"</right>,
        <bg=#dcfce7><color=#166534><b><right>"+$60,000"</right></b></color></bg>;
    <left>Sales & Marketing</left>, <right>"$310,000"</right>, <right>"$210,000"</right>,
        <bg=#dcfce7><color=#166534><b><right>"+$100,000"</right></b></color></bg>;
    <left>Operations</left>, <right>"$120,000"</right>, <right>"$140,000"</right>,
        <bg=#fee2e2><color=#991b1b><b><right>"-$20,000"</right></b></color></bg>
)'''

model = tentags.compile(preamble, style, data)
html  = tentags.render_html(model)
tentags.render_xlsx(model, 'dashboard.xlsx')
tentags.render_pdf(model,  'dashboard.pdf')
```

---

### Link list with formatting

```python
import tentags

preamble = '4, 3, 1, "#e2e8f0", "solid", 0, 45'
style    = 'style(<b><left></left></b>, <center></center>, <right></right>)'

entries = [
    ('<url=https://github.com/tentags>GitHub Repository</url>', 'Open Source', '<color=green>Active</color>'),
    ('<url=https://pypi.org/project/tentags>PyPI Package</url>', 'v2.0.0',     '<u>Stable</u>'),
    ('<url=https://tentags.readthedocs.io>Documentation</url>',  'Read the Docs', '<color=blue>Online</color>'),
]
rows = '; '.join(f'{link}, {badge}, {status}' for link, badge, status in entries)
html = tentags.render(preamble, style, f'data({rows})')
```

---

### Invoice (XLSX + PDF)

```python
import tentags

items = [
    ('Backend API Development', '40 hrs', '$150/hr', '$6,000'),
    ('UI/UX Design',            '20 hrs', '$100/hr', '$2,000'),
    ('QA Testing',              '15 hrs', '$80/hr',  '$1,200'),
    ('DevOps Setup',            '10 hrs', '$120/hr', '$1,200'),
]

rows_str = '; '.join(
    f'<left>{name}</left>, <center>{qty}</center>, <center>{rate}</center>, <b><right>{total}</right></b>'
    for name, qty, rate, total in items
)

preamble = f'{len(items) + 3}, 4, 1, "#e2e8f0", "solid", 0, 42'
style = '''style(
    <fs=16><bg=white><b><left><cm>INVOICE #1024, , , </cm></left></b></bg></fs>;
    <left><cm>Date: 2026-07-15, , , </cm></left>;
    <bg=#3b82f6><color=white><b>Description</b></color></bg>,
        <bg=#3b82f6><color=white><b><center>Qty</center></b></color></bg>,
        <bg=#3b82f6><color=white><b><center>Rate</center></b></color></bg>,
        <bg=#3b82f6><color=white><b><right>Total</right></b></color></bg>
)'''
data = f'data(, , , ; , , , ; {rows_str})'

model = tentags.compile(preamble, style, data)
tentags.render_xlsx(model, 'invoice.xlsx')
tentags.render_pdf(model,  'invoice.pdf')
```

---

### Dynamic table from database (FastAPI + SQLAlchemy)

```python
@app.get('/sales-report')
async def sales_report(request: Request, db: Session = Depends(get_db)):
    rows_db = db.query(Sale).filter(Sale.month == 'July').all()

    header = (
        '<bg=#1e293b><color=white><b>Manager</b></color></bg>, '
        '<bg=#1e293b><color=white><b><center>Sales</center></b></color></bg>, '
        '<bg=#1e293b><color=white><b><right>Revenue</right></b></color></bg>'
    )

    data_rows = []
    for row in rows_db:
        bg    = '#dcfce7' if row.total > 50000 else '#fef9c3'
        color = '#166534' if row.total > 50000 else '#92400e'
        data_rows.append(
            f'<left>{row.manager_name}</left>, '
            f'<center>{row.count}</center>, '
            f'<bg={bg}><color={color}><b><right>${row.total:,.0f}</right></b></color></bg>'
        )

    data       = 'data(' + header + '; ' + '; '.join(data_rows) + ')'
    preamble   = f'{len(rows_db) + 1}, 3, 1, "#e2e8f0", "solid", 0, 45'
    html_table = tentags.render(preamble, data=data)

    return templates.TemplateResponse('sales.html', {
        'request': request,
        'table': html_table
    })
```

```html
{# sales.html #}
{{ table | safe }}
```

---

## Quick Reference

### All Tags

| Category | Tag | Description |
|---|---|---|
| Typography | `<b>`, `<i>`, `<u>`, `<s>` | Bold, italic, underline, strikethrough |
| Font size | `<fs=N>` | Font size in px |
| Color | `<color=...>`, `<bg=...>` | Text color / cell background |
| Alignment | `<left>`, `<center>`, `<right>` | Horizontal text alignment |
| Merging | `<cm>`, `<rm>` | Colspan / Rowspan |
| Link | `<url=https://...>` | Clickable hyperlink |
| Data | `csv("path")` | Inline CSV import |

### Where to write tags

| Tag | Recommended in |
|---|---|
| `<b>`, `<i>`, `<u>`, `<s>`, `<color>`, `<bg>`, `<fs>`, `<left>`, `<center>`, `<right>`, `<cm>`, `<rm>` | `style()` — formatting template |
| `<url=...>` | `data()` — unique per row |
| `{{ variable }}` (Django / Jinja2) | `data()` — dynamic content from backend |

### Block order — always

```
preamble  →  style()  →  data()
```

### Framework comparison

| Feature | Django | Flask (Jinja2) | FastAPI (Jinja2) |
|---|---|---|---|
| Block tag | `{% tt %}...{% endtt %}` | `{% tt %}...{% endtt %}` | `{% tt %}...{% endtt %}` |
| Setup | `'tentags'` in `INSTALLED_APPS` | `init_app(app)` | `register_templates(templates)` |
| Load tags | `{% load tentags %}` | automatic | automatic |
| Inline render | `{% tentags_inline formula %}` | `{{ tentags(formula) }}` | `{{ tentags(formula) }}` |
| Decoupled inline | `{% tentags_inline p s d %}` | `{{ tentags(p, s, d) }}` | `{{ tentags(p, s, d) }}` |
| Template variables | `{{ var }}` | `{{ var }}` | `{{ var }}` |
