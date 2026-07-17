from pathlib import Path
import sqlite3
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import tentags
from demo_paths import DEMO_OUTPUT_DIR


STATUS_COLORS = {
    "Closed": {"bg": "#dcfce7", "fg": "#166534"},
    "Review": {"bg": "#fef3c7", "fg": "#92400e"},
    "Forecast": {"bg": "#dbeafe", "fg": "#1e3a8a"},
}


def _create_finance_db(path: Path) -> None:
    conn = sqlite3.connect(path)
    try:
        conn.execute(
            """
            CREATE TABLE monthly_report (
                period TEXT NOT NULL,
                revenue INTEGER NOT NULL,
                expenses INTEGER NOT NULL,
                profit INTEGER NOT NULL,
                status TEXT NOT NULL
            )
            """
        )
        conn.executemany(
            "INSERT INTO monthly_report VALUES (?, ?, ?, ?, ?)",
            [
                ("January", 125000, 82000, 43000, "Closed"),
                ("February", 132500, 87500, 45000, "Closed"),
                ("March", 141200, 91300, 49900, "Closed"),
                ("April", 138000, 94500, 43500, "Closed"),
                ("May", 152400, 98200, 54200, "Closed"),
                ("June", 160750, 104300, 56450, "Closed"),
                ("July", 158900, 109100, 49800, "Review"),
                ("August", 171300, 112800, 58500, "Forecast"),
            ],
        )
        conn.execute(
            """
            CREATE TABLE dashboard_links (
                section TEXT NOT NULL,
                target TEXT NOT NULL,
                owner TEXT NOT NULL,
                status TEXT NOT NULL
            )
            """
        )
        conn.executemany(
            "INSERT INTO dashboard_links VALUES (?, ?, ?, ?)",
            [
                ("Finance", "Report!Sales!A1", "CFO", "Closed"),
                ("Invoices", "Invoice!Items!A1", "Ops", "Review"),
            ],
        )
        conn.execute(
            """
            CREATE TABLE invoice_items (
                item TEXT NOT NULL,
                qty INTEGER NOT NULL,
                unit_price INTEGER NOT NULL,
                total INTEGER NOT NULL
            )
            """
        )
        conn.executemany(
            "INSERT INTO invoice_items VALUES (?, ?, ?, ?)",
            [
                ("Paper", 2, 25, 50),
                ("Ink", 4, 30, 120),
            ],
        )
        conn.commit()
    finally:
        conn.close()


def _rows_from_db(path: Path, sql: str) -> list[dict]:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        return [dict(row) for row in conn.execute(sql)]
    finally:
        conn.close()


def _financial_model_from_db(path: Path):
    records = _rows_from_db(
        path,
        """
        SELECT period, revenue, expenses, profit, status
        FROM monthly_report
        ORDER BY rowid
        """,
    )

    data_rows = [
        [
            "<color=#ffffff><b>Period</b></color>",
            "<right><color=#ffffff><b>Revenue</b></color></right>",
            "<right><color=#ffffff><b>Expenses</b></color></right>",
            "<right><color=#ffffff><b>Profit</b></color></right>",
            "<center><color=#ffffff><b>Status</b></color></center>",
        ]
    ]
    style_rows = [["<bg=#0f172a><b></b></bg>"] * 5]

    for index, record in enumerate(records):
        base_bg = "#ffffff" if index % 2 == 0 else "#f8fafc"
        status = STATUS_COLORS[record["status"]]
        style_rows.append(
            [
                f"<bg={base_bg}></bg>",
                f"<bg={base_bg}></bg>",
                f"<bg={base_bg}></bg>",
                f"<bg={base_bg}></bg>",
                f"<bg={status['bg']}></bg>",
            ]
        )
        data_rows.append(
            [
                record["period"],
                f"<right>{record['revenue']}</right>",
                f"<right>{record['expenses']}</right>",
                f"<right><color=#16a34a><b>{record['profit']}</b></color></right>",
                f"<center><color={status['fg']}>{record['status']}</color></center>",
            ]
        )

    preamble = tentags.serialize.preamble(
        len(data_rows),
        5,
        border_color="#64748b",
        border_style="solid-1",
        cell_height=28,
    )
    style = tentags.serialize.style(style_rows, expected_rows=len(data_rows), expected_cols=5)
    data = tentags.serialize.data(data_rows, expected_rows=len(data_rows), expected_cols=5)
    return tentags.compile(preamble, style, data)


def _dashboard_table_from_db(path: Path) -> dict:
    records = _rows_from_db(
        path,
        """
        SELECT section, target, owner, status
        FROM dashboard_links
        ORDER BY rowid
        """,
    )
    data_rows = [["Section", "Target", "Owner", "Status"]]
    style_rows = [["<bg=#dbeafe><b></b></bg>"] * 4]

    for index, record in enumerate(records):
        base_bg = "#ffffff" if index % 2 == 0 else "#eff6ff"
        status = STATUS_COLORS[record["status"]]
        data_rows.append(
            [
                record["section"],
                f"<url=goto:{record['target']}>Open</url>",
                record["owner"],
                f"<center><color={status['fg']}>{record['status']}</color></center>",
            ]
        )
        style_rows.append(
            [
                f"<bg={base_bg}></bg>",
                f"<bg={base_bg}></bg>",
                f"<bg={base_bg}></bg>",
                f"<bg={status['bg']}></bg>",
            ]
        )

    return {
        "document": "Dashboard",
        "table_name": "Menu",
        "sheet_name": "Menu",
        "title": "Dashboard Menu",
        "preamble": tentags.serialize.preamble(len(data_rows), 4, border_color="#64748b", border_style="solid-1", cell_height=24),
        "style": tentags.serialize.style(style_rows, expected_rows=len(data_rows), expected_cols=4),
        "data": tentags.serialize.data(data_rows, expected_rows=len(data_rows), expected_cols=4),
    }


