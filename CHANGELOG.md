# Changelog

All notable changes to this project will be documented in this file.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

---

## [2.1.9] - 2026-07-18

### Fixed
- Changed XLSX text, background, and border colors from transparent `00RRGGBB` values to opaque `FFRRGGBB` ARGB values for consistent display in Excel-compatible applications.

### Testing
- Added exact cross-renderer assertions for named and HEX text colors in IR, HTML, XLSX, and PDF, including nested `<bg><color><b>` styling.

---

## [2.1.8] - 2026-07-18

### Fixed
- Restored real Unicode italic and bold-italic font faces in PDF output, so `<i>` and nested `<b><i>` no longer fall back to regular or bold-only text.

### Testing
- Added one cross-renderer regression matrix for every supported cell tag: `<b>`, `<i>`, `<u>`, `<s>`, `<color>`, `<bg>`, `<fs>`, `<left>`, `<center>`, `<right>`, `<url>`, `<mark>`, `<value>`, `<img>`, `<cm>`, and `<rm>`.

---

## [2.1.7] - 2026-07-18

### Fixed
- Restored PDF `solid`, `dashed`, and `dotted` border patterns, including `-1` inner-grid and `-0` borderless suffix behavior, after the non-destructive `cm/rm` line-segment renderer change.

### Testing
- Added the complete nine-case border matrix across HTML, XLSX, and PDF: `solid`, `solid-1`, `solid-0`, `dashed`, `dashed-1`, `dashed-0`, `dotted`, `dotted-1`, and `dotted-0`, including `cm/rm` interactions and visible MultiTable artifacts.

---

## [2.1.6] - 2026-07-18

### Fixed
- Aligned XLSX and PDF `cm/rm` behavior with HTML: internal grid lines are hidden without creating destructive native merged ranges or PDF spans, so every logical cell retains its content, style, link, mark, and address.

---

## [2.1.5] - 2026-07-18

### Added
- Added the optional preamble extension `scale(A1=vertical,horizontal;...)` for renderer-independent relative row and column sizing.
- Added strict `1..5` scale validation, local A1 bounds checking, and deterministic per-axis `max()` merging.
- Added sparse `row_scales` and `col_scales` fields to `TableModel` without changing existing constructor calls.
- Added `scale=` support to `tentags.serialize.preamble()` and `dumps_preamble()`.
- Added HTML, XLSX, PDF, and MultiTable scale rendering with regression coverage.

### Fixed
- Unified PDF named-color conversion with XLSX color normalization so values such as `blue`, `white`, and `yellow` render consistently.

---

## [2.1.4] - 2026-07-17

### Fixed
- Synchronized package version configuration and metadata across the root and demo subprojects.
- Updated FastAPI and Flask demo requirements and hardcoded version strings to use the latest version.
- Overwrote older copies of `TENTAGS_LLM_BOOTSTRAP_PROMPT.md` in the demo projects with the actual root prompt file.

---

## [2.1.3] - 2026-07-17

### Fixed
- Fixed multiline `style(...)` parsing when the final style row contains only active/closing tags and no text. Such styled-empty cells are now preserved and correctly overlaid onto the matching `data(...)` row.
- Added regression coverage for open tags spanning multiple style rows, including the third-row `url=goto:` case where data text exists but the final style cell has no text body.

### Documentation
- Documented that `style(...)` cells may be text-empty while still carrying presentation. Do not treat them as missing rows when checking `preamble rows == style rows == data rows`.

---

## [2.1.2] - 2026-07-17

### Fixed
- Aligned HTML default cell alignment with PDF/XLSX by emitting centered horizontal alignment and middle vertical alignment when no explicit alignment tag is used.
- Allowed XLSX multitable stacked export to accept shared string gap settings such as `"1px"` without raising type errors.

---

## [2.1.1] - 2026-07-17

### Fixed
- Fixed `multitable_pdf()` layout when shared HTML/PDF settings pass `gap` as a CSS-like string such as `"24px"`.
- PDF multitable `gap` now accepts numbers and numeric strings with optional `px` or `pt` suffixes.

---

## [2.1.0] - 2026-07-17

Serializer API, Addressing Model, and Multitable Layout.

