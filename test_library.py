import tentags

def test():
    # 1. Тест базового вложенного слияния строк и столбцов
    print("--- Test 1 (Basic & Nesting): ---")
    expr = '3,4,1,"#000","solid",1, data(#,<rm>Date</rm>,Name,Job;1,<rm>10.07.2026</rm><cm>,Jone</cm>,None; ,,Piter)'
    html = tentags.render(expr)
    print(html)
    
    # 2. Тест подстановки переменных
    print("\n--- Test 2 (Variable Context): ---")
    expr_vars = '2,2,1,"#ccc","solid",0,40, data(User, Status; NameVar, StateVar)'
    context = {
        'NameVar': 'Antigravity AI',
        'StateVar': 'Active'
    }
    html_vars = tentags.render(expr_vars, context)
    print(html_vars)

    # 3. Тест импорта CSV
    print("\n--- Test 3 (CSV Import): ---")
    # Убедитесь, что предварительно создали файл test_data.csv
    expr_csv = '3,4,1,"#000","solid",1, data(csv("test_data.csv"))'
    html_csv = tentags.render(expr_csv)
    print(html_csv)

    # 4. Тест нового API разделенного TableModel
    print("\n--- Test 4 (Decoupled TableModel & HTML Renderer API): ---")
    expr_decoupled = '2,2,1,"blue","solid",1, data(Hello, World; One, Two)'
    # 1. Сначала парсим в промежуточную TableModel
    table_model = tentags.parse(expr_decoupled)
    print(f"Parsed TableModel metadata: rows={table_model.rows}, cols={table_model.cols}, border={table_model.border_color}")
    # 2. Передаем модель в рендерер HTML
    html_decoupled = tentags.render_html(table_model)
    print("Rendered HTML:")
    print(html_decoupled)

    # 5. Тест генерации Excel (.xlsx)
    print("\n--- Test 5 (Excel XLSX Renderer API): ---")
    expr_xlsx = '3,4,1,"#000","solid",1, data(#,<rm>Date</rm>,Name,Job;1,<rm>10.07.2026</rm><cm>,Jone</cm>,None; ,,Piter)'
    model_xlsx = tentags.parse(expr_xlsx)
    output_filename = "test_output.xlsx"
    tentags.render_xlsx(model_xlsx, output_filename)
    print(f"Excel table generated successfully and saved as: {output_filename}")

    # 6. Тест новых тегов стилизации <b>, <i>, <color>, <bg>
    print("\n--- Test 6 (Styling Tags: b, i, color, bg): ---")
    expr_style = '2,2,1,"#000","solid",0,40, data(Regular, <b>Bold Text</b>; <color=red><i>Italic Red</i></color>, <bg=#eeeeee>Gray BG</bg>)'
    html_style = tentags.render(expr_style)
    print("Rendered HTML with styles:")
    print(html_style)

    model_style = tentags.parse(expr_style)
    tentags.render_xlsx(model_style, "test_style_output.xlsx")
    print("Excel table with custom fonts and fills saved as: test_style_output.xlsx")

    # 6.2 Проверим теги выравнивания и размера шрифта <fs>, <left>, <center>, <right>
    print("\n--- Test 6.2 (Typography & Alignment: fs, left, center, right): ---")
    expr_align = '2,3,1,"#64748b","solid",0,45, data(<fs=18><left>Left 18px</left></fs>, <center>Centered</center>, <right>Right Aligned</right>; <b>A</b>, <i>B</i>, <color=blue>C</color>)'
    html_align = tentags.render(expr_align)
    print("Rendered HTML with alignment and font size:")
    print(html_align)
    model_align = tentags.parse(expr_align)
    tentags.render_xlsx(model_align, "test_align_output.xlsx")
    print("Excel table with alignment and font size saved as: test_align_output.xlsx")

    # 6.3 Комплексный пример (Financial Dashboard)
    print("\n--- Test 6.3 (Advanced Showcase: Q3 Financial Dashboard): ---")
    expr_dashboard = '''4,4,1,"#cbd5e1","solid",0,45, data(
        <fs=18><bg=#1e293b><color=white><b><cm>Q3 Financial Performance Dashboard, , , , </cm></b></color></bg></fs>;
        <bg=#f1f5f9><b><left>Department</left></b></bg>, <bg=#f1f5f9><b><center>Revenue</center></b></bg>, <bg=#f1f5f9><b><center>Expenses</center></b></bg>, <bg=#f1f5f9><b><center>Net Profit</center></b></bg>;
        <left>Engineering</left>, <right>"$240,000"</right>, <right>"$180,000"</right>, <bg=#dcfce7><color=#166534><b><right>"+$60,000"</right></b></color></bg>;
        <left>Sales & Marketing</left>, <right>"$310,000"</right>, <right>"$210,000"</right>, <bg=#dcfce7><color=#166534><b><right>"+$100,000"</right></b></color></bg>
    )'''
    html_dashboard = tentags.render(expr_dashboard)
    print("Rendered HTML Dashboard:")
    print(html_dashboard)
    model_dashboard = tentags.parse(expr_dashboard)
    tentags.render_xlsx(model_dashboard, "Q3_Financial_Dashboard.xlsx")
    print("Excel dashboard table saved as: Q3_Financial_Dashboard.xlsx")
    try:
        tentags.render_pdf(model_dashboard, "Q3_Financial_Dashboard.pdf")
        print("PDF dashboard table saved as: Q3_Financial_Dashboard.pdf")
    except ImportError as e:
        print(f"Skipping PDF dashboard export: {e}")

    # 6.4 Пример матрицы с вертикальными (<rm>) и горизонтальными (<cm>) слияниями и цветами Excel
    print("\n--- Test 6.4 (Excel Matrix Example: Multi-row/col merges & fills): ---")
    expr_matrix = '''5,5,1,"#B0C4DE","solid",0,35, data(
        <fs=16><bg=#1F4E78><color=white><b><cm>2026 Enterprise Budget & Allocation Matrix, , , , </cm></b></color></bg></fs>;
        <bg=#DDEBF7><b><rm><center>Category</center></rm></b></bg>, <bg=#DDEBF7><b><cm><center>Q1 & Q2 Allocation, </center></cm></b></bg>, <bg=#DDEBF7><b><cm><center>Q3 & Q4 Allocation, </center></cm></b></bg>;
        <bg=#DDEBF7><b><rm> </rm></b></bg>, <bg=#F2F2F2><b><center>Hardware</center></b></bg>, <bg=#F2F2F2><b><center>Software</center></b></bg>, <bg=#F2F2F2><b><center>Hardware</center></b></bg>, <bg=#F2F2F2><b><center>Software</center></b></bg>;
        <bg=#FFF2CC><b><left>R&D Division</left></b></bg>, <right>"$150,000"</right>, <right>"$85,000"</right>, <right>"$120,000"</right>, <right>"$95,000"</right>;
        <bg=#E2EFDA><color=#375623><b><left>Total Budget</left></b></color></bg>, <bg=#E2EFDA><color=#375623><b><cm><right>"$235,000", </right></cm></b></color></bg>, <bg=#E2EFDA><color=#375623><b><cm><right>"+$215,000", </right></cm></b></color></bg>
    )'''
    html_matrix = tentags.render(expr_matrix)
    print("Rendered HTML Matrix:")
    print(html_matrix)
    model_matrix = tentags.parse(expr_matrix)
    tentags.render_xlsx(model_matrix, "Enterprise_Budget_Matrix.xlsx")
    print("Excel matrix table saved as: Enterprise_Budget_Matrix.xlsx")
    try:
        tentags.render_pdf(model_matrix, "Enterprise_Budget_Matrix.pdf")
        print("PDF matrix table saved as: Enterprise_Budget_Matrix.pdf")
    except ImportError as e:
        print(f"Skipping PDF matrix export: {e}")

    # 7. Генерация сводного HTML-файла с результатами
    print("\n--- Test 7 (Generating Summary HTML File): ---")
    html_template = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TenTags Standalone Test Outputs</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
    <style>
        body {{
            font-family: 'Inter', sans-serif;
            background-color: #f8fafc;
            color: #0f172a;
            margin: 0;
            padding: 40px;
        }}
        h1 {{
            font-size: 24px;
            margin-bottom: 24px;
            color: #1e293b;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
            gap: 24px;
        }}
        .card {{
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }}
        .card-title {{
            font-weight: 600;
            font-size: 14px;
            color: #64748b;
            margin-bottom: 12px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        .table-container {{
            overflow-x: auto;
        }}
    </style>
</head>
<body>
    <h1>TenTags Standalone Library - Test Report</h1>
    <div class="grid">
        <div class="card" style="grid-column: 1 / -1;">
            <div class="card-title">Test 6.4: Excel Matrix Example (Row & Column Merges with Excel Theme Fills)</div>
            <div class="table-container">
                {html_matrix}
            </div>
        </div>

        <div class="card" style="grid-column: 1 / -1;">
            <div class="card-title">Test 6.3: Advanced Showcase (Q3 Financial Dashboard with Merges, Fills & Typography)</div>
            <div class="table-container">
                {html_dashboard}
            </div>
        </div>

        <div class="card">
            <div class="card-title">Test 1: Basic nested column & row merge</div>
            <div class="table-container">
                {html}
            </div>
        </div>

        <div class="card">
            <div class="card-title">Test 2: Variable interpolation context</div>
            <div class="table-container">
                {html_vars}
            </div>
        </div>

        <div class="card">
            <div class="card-title">Test 3: CSV Import (with active merges)</div>
            <div class="table-container">
                {html_csv}
            </div>
        </div>

        <div class="card">
            <div class="card-title">Test 4: Decoupled TableModel & HTML Renderer</div>
            <div class="table-container">
                {html_decoupled}
            </div>
        </div>

        <div class="card">
            <div class="card-title">Test 6: Advanced styling tags (bold, italic, color, bg)</div>
            <div class="table-container">
                {html_style}
            </div>
        </div>

        <div class="card">
            <div class="card-title">Test 6.2: Typography & Alignment (fs, left, center, right)</div>
            <div class="table-container">
                {html_align}
            </div>
        </div>
    </div>
</body>
</html>"""
    
    html_filename = "test_output.html"
    with open(html_filename, "w", encoding="utf-8") as f:
        f.write(html_template)
    print(f"Summary HTML report generated successfully and saved as: {html_filename}")

if __name__ == '__main__':
    test()