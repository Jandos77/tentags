from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import tentags
from demo_paths import demo_output_path


HTML_OUTPUT = demo_output_path("demo_multitable_navigation.html")
XLSX_OUTPUT = demo_output_path("demo_multitable_navigation.xlsx")
PDF_OUTPUT = demo_output_path("demo_multitable_navigation.pdf")


def _tables():
    return [
        {
            "document": "Dashboard",
            "table_name": "Menu",
            "sheet_name": "Menu",
            "title": "Главное меню",
            "preamble": tentags.serialize.preamble(4, 2, border_color="#1e40af", border_style="solid-1", cell_height=32),
            "style": tentags.serialize.style([
                ["<bg=#dbeafe><b></b></bg>"] * 2,
                ["<bg=#f0f9ff></bg>"] * 2,
                ["<bg=#f0f9ff></bg>"] * 2,
                ["<bg=#f0f9ff></bg>"] * 2,
            ]),
            "data": tentags.serialize.data([
                ["<b>Раздел</b>", "<b>Действие</b>"],
                ["Продажи", "<url=goto:Sales!Report!A1>Открыть отчёт по продажам</url>"],
                ["Товары", "<url=goto:Products!Catalog!A1>Каталог товаров</url>"],
                ["Клиенты", "<url=goto:Customers!List!Summary>Сводка по клиентам</url>"],
            ]),
        },
        {
            "document": "Sales",
            "table_name": "Report",
            "sheet_name": "Report",
            "title": "Отчёт по продажам",
            "preamble": tentags.serialize.preamble(5, 4, border_color="#166534", border_style="solid-1", cell_height=28),
            "style": tentags.serialize.style([
                ["<bg=#dcfce7><b></b></bg>"] * 4,
                ["<bg=#f0fdf4></bg>"] * 4,
                ["<bg=#f0fdf4></bg>"] * 4,
                ["<bg=#f0fdf4></bg>"] * 4,
                ["<bg=#bbf7d0><b></b></bg>"] * 4,
            ]),
            "data": tentags.serialize.data([
                ["Период", "Выручка", "Себестоимость", "Прибыль"],
                ["Январь", "1 250 000", "820 000", "<right><color=#166534><b>430 000</b></color></right>"],
                ["Февраль", "1 480 000", "910 000", "<right><color=#166534><b>570 000</b></color></right>"],
                ["Март", "1 620 000", "980 000", "<right><color=#166534><b>640 000</b></color></right>"],
                ["<mark=Total><b>Итого</b>", "<b>4 350 000</b>", "<b>2 710 000</b>", "<right><color=#166534><b>1 640 000</b></color></right>"],
            ]),
        },
        {
            "document": "Products",
            "table_name": "Catalog",
            "sheet_name": "Catalog",
            "title": "Каталог товаров",
            "preamble": tentags.serialize.preamble(6, 3, border_color="#7c2d12", border_style="solid-1", cell_height=28),
            "style": tentags.serialize.style([
                ["<bg=#ffedd5><b></b></bg>"] * 3,
                ["<bg=#fff7ed></bg>"] * 3,
                ["<bg=#fff7ed></bg>"] * 3,
                ["<bg=#fff7ed></bg>"] * 3,
                ["<bg=#fff7ed></bg>"] * 3,
                ["<bg=#fed7aa><b></b></bg>"] * 3,
            ]),
            "data": tentags.serialize.data([
                ["Артикул", "Название", "Цена"],
                ["P001", "Ноутбук Dell", "89 990"],
                ["P002", "Монитор 27\"", "34 500"],
                ["P003", "Клавиатура", "4 200"],
                ["P004", "Мышь Logitech", "2 890"],
                ["<mark=Summary><b>Всего позиций: 4</b>", "", ""],
            ]),
        },
        {
            "document": "Customers",
            "table_name": "List",
            "sheet_name": "Customers",
            "title": "Клиенты",
            "preamble": tentags.serialize.preamble(4, 2, border_color="#581c87", border_style="solid", cell_height=30),
            "style": tentags.serialize.style([
                ["<bg=#f3e8ff><b></b></bg>"] * 2,
                ["<bg=#faf5ff></bg>"] * 2,
                ["<bg=#faf5ff></bg>"] * 2,
                ["<bg=#f3e8ff><b></b></bg>"] * 2,
            ]),
            "data": tentags.serialize.data([
                ["<b>Клиент</b>", "<b>Статус</b>"],
                ["ООО Ромашка", "VIP"],
                ["ИП Иванов", "Regular"],
                ["<mark=Summary><b>Всего клиентов: 2</b>", "<url=goto:Dashboard!Menu!A1>← В меню</url>"],
            ]),
        },
    ]


HTML_SETTINGS = {
    "output": HTML_OUTPUT,
    "table_order": ["Dashboard!Menu", "Sales!Report", "Products!Catalog", "Customers!List"],
    "html_title": "Дашборд — Multitable с навигацией",
    "layout": "vertical",
    "gap": "40px",
    "full_page": True,
}

XLSX_SETTINGS = {
    "output": XLSX_OUTPUT,
    "table_order": ["Dashboard!Menu", "Sales!Report", "Products!Catalog", "Customers!List"],
    "mode": "sheets",
    "gap": 3,
    "show_titles": True,
}

PDF_SETTINGS = {
    "output": PDF_OUTPUT,
    "table_order": ["Dashboard!Menu", "Sales!Report", "Products!Catalog", "Customers!List"],
    "tables_per_row": "auto",
    "tables_per_page": "auto",
    "gap": 20,
    "page_size": "A4",
    "orientation": "landscape",
}


def build_multitable_navigation_serializer_artifacts():
    tables = _tables()
    tentags.multitable_html(tables, settings=HTML_SETTINGS)
    tentags.multitable_xlsx(tables, settings=XLSX_SETTINGS)
    tentags.multitable_pdf(tables, settings=PDF_SETTINGS)
    return HTML_OUTPUT, XLSX_OUTPUT, PDF_OUTPUT


def test_multitable_navigation_serializer_outputs_files_in_demo_output():
    html_output, xlsx_output, pdf_output = build_multitable_navigation_serializer_artifacts()

    html = html_output.read_text(encoding="utf-8")
    assert html.count("<table ") == 4
    assert 'href="#tt-Sales-Report-A1"' in html
    assert 'href="#tt-Products-Catalog-A1"' in html
    assert 'href="#tt-Customers-List-mark-Summary"' in html
    assert 'href="#tt-Dashboard-Menu-A1"' in html

    xlsx_bytes = xlsx_output.read_bytes()
    assert xlsx_bytes.startswith(b"PK")
    assert xlsx_output.stat().st_size > 1000

    pdf_bytes = pdf_output.read_bytes()
    assert pdf_bytes.startswith(b"%PDF")
    assert pdf_output.stat().st_size > 1000
    assert b"/FontFile2" in pdf_bytes


if __name__ == "__main__":
    outputs = build_multitable_navigation_serializer_artifacts()
    print("Все файлы успешно созданы:")
    for output in outputs:
        data = output.read_bytes()
        assert len(data) > 1000
        if output.suffix == ".pdf":
            assert data.startswith(b"%PDF")
        if output.suffix == ".xlsx":
            assert data.startswith(b"PK")
        print("   •", output)
