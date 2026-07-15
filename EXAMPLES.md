# TenTags — Примеры и справочник

Полное руководство по использованию TenTags: все теги, шаблонные движки и передача аргументов через бэкенд.

---

## Содержание

1. [Структура формулы](#1-структура-формулы)
2. [Справочник тегов](#2-справочник-тегов)
3. [Python API](#3-python-api)
4. [Django — Template Tags](#4-django--template-tags)
5. [Flask — Jinja2](#5-flask--jinja2)
6. [FastAPI — Jinja2](#6-fastapi--jinja2)
7. [Decoupled API: preamble + style + data](#7-decoupled-api-preamble--style--data)
8. [Реальные примеры](#8-реальные-примеры)

---

## 1. Структура формулы

Каждая TenTags формула состоит из трёх частей:

```
ROWS, COLS, BORDER_WIDTH, "BORDER_COLOR", "BORDER_STYLE", STRETCH, CELL_HEIGHT, data(...)
```

| Параметр | Тип | Описание |
|---|---|---|
| `ROWS` | int | Количество строк |
| `COLS` | int | Количество столбцов |
| `BORDER_WIDTH` | int | Толщина рамки (px) |
| `BORDER_COLOR` | string | Цвет рамки (`"black"`, `"#ccc"`) |
| `BORDER_STYLE` | string | Стиль рамки (`"solid"`, `"solid-1"`, `"none"`) |
| `STRETCH` | int | `0` = фиксированная высота, `1` = авторастяжение |
| `CELL_HEIGHT` | int | Высота ячейки в px |
| `data(...)` | block | Содержимое ячеек |

**Разделители в `data()`:**
- `,` — новая ячейка (следующий столбец)
- `;` — новая строка

```python
import tentags

html = tentags.render('2, 3, 1, "black", "solid", 0, 40, data(A, B, C; D, E, F)')
```

---

## 2. Справочник тегов

Теги применяются **внутри ячеек** в блоках `style()` или `data()`.
Все теги должны быть **закрыты**: `<тег>содержимое</тег>`.

### Типографика

| Тег | Описание | CSS эффект |
|---|---|---|
| `<b>текст</b>` | **Жирный** | `font-weight: bold` |
| `<i>текст</i>` | *Курсив* | `font-style: italic` |
| `<u>текст</u>` | Подчёркнутый | `text-decoration: underline` |
| `<s>текст</s>` | Зачёркнутый | `text-decoration: line-through` |
| `<fs=18>текст</fs>` | Размер шрифта 18px | `font-size: 18px` |

```python
# Жирный + курсив
tentags.render('1,1,1,"black","solid",0,40, data(<b><i>Важно!</i></b>)')

# Подчёркнутый
tentags.render('1,1,1,"black","solid",0,40, data(<u>Важное условие</u>)')

# Зачёркнутая цена + новая
tentags.render('1,2,1,"black","solid",0,40, data(<s>"$199"</s>, "$99"))')

# Крупный шрифт
tentags.render('1,1,1,"black","solid",0,60, data(<fs=24><b>ИТОГО</b></fs>)')

# Комбинирование
tentags.render('1,1,1,"black","solid",0,40, data(<b><u><s>Всё сразу</s></u></b>)')
```

---

### Цвет и фон

| Тег | Описание |
|---|---|
| `<color=red>текст</color>` | Цвет текста (имя или hex) |
| `<bg=#f0f0f0>текст</bg>` | Цвет фона ячейки |

```python
# Именованные цвета
tentags.render('1,3,1,"black","solid",0,40, data(<color=red>Убыток</color>, <color=green>Прибыль</color>, <color=blue>Нейтральный</color>)')

# Hex-цвета
tentags.render('1,2,1,"#ccc","solid",0,40, data(<bg=#1e293b><color=white>Заголовок</color></bg>, <bg=#f8fafc>Данные</bg>)')

# Цветной бейдж
tentags.render('1,1,1,"black","solid",0,50, data(<bg=#dcfce7><color=#166534><b>+$60,000</b></color></bg>)')
```

---

### Выравнивание

| Тег | Описание |
|---|---|
| `<left>текст</left>` | По левому краю |
| `<center>текст</center>` | По центру |
| `<right>текст</right>` | По правому краю |

```python
tentags.render('1,3,1,"black","solid",0,40, data(<left>Левый</left>, <center>Центр</center>, <right>Правый</right>)')
```

---

### Объединение ячеек

| Тег | Описание |
|---|---|
| `<cm>текст, , </cm>` | Colspan: объединить N столбцов (по числу запятых) |
| `<rm>текст</rm>` | Rowspan: объединить строки вертикально |

```python
# Объединить 3 столбца
tentags.render('2,3,1,"black","solid",0,40, data(<cm>Заголовок на 3 колонки, , </cm>; A, B, C)')

# Объединить 2 строки
tentags.render('2,2,1,"black","solid",0,40, data(<rm>Объединённая</rm>, Правая 1; <rm> </rm>, Правая 2)')
```

---

### Ссылки

| Тег | Описание |
|---|---|
| `<url=https://...>текст</url>` | Кликабельная ссылка |

> **Рекомендация:** `<url>` лучше писать в `data()`, а не в `style()`.  
> Это позволяет переиспользовать шаблон стилей с разными ссылками.

```python
# Простая ссылка
tentags.render('1,1,1,"black","solid",0,40, data(<url=https://example.com>Перейти</url>)')

# Жирная ссылка
tentags.render('1,1,1,"black","solid",0,40, data(<url=https://example.com><b>Скачать PDF</b></url>)')

# Decoupled: URL в data(), форматирование в style()
tentags.render(
    '1,1,1,"black","solid",0,40',
    'style(<b><left></left></b>)',
    'data(<url=https://example.com>Посетить сайт</url>)'
)
```

---

### Загрузка CSV

```python
# Из локального файла
tentags.render('5,3,1,"black","solid",0,40, data(csv("data/sales.csv")))')

# Из URL
tentags.render('5,3,1,"black","solid",0,40, data(csv("https://example.com/data.csv")))')
```

---

## 3. Python API

### Простой рендеринг

```python
import tentags

html = tentags.render('2,2,1,"black","solid",0,40, data(A, B; C, D)')

# С переменными через context
context = {'name': 'Zhandos', 'role': 'Admin'}
html = tentags.render('1,2,1,"black","solid",0,40, data(name, role)', context)
```

### Compile → Render (один source, несколько форматов)

```python
import tentags

model = tentags.parse('2,2,1,"black","solid",0,40, data(A, B; C, D)')

html = tentags.render_html(model)           # HTML строка
tentags.render_xlsx(model, 'out.xlsx')      # Excel файл
tentags.render_pdf(model,  'out.pdf')       # PDF файл
```

### Decoupled API

```python
import tentags

preamble = '2, 3, 1, "#ccc", "solid", 0, 40'
style    = 'style(<bg=#1e293b><color=white><b><cm>Заголовок, , </cm></b></color></bg>; <left></left>, <center></center>, <right></right>)'
data     = 'data(Отдел, Сотрудников, Бюджет; Разработка, 12, "$500,000")'

html  = tentags.render(preamble, style, data)
html2 = tentags.render(preamble, style, 'data(Маркетинг, 8, "$200,000")')  # другие данные, тот же style
```

---

## 4. Django — Template Tags

### Установка

```python
# settings.py
INSTALLED_APPS = [
    ...
    'tentags',
]
```

---

### `{% tt %}` — формула прямо в шаблоне

```python
# views.py
def report_view(request):
    return render(request, 'report.html', {
        'dept':     'Разработка',
        'revenue':  '$240,000',
        'expenses': '$180,000',
        'profit':   '+$60,000',
    })
```

```html
{% load tentags %}

{% tt %}
4, 4, 1, "#cbd5e1", "solid", 0, 45,
style(
    <fs=18><bg=#1e293b><color=white><b><cm>Финансовый отчёт, , , </cm></b></color></bg></fs>;
    <bg=#f1f5f9><b><left>Отдел</left></b></bg>,
    <bg=#f1f5f9><b><center>Выручка</center></b></bg>,
    <bg=#f1f5f9><b><center>Расходы</center></b></bg>,
    <bg=#f1f5f9><b><center>Прибыль</center></b></bg>
),
data(
    , , , ;
    {{ dept }}, {{ revenue }}, {{ expenses }},
    <bg=#dcfce7><color=#166534><b><right>{{ profit }}</right></b></color></bg>
)
{% endtt %}
```

---

### `{% tentags_inline %}` — формула из бэкенда

```python
# views.py
def badge_view(request):
    user_name = "Zhandos Mambetali"
    formula = (
        f"1, 2, 1, '#38bdf8', 'solid', 0, 50, "
        f"data(<b>User:</b> {user_name}, Role: Admin)"
    )
    return render(request, 'badge.html', {'formula': formula})
```

```html
{% load tentags %}
{% tentags_inline formula %}
```

---

### `{% tentags_inline %}` — decoupled режим (3 аргумента)

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
{% load tentags %}

{% for data_block in data_blocks %}
    {% tentags_inline preamble style_block data_block %}
{% endfor %}
```

---

### Все теги в одном `{% tt %}`

```html
{% load tentags %}

{% tt %}
2, 6, 1, "#e2e8f0", "solid", 0, 50,
style(<left></left>, <center></center>, <center></center>, <center></center>, <center></center>, <right></right>),
data(
    <b>Жирный</b>,
    <i>Курсив</i>,
    <u>Подчёркнутый</u>,
    <s>Зачёркнутый</s>,
    <url=https://example.com><b>Ссылка</b></url>,
    <color=green><b>+500</b></color>;
    <fs=14><left>{{ user_name }}</left></fs>,
    <bg=#f0f9ff><center>{{ user_role }}</center></bg>,
    <u><center>{{ join_date }}</center></u>,
    <s><right>{{ old_price }}</right></s>,
    <url={{ profile_url }}><color=blue><center>Профиль</center></color></url>,
    <bg=#dcfce7><color=#166534><b><right>{{ balance }}</right></b></color></bg>
)
{% endtt %}
```

---

## 5. Flask — Jinja2

### Подключение

```python
from flask import Flask, render_template
from tentags.contrib.flask import init_app

app = Flask(__name__)
init_app(app)  # регистрирует {% tt %}, {% tentags %} и {{ tentags(...) }}
```

---

### `{% tt %}` с Jinja2 переменными и циклами

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
{% tt %}
{{ items|length + 1 }}, 3, 1, "#e2e8f0", "solid", 0, 40,
style(
    <bg=#0f172a><color=white><b><left>Товар</left></b></color></bg>,
    <bg=#0f172a><color=white><b><center>Цена</center></b></color></bg>,
    <bg=#0f172a><color=white><b><center>Остаток</center></b></color></bg>
),
data(
    , , ;
    {% for p in items %}
    <left>{{ p.name }}</left>,
    <center>{{ p.price }}</center>,
    {% if p.stock == 0 %}
        <bg=#fee2e2><color=#991b1b><center>Нет в наличии</center></color></bg>
    {% elif p.stock < 50 %}
        <bg=#fef9c3><color=#92400e><center>{{ p.stock }} шт.</center></color></bg>
    {% else %}
        <bg=#dcfce7><color=#166534><center>{{ p.stock }} шт.</center></color></bg>
    {% endif %}
    {% if not loop.last %};{% endif %}
    {% endfor %}
)
{% endtt %}
```

---

### `{{ tentags(...) }}` — функция из шаблона

```python
@app.route('/user/<username>')
def user_profile(username):
    return render_template('profile.html',
        preamble    = '1, 2, 1, "#38bdf8", "solid", 0, 50',
        style_block = 'style(<b><left></left></b>, <right></right>)',
        data_block  = f'data(Пользователь: {username}, Роль: Admin)'
    )
```

```html
{# Decoupled: 3 аргумента #}
{{ tentags(preamble, style_block, data_block) }}

{# Или одной строкой прямо в шаблоне #}
{{ tentags('1,1,1,"black","solid",0,40, data(Добро пожаловать, ' ~ username ~ ')') }}
```

---

### Прайс-лист со ссылками и зачёркнутыми ценами

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

### Подключение

```python
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from tentags.contrib.fastapi import register_templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")
register_templates(templates)  # регистрирует теги и функции
```

---

### `{% tt %}` в FastAPI

```python
@app.get('/dashboard')
async def dashboard(request: Request):
    return templates.TemplateResponse('dashboard.html', {
        'request': request,
        'kpi': [
            {'metric': 'Выручка',     'value': '$1,200,000', 'change': '+12%',  'up': True},
            {'metric': 'Пользователи', 'value': '45,230',    'change': '+8%',   'up': True},
            {'metric': 'Конверсия',    'value': '3.4%',      'change': '-0.2%', 'up': False},
        ]
    })
```

```html
{% tt %}
{{ kpi|length + 1 }}, 3, 1, "#e2e8f0", "solid", 0, 50,
style(
    <bg=#0f172a><color=white><b><left></left></b></color></bg>,
    <bg=#0f172a><color=white><b><center></center></b></color></bg>,
    <bg=#0f172a><color=white><b><right></right></b></color></bg>
),
data(
    Метрика, Значение, Изменение;
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

### Счёт-фактура через decoupled API

```python
@app.get('/invoice/{invoice_id}')
async def invoice(request: Request, invoice_id: int):
    items = [
        ('Разработка backend',  40, '$150/ч', '$6,000'),
        ('UI/UX дизайн',        20, '$100/ч', '$2,000'),
        ('QA тестирование',     15, '$80/ч',  '$1,200'),
    ]
    rows = '; '.join(
        f'<left>{n}</left>, <center>{q}</center>, <center>{p}</center>, <b><right>{t}</right></b>'
        for n, q, p, t in items
    )
    return templates.TemplateResponse('invoice.html', {
        'request':     request,
        'preamble':    f'{len(items) + 2}, 4, 1, "#e2e8f0", "solid", 0, 42',
        'style_block': 'style(<fs=16><b><cm>Invoice, , , </cm></b></fs>; <bg=#3b82f6><color=white><b></b></color></bg>, <bg=#3b82f6><color=white><b><center></center></b></color></bg>, <bg=#3b82f6><color=white><b><center></center></b></color></bg>, <bg=#3b82f6><color=white><b><right></right></b></color></bg>)',
        'data_block':  f'data(Invoice #{invoice_id}, , , ; Описание, Кол-во, Цена, Сумма; {rows})',
    })
```

```html
{{ tentags(preamble, style_block, data_block) }}
```

---

## 7. Decoupled API: preamble + style + data

### Принцип

```
preamble → размеры таблицы, рамка, высота
style()  → форматирование ячеек (теги стилей)
data()   → содержимое ячеек (текст, числа, ссылки)
```

`style()` — **переиспользуемый шаблон**: определяете один раз, применяете многократно.

### Один шаблон — три месяца

```python
import tentags

preamble = '3, 3, 1, "#cbd5e1", "solid", 0, 45'
style = '''style(
    <bg=#0f172a><color=white><b><cm>Отчёт, , </cm></b></color></bg>;
    <bg=#f8fafc><b><left></left></b></bg>, <bg=#f8fafc><b><center></center></b></bg>, <bg=#f8fafc><b><right></right></b></bg>
)'''

html_jan = tentags.render(preamble, style, 'data(Январь, , ; Продажи, 1200, "$36,000")')
html_feb = tentags.render(preamble, style, 'data(Февраль, , ; Продажи, 1450, "$43,500")')
html_mar = tentags.render(preamble, style, 'data(Март, , ; Продажи, 1800, "$54,000")')
```

---

### URL в decoupled-режиме

```python
# style — неизменный шаблон оформления
preamble = '1, 2, 1, "#e2e8f0", "solid", 0, 40'
style    = 'style(<b><left></left></b>, <right></right>)'

# URL — в data(), уникален для каждой строки
links = [
    'data(<url=https://github.com>GitHub</url>, Репозиторий)',
    'data(<url=https://docs.example.com>Документация</url>, API справочник)',
    'data(<url=mailto:support@example.com>Поддержка</url>, Написать письмо)',
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

### data() переопределяет style()

```python
style = 'style(<color=gray></color>)'   # серый по умолчанию
data  = 'data(<color=red>ОШИБКА</color>)'  # data перекрывает

html = tentags.render(preamble, style, data)
# → цвет будет красным
```

---

## 8. Реальные примеры

### Финансовый дашборд (все форматы)

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

### Список ссылок с оформлением

```python
preamble = '4, 3, 1, "#e2e8f0", "solid", 0, 45'
style    = 'style(<b><left></left></b>, <center></center>, <right></right>)'
entries  = [
    ('<url=https://github.com/tentags>GitHub Репозиторий</url>', 'Open Source', '<color=green>Активный</color>'),
    ('<url=https://pypi.org/project/tentags>PyPI Пакет</url>', 'v2.0.0', '<u>Стабильный</u>'),
    ('<url=https://tentags.readthedocs.io>Документация</url>', 'Read the Docs', '<color=blue>Онлайн</color>'),
]
rows = '; '.join(f'{link}, {badge}, {status}' for link, badge, status in entries)
html = tentags.render(preamble, style, f'data({rows})')
```

---

### Динамическая таблица из базы данных (FastAPI)

```python
@app.get('/sales')
async def sales_report(request: Request, db: Session = Depends(get_db)):
    rows_db = db.query(Sale).filter(Sale.month == 'July').all()
    header  = (
        '<bg=#1e293b><color=white><b>Менеджер</b></color></bg>, '
        '<bg=#1e293b><color=white><b><center>Продаж</center></b></color></bg>, '
        '<bg=#1e293b><color=white><b><right>Сумма</right></b></color></bg>'
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
    data     = 'data(' + header + '; ' + '; '.join(data_rows) + ')'
    preamble = f'{len(rows_db) + 1}, 3, 1, "#e2e8f0", "solid", 0, 45'
    html_table = tentags.render(preamble, data=data)
    return templates.TemplateResponse('sales.html', {'request': request, 'table': html_table})
```

```html
{# sales.html #}
{{ table | safe }}
```

---

## Быстрый справочник

### Все теги

| Категория | Тег | Описание |
|---|---|---|
| Типографика | `<b>`, `<i>`, `<u>`, `<s>` | Жирный, курсив, подчёркнутый, зачёркнутый |
| Размер | `<fs=N>` | Размер шрифта в px |
| Цвет | `<color=...>`, `<bg=...>` | Цвет текста / фон ячейки |
| Выравнивание | `<left>`, `<center>`, `<right>` | Горизонтальное выравнивание |
| Объединение | `<cm>`, `<rm>` | Colspan / Rowspan |
| Ссылка | `<url=https://...>` | Кликабельная ссылка |
| Данные | `csv("path")` | Вставка CSV данных |

### Правило: где писать теги

| Тег | Рекомендуется в |
|---|---|
| `<b>`, `<i>`, `<u>`, `<s>`, `<color>`, `<bg>`, `<fs>`, `<left>`, `<center>`, `<right>`, `<cm>`, `<rm>` | `style()` — описывает оформление |
| `<url=...>` | `data()` — уникален для каждой строки |
| `{{ переменная }}` | `data()` — содержимое из бэкенда |

### Порядок блоков всегда

```
preamble  →  style()  →  data()
```