### Added
- Added Serializer API namespace: `tentags.serialize.preamble()`, `tentags.serialize.style()`, and `tentags.serialize.data()` for converting Python values and matrices into canonical TenTags DSL.
- Added compatible top-level aliases: `dumps_preamble()`, `dumps_style()`, and `dumps_data()`.
- Added explicit Serializer API coverage for `multitable_html()`, `multitable_xlsx()`, and `multitable_pdf()` table items.
- Added runnable SQLite database serialization examples for single-table and multitable reports.
- Added library-level multitable export settings dictionaries: `DEFAULT_MULTITABLE_HTML_SETTINGS`, `DEFAULT_MULTITABLE_XLSX_SETTINGS`, and `DEFAULT_MULTITABLE_PDF_SETTINGS`.
- Added canonical `settings=...` support for multitable HTML, XLSX, and PDF export examples.
- Added PDF multitable layout controls for `tables_per_row`, `tables_per_row="auto"`, `tables_per_page`, `tables_per_page="auto"`, and `gap`.
- Added multitable documentation for table ordering and column validation through `table_order` and `columns`.

### Changed
- Documented the canonical path `Python structures -> tentags.serialize.* -> TenTags DSL -> compile() -> IR`, keeping `compile(preamble, style, data)` as the single compiler entry point.
- Updated multitable examples to use named settings dictionaries instead of magic inline parameters.
- Clarified that multitable means several separate List/Table entries, each with its own preamble, style, and data.

---

## [2.0.3] - 2026-07-16

### Added
- Added the single `<img src=... w=... h=...>` tag for compact image cells in `data()`.
- Added `m=<pixels>` support for equal image margin on all four sides.
- Added stretch-aware image rendering: `stretch=1` lets image cells expand with the image, while `stretch=0` forces image height to `cell_height` and width to `auto`.
- Documented image sizing rules for numeric pixel sizes and `auto`.

---

## [2.0.2] - 2026-07-15

### Fixed
- Synchronized Django template tag tests with direct script execution.
- Added metadata checks that validate package version consistency before publishing.

---

## [2.0.1] - yanked

### Fixed
- `NameError: name 'Union' is not defined` on **Python 3.13+** at import time.  
  The `render_pdf()` signature used bare `Union[str, Any]` instead of the module-aliased
  `_Union[str, _Any]`. Fixed to be consistent with all other type annotations in the file.

> **Removed from PyPI** due to a defect discovered after publication.
> Use the latest stable **2.1.9** release instead.

---

## [2.0.0] - yanked

> **Removed from PyPI** due to `NameError: Union is not defined` on Python 3.13+ at import.  
> Use the latest stable **2.1.9** release instead.

### Added (carried into 2.0.2 and later)
- `<u>` tag — underline text (HTML inline CSS, XLSX `Font(underline="single")`, PDF `UNDERLINE`)
- `<s>` tag — strikethrough text (HTML inline CSS, XLSX `Font(strike=True)`, PDF `STRIKETHROUGH`)
- `<url=https://...>` tag — clickable hyperlink (HTML `<a>`, XLSX native hyperlink, PDF `<link>`)
- Decoupled API: `render(preamble, style, data)` — reusable style templates
- Django Template Tags: `{% tt %}`, `{% tentags_inline formula %}`, `{% tentags_inline p s d %}`
- Flask integration: `tentags.contrib.flask.init_app(app)`
- FastAPI integration: `tentags.contrib.fastapi.register_templates(templates)`
- Jinja2 Extension: `TenTagsExtension`, `{{ tentags(...) }}` global function
- `EXAMPLES.md` — comprehensive reference guide included in the package
- `MANIFEST.in` — ensures `.md` files are bundled in sdist

---

## [1.1.6] - yanked
## [1.1.5] - yanked
## [1.1.4] - yanked

> **Removed from PyPI** — contained the same `NameError: Union is not defined` bug on Python 3.13+.
> Use the latest stable **2.1.9** release instead.

---

## [1.1.3] - 2026-06-xx

### Added
- Multi-table rendering: `multitable_html()`, `multitable_pdf()`, `multitable_xlsx()`
- `validate()` utility function
- `features()` — check available render backends
- `info()` — system diagnostics

---

## [1.1.x] - earlier releases

See [GitHub commit history](https://github.com/Jandos77/tentags/commits/main) for details.

---

## [1.0.0] - initial stable release

- Core parser and renderer
- HTML, XLSX, PDF output
- `<b>`, `<i>`, `<color>`, `<bg>`, `<fs>`, `<left>`, `<center>`, `<right>`, `<cm>`, `<rm>` tags
- `compile()`, `parse()`, `render()`, `render_html()`, `render_xlsx()`, `render_pdf()`
