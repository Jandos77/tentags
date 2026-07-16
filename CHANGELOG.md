# Changelog

All notable changes to this project will be documented in this file.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

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
> Use **2.0.3** instead.

---

## [2.0.0] - yanked

> **Removed from PyPI** due to `NameError: Union is not defined` on Python 3.13+ at import.  
> Use **2.0.3** instead.

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
> Use **2.0.3** instead.

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
