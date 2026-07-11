# TenTags 🏷️

<p align="center">
  <a href="https://pycells.com">
    <img src="https://pycells.com/assets/img/tentags_logo.png" width="400" alt="TenTags logo">
  </a>
</p>

[![PyPI version](https://img.shields.io/pypi/v/tentags.svg)](https://pypi.org/project/tentags/)
[![Python versions](https://img.shields.io/pypi/pyversions/tentags.svg)](https://pypi.org/project/tentags/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

**TenTags** is a declarative template language and **Intermediate Representation (IR)** for automated **HTML**, **Excel (`.xlsx`)**, and **PDF** table and document generation.

### 💡 Why TenTags? (A Language for Programs & AI, Not Manual Editing)

While general markup formats are designed for *humans* to manually write text, **TenTags** is designed specifically as a **Template DSL for programs, server engines, and AI agents**.

Whether you are building backend report pipelines, ERP/CRM accounting modules, invoice generators, or LLM-driven document agents, generating clean TenTags strings via loops and f-strings is orders of magnitude simpler and safer than emitting verbose HTML strings with inline `style=""` or hundreds of lines of `openpyxl` / `reportlab` API calls:

```python
# Programmatically generate high-fidelity reports with dynamic loops and f-strings:
formula = f'''
5,4,1,"#ccc","solid",0,40, data(
    <bg=#1e293b><color=white><b><cm>{report_title}, , , </cm></b></color></bg>;
    {generated_rows_from_db}
)'''
```

### ⚙️ Intermediate Representation (IR) Compiler Architecture

At its core, **TenTags** decouples markup tokenization from rendering by compiling formulas into a unified `TableModel` (AST/IR). Because `TableModel` serves as a clean **Intermediate Representation**, you can compile exact multi-cell grid merges (`<cm>`, `<rm>`), typography (`<fs>`, `<b>`, `<i>`), alignments, and pattern fills (`<bg>`, `<color>`) across all three major corporate backends:

```text
Text Formula
     ↓
   Lexer
     ↓
  Tokens
     ↓
  Parser
     ↓
 TableModel (Intermediate Representation / IR)
   ↙    ↓    ↘
HTML  Excel  PDF (.pdf)   [Future: DOCX, Canvas, Flutter...]
```

- 🎯 **Target Audience**: Backend developers (FastAPI, Django, Flask), ERP/CRM financial engines, automated invoice/receipt generators, and AI/LLM agents.
- 🤖 **AI & LLM Native**: LLMs generate exact, compact TenTags formulas reliably without CSS layout bugs or Excel/PDF API hallucinations.
- 🔀 **Declarative Grid Merges**: Effortlessly merge cells rightward across columns (`<cm>`) and downward across rows (`<rm>`).
- 🎨 **Rich Typography & Styling**: Inline control over font size (`<fs>`), bold (`<b>`), italic (`<i>`), alignment (`<left>`, `<center>`, `<right>`), text color (`<color=>`), and cell fills (`<bg=>`).
- 📊 **Triple Backend Rendering**: Directly compile your IR to high-fidelity **HTML** (`render_html`), native **Excel (`.xlsx`)** (`render_xlsx`), or vector **PDF (`.pdf`)** (`render_pdf`).
- ⚡ **Lightweight & Modular Runtime**: Pure Python runtime (`xml.etree.ElementTree`) for DSL tokenization and HTML rendering. Optional Excel export (`openpyxl`) and PDF export (`reportlab`).

---

## ⚡ Quick Code → Result

Write this concise, expressive TenTags formula:

```python
import tentags

formula = '''3,2,1,"#cbd5e1","solid",0,40, data(
    <fs=16><bg=#1e293b><color=white><b><cm><center>Quarter Report, ,</center></cm></b></color></bg></fs>;
    <b>Sales</b>, <right>"$120,000"</right>;
    <b>Marketing</b>, <right>"$80,000"</right>
)'''

# 1. Render directly to high-fidelity HTML string
html_table = tentags.render(formula)

# 2. Compile IR for Excel (.xlsx) and PDF (.pdf) export
model = tentags.parse(formula)

# Export to native Excel (.xlsx)
tentags.render_xlsx(model, "Quarter_Report.xlsx")

# Export to vector PDF (.pdf)
tentags.render_pdf(model, "Quarter_Report.pdf")
```

**↓ Faithful Visual Output across HTML, Excel (`.xlsx`) and PDF (`.pdf`):**

<p align="center">
  <img src="https://pycells.com/assets/img/Quarter_Report.png" alt="TenTags Quarter Report Output" width="600">
</p>

| Quarter Report *(Merged across 2 columns (`<cm>`), 16px Bold White text, Dark Slate `#1e293b` fill)* | — |
| :--- | :---: |
| **Sales** *(Bold)* | $120,000 *(Right aligned)* |
| **Marketing** *(Bold)* | $80,000 *(Right aligned)* |

---

## 🏷️ The 10 Tags in `data(...)`

TenTags derives its name from the **10 core structural and styling tags** supported inside the `data(...)` argument block:

| # | Tag / Syntax | Type | Description | Example |
|---|---|---|---|---|
| 1 | `<fs=...>` | Typography | Sets custom font size (`font-size` in HTML, `size` in Excel `openpyxl`). | `data(<fs=16>Heading</fs>, Text)` |
| 2 | `<b>...</b>` | Typography | Renders cell text in **Bold** font weight (`font-weight: bold`). | `data(<b>Total</b>, 100)` |
| 3 | `<i>...</i>` | Typography | Renders cell text in *Italic* font style (`font-style: italic`). | `data(<i>Pending</i>, Done)` |
| 4 | `<left>` | Alignment | Aligns cell content to the **left** (`text-align: left`). | `data(<left>Left aligned text)` |
| 5 | `<center>` | Alignment | Aligns cell content to the **center** (`text-align: center`). | `data(<center>Centered text)` |
| 6 | `<right>` | Alignment | Aligns cell content to the **right** (`text-align: right`). | `data(<right>Right aligned $5,000)` |
| 7 | `<color=...>` | Text Color | Sets custom HEX or CSS text color (`color: ...` / font color). | `data(<color=#ef4444>Error</color>, OK)` |
| 8 | `<bg=...>` | Background Fill | Sets cell background fill color (`background-color: ...` / PatternFill). | `data(<bg=#f8fafc>Summary</bg>, $500)` |
| 9 | `<cm>...</cm>` | Column Merge | Merges the cell rightward with adjacent columns (`colspan`). | `data(<cm>Merged Title, ,</cm>; A, B)` |
| 10 | `<rm>...</rm>` | Row Merge | Merges the cell downward with rows below it (`rowspan`). | `data(<rm>Date</rm>, Job; , Engineer)` |

> **Note on Tag Transfer & Empty Elements**: Notice how empty elements (such as `, ,` or `, ;`) are used when adjacent cells are absorbed by a `<cm>` horizontal merge or `<rm>` vertical merge. TenTags automatically transfers and preserves all active tags across cell boundaries without requiring explicit `None` placeholders.

---

## 📦 Installation

Install from PyPI via pip:

```bash
pip install tentags
```

For **Excel (`.xlsx`)** export, install the optional `excel` dependency:

```bash
pip install tentags[excel]
# or directly: pip install openpyxl
```

For **PDF (`.pdf`)** export, install the optional `pdf` dependency:

```bash
pip install tentags[pdf]
# or directly: pip install reportlab
```

To install **all optional backends** at once:

```bash
pip install tentags[all]
```

---

## 🎨 Advanced Example: Beautiful Styled Table & Merges

Here is how a single, clean **TenTags** expression generates an enterprise-grade financial dashboard table featuring merged headers (`<cm>`), custom font sizing (`<fs>`), cell background colors (`<bg=>`), text alignment (`<left>`, `<right>`), and custom typography (`<b>`, `<i>`, `<color=>`) across both **HTML** and **Excel (`.xlsx`)**:

```python
import tentags

# Define an advanced 4x4 styled financial performance grid using clean empty elements (, ,) inside merges
formula = '''4,4,1,"#cbd5e1","solid",0,45, data(
    <fs=18><bg=#1e293b><color=white><b><cm>Q3 Financial Performance Dashboard, , , , </cm></b></color></bg></fs>;
    <bg=#f1f5f9><b><left>Department</left></b></bg>, <bg=#f1f5f9><b><center>Revenue</center></b></bg>, <bg=#f1f5f9><b><center>Expenses</center></b></bg>, <bg=#f1f5f9><b><center>Net Profit</center></b></bg>;
    <left>Engineering</left>, <right>"$240,000"</right>, <right>"$180,000"</right>, <bg=#dcfce7><color=#166534><b><right>"+$60,000"</right></b></color></bg>;
    <left>Sales & Marketing</left>, <right>"$310,000"</right>, <right>"$210,000"</right>, <bg=#dcfce7><color=#166534><b><right>"+$100,000"</right></b></color></bg>
)'''

# Compile IR once — render to any backend
model = tentags.parse(formula)

# 1. Export to native Excel (.xlsx) with exact fonts, fills & merge_cells
tentags.render_xlsx(model, "Q3_Financial_Dashboard.xlsx")

# 2. Export to vector PDF (.pdf) via ReportLab
tentags.render_pdf(model, "Q3_Financial_Dashboard.pdf")

# 3. Render to responsive HTML string with inline CSS
html_table = tentags.render_html(model)
print(html_table)
```

### 📋 Visual Structure & Styling Result:

<p align="center">
  <img src="https://pycells.com/assets/img/Q3_Financial_Dashboard.png" alt="Q3 Financial Performance Dashboard Output" width="750">
</p>

---

## 📊 Excel Matrix Example: Row Merges (`<rm>`), Column Merges (`<cm>`) & Colors

To see how **TenTags** shines as a native Excel spreadsheet generator, here is a 5x5 **Enterprise Allocation Matrix** utilizing combined row merges (`<rm>`), multi-column merges (`<cm>`), clean empty elements (` `, `, `), and classic Microsoft Excel color palettes (`#1F4E78`, `#DDEBF7`, `#E2EFDA`, `#FFF2CC`):

```python
import tentags

# Define an Excel matrix with vertical row merges (<rm>) and horizontal column merges (<cm>)
excel_formula = '''5,5,1,"#B0C4DE","solid",0,35, data(
    <fs=16><bg=#1F4E78><color=white><b><cm>2026 Enterprise Budget & Allocation Matrix, , , , </cm></b></color></bg></fs>;
    <bg=#DDEBF7><b><rm><center>Category</center></rm></b></bg>, <bg=#DDEBF7><b><cm><center>Q1 & Q2 Allocation, </center></cm></b></bg>, <bg=#DDEBF7><b><cm><center>Q3 & Q4 Allocation, </center></cm></b></bg>;
    <bg=#DDEBF7><b><rm> </rm></b></bg>, <bg=#F2F2F2><b><center>Hardware</center></b></bg>, <bg=#F2F2F2><b><center>Software</center></b></bg>, <bg=#F2F2F2><b><center>Hardware</center></b></bg>, <bg=#F2F2F2><b><center>Software</center></b></bg>;
    <bg=#FFF2CC><b><left>R&D Division</left></b></bg>, <right>"$150,000"</right>, <right>"$85,000"</right>, <right>"$120,000"</right>, <right>"$95,000"</right>;
    <bg=#E2EFDA><color=#375623><b><left>Total Budget</left></b></color></bg>, <bg=#E2EFDA><color=#375623><b><cm><right>"$235,000", </right></cm></b></color></bg>, <bg=#E2EFDA><color=#375623><b><cm><right>"+$215,000", </right></cm></b></color></bg>
)'''

# Compile IR once — export to all three backends
model = tentags.parse(excel_formula)

# Export to native Excel (.xlsx)
tentags.render_xlsx(model, "Enterprise_Budget_Matrix.xlsx")

# Export to vector PDF (.pdf)
tentags.render_pdf(model, "Enterprise_Budget_Matrix.pdf")
```

### 🗓️ Visual Spreadsheet Grid Structure (`A1:E5`):

<p align="center">
  <img src="https://pycells.com/assets/img/example.png" alt="TenTags Excel Matrix Output" width="750">
</p>


| # | Tag / Syntax | Type | Description | Example |
|---|---|---|---|---|
| 1 | `<fs=...>` | Typography | Sets custom font size (`font-size` in HTML, `size` in Excel `openpyxl`). | `data(<fs=16>Heading</fs>, Text)` |
| 2 | `<b>...</b>` | Typography | Renders cell text in **Bold** font weight (`font-weight: bold`). | `data(<b>Total</b>, 100)` |
| 3 | `<i>...</i>` | Typography | Renders cell text in *Italic* font style (`font-style: italic`). | `data(<i>Pending</i>, Done)` |
| 4 | `<left>` | Alignment | Aligns cell content to the **left** (`text-align: left`). | `data(<left>Left aligned text)` |
| 5 | `<center>` | Alignment | Aligns cell content to the **center** (`text-align: center`). | `data(<center>Centered text)` |
| 6 | `<right>` | Alignment | Aligns cell content to the **right** (`text-align: right`). | `data(<right>Right aligned $5,000)` |
| 7 | `<color=...>` | Text Color | Sets custom HEX or CSS text color (`color: ...` / font color). | `data(<color=#ef4444>Error</color>, OK)` |
| 8 | `<bg=...>` | Background Fill | Sets cell background fill color (`background-color: ...` / PatternFill). | `data(<bg=#f8fafc>Summary</bg>, $500)` |
| 9 | `<cm>...</cm>` | Column Merge | Merges the cell rightward with adjacent columns (`colspan`). | `data(<cm>Merged Title</cm>, None; A, B)` |
| 10 | `<rm>...</rm>` | Row Merge | Merges the cell downward with rows below it (`rowspan`). | `data(<rm>Date</rm>, Job; <cm>, Engineer)` |

> **Note on Tag Transfer**: When merging (`<cm>`, `<rm>`) or expanding ranges across styled cells (`<fs>`, `<b>`, `<i>`, `<color>`, `<bg>`, `<left>`, `<center>`, `<right>`), TenTags automatically transfers and preserves all formatting across cell boundaries in both HTML and Excel outputs.
> 
> **Dynamic Data Expressions**: In addition to the 10 markup tags above, TenTags `data(...)` supports dynamic line numbering (`#`), variable context substitution (`VarName`), CSV URL/file import (`csv(...)`), and cell range expansion (`A1:B3`).

---

## 🛠️ API Reference

### `tentags.render(formula: str, context: dict = None) -> str`
Parses the input DSL formula string and returns a complete `<table>...</table>` HTML string.
- **`formula`**: String in format `'rows, cols, border_width, "border_color", "border_style", margin, row_height, data(...)'`.
- **`context`**: Optional dictionary of variable names and their replacement values (`{'VarName': 'Value'}`).

### `tentags.parse(formula: str, context: dict = None) -> TableModel`
Parses the formula into a structured `TableModel` instance containing 2D cell grids (`CellDesc`), `BorderFlags`, and styles without generating HTML.

### `tentags.render_html(model: TableModel) -> str`
Renders a previously parsed `TableModel` instance into an HTML string.

### `tentags.render_xlsx(model: TableModel, output_filename: str) -> None`
Exports a `TableModel` directly to an Excel `.xlsx` file using `openpyxl`. Applies `openpyxl.styles.Font` (bold, italic, color), `openpyxl.styles.PatternFill` (background color), and `openpyxl.styles.Border` according to the table formula. Requires `pip install tentags[excel]`.

### `tentags.render_pdf(model: TableModel, output_filename: str) -> None`
Exports a `TableModel` directly to a vector **PDF** file using `ReportLab`. Translates IR coordinates, merged cell regions (`SPAN`), background fills (`BACKGROUND`), fonts, alignments, and border grids into native `ReportLab` `TableStyle` commands. Automatically selects portrait or landscape page orientation based on column count. Requires `pip install tentags[pdf]`.

---

## 🧪 Running Tests

To run the standalone test suite and generate sample visual outputs:

```bash
python test_library.py
```

Generated output files include:
- `test_output.html` — Summary HTML report of all rendered tables
- `test_output.xlsx` — Basic Excel table
- `test_style_output.xlsx` — Excel with styling tags
- `Q3_Financial_Dashboard.xlsx` / `.pdf` — Financial dashboard in Excel and PDF
- `Enterprise_Budget_Matrix.xlsx` / `.pdf` — Enterprise budget matrix in Excel and PDF

> PDF files require `pip install tentags[pdf]` (ReportLab).

---

## 📄 License

Licensed under the [MIT License](LICENSE). Copyright (c) 2026 Zhandos Mambetali.