def _invoice_table_from_db(path: Path) -> dict:
    records = _rows_from_db(
        path,
        """
        SELECT item, qty, unit_price, total
        FROM invoice_items
        ORDER BY rowid
        """,
    )
    data_rows = [["Item", "Qty", "Unit Price", "Total"]]
    style_rows = [["<bg=#ffedd5><b></b></bg>"] * 4]

    for index, record in enumerate(records):
        base_bg = "#ffffff" if index % 2 == 0 else "#fff7ed"
        data_rows.append(
            [
                record["item"],
                f"<right>{record['qty']}</right>",
                f"<right>{record['unit_price']}</right>",
                f"<right><b>{record['total']}</b></right>",
            ]
        )
        style_rows.append([f"<bg={base_bg}></bg>"] * 4)

    return {
        "document": "Invoice",
        "table_name": "Items",
        "sheet_name": "Items",
        "title": "Invoice Items",
        "preamble": tentags.serialize.preamble(len(data_rows), 4, border_color="#64748b", border_style="solid-1", cell_height=24),
        "style": tentags.serialize.style(style_rows, expected_rows=len(data_rows), expected_cols=4),
        "data": tentags.serialize.data(data_rows, expected_rows=len(data_rows), expected_cols=4),
    }


def build_single_db_report(output_dir: Path) -> tuple[Path, Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    db_path = output_dir / "serializer_db_example.sqlite"
    _create_finance_db(db_path)
    model = _financial_model_from_db(db_path)

    html_output = output_dir / "serializer_db_report.html"
    pdf_output = output_dir / "serializer_db_report.pdf"
    xlsx_output = output_dir / "serializer_db_report.xlsx"

    html_output.write_text(tentags.render_html(model), encoding="utf-8")
    tentags.render_pdf(model, str(pdf_output))
    tentags.render_xlsx(model, str(xlsx_output))
    return html_output, pdf_output, xlsx_output


def build_multitable_db_report(output_dir: Path) -> tuple[Path, Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    db_path = output_dir / "serializer_multitable_db_example.sqlite"
    _create_finance_db(db_path)
    tables = [_dashboard_table_from_db(db_path), _invoice_table_from_db(db_path), {
        "document": "Report",
        "table_name": "Sales",
        "sheet_name": "Sales",
        "title": "Sales Report",
        "preamble": tentags.serialize.preamble(1, 1, border_color="#64748b", border_style="solid-1", cell_height=24),
        "style": tentags.serialize.style([["<bg=#dcfce7><b></b></bg>"]], expected_rows=1, expected_cols=1),
        "data": tentags.serialize.data([["<mark=A1>Sales top"]], expected_rows=1, expected_cols=1),
    }]

    settings = {
        "table_order": ["Dashboard!Menu", "Invoice!Items", "Report!Sales"],
        "columns": {
            "Dashboard!Menu": ["Section", "Target", "Owner", "Status"],
            "Invoice!Items": ["Item", "Qty", "Unit Price", "Total"],
            "Report!Sales": ["Sales top"],
        },
    }
    html_output = output_dir / "serializer_multitable_db_report.html"
    pdf_output = output_dir / "serializer_multitable_db_report.pdf"
    xlsx_output = output_dir / "serializer_multitable_db_report.xlsx"

    tentags.multitable_html(
        tables,
        settings={
            **settings,
            "output": html_output,
            "full_page": True,
            "layout": "grid",
            "cols": 2,
            "tables_per_row": 2,
            "html_title": "Serializer DB Multitable Report",
        },
    )
    tentags.multitable_pdf(
        tables,
        settings={
            **settings,
            "output": pdf_output,
            "tables_per_row": "auto",
            "tables_per_page": "auto",
            "page_size": "A4",
            "orientation": "landscape",
            "page_break_after_each": False,
        },
    )
    tentags.multitable_xlsx(
        tables,
        settings={
            **settings,
            "output": xlsx_output,
            "mode": "sheets",
            "tables_per_sheet": 1,
        },
    )
    return html_output, pdf_output, xlsx_output


def test_serializer_single_table_from_sqlite_db(tmp_path):
    html_output, pdf_output, xlsx_output = build_single_db_report(tmp_path)

    html = html_output.read_text(encoding="utf-8")
    assert "January" in html
    assert "#dcfce7" in html
    assert pdf_output.read_bytes().startswith(b"%PDF")
    assert xlsx_output.stat().st_size > 1000


def test_serializer_multitable_from_sqlite_db(tmp_path):
    html_output, pdf_output, xlsx_output = build_multitable_db_report(tmp_path)

    html = html_output.read_text(encoding="utf-8")
    assert html.count("<table ") == 3
    assert 'href="#tt-Invoice-Items-A1"' in html
    assert pdf_output.read_bytes().startswith(b"%PDF")
    assert xlsx_output.stat().st_size > 1000


if __name__ == "__main__":
    single_outputs = build_single_db_report(DEMO_OUTPUT_DIR)
    multitable_outputs = build_multitable_db_report(DEMO_OUTPUT_DIR)
    for output in [*single_outputs, *multitable_outputs]:
        data = output.read_bytes()
        assert len(data) > 100
        if output.suffix == ".pdf":
            assert data.startswith(b"%PDF")
        print(f"Generated: {output}")
