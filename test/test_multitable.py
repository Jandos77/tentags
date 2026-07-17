import tentags
from demo_paths import demo_output_path

def test_multitable():
    print("--- Test 9 (Multi-Table Rendering) ---")
    
    # 1. Define shared templates (preambles and styles)
    preamble_a = '3, 4, 1, #1977ff, solid-1, 1' # 3x4 grid with blue grid borders
    preamble_b = '4, 4, 1, green, solid, 1'     # 4x4 grid with green outer border only
    
    style_a = 'style(<bg=white><center><b><cm>Materials Summary, , , </cm></b></center></bg>; <center><bg=white> , , , </bg></center>)'
    style_b = 'style(<bg=white><center><b><cm>Tools Summary, , , </cm></b></center></bg>; <center><bg=white> , , , </bg></center>)'

    # 2. Define different datasets
    data_a = 'data(Item, Qty, Price, Total; Wood, 10, 150, 1500; Metal, 5, 300, 1500)'
    data_b = 'data(Tool, Qty, Condition, Status; Hammer, 2, New, Active; Drill, 1, Used, Active; Saw, 3, New, Active)'

    # 3. Assemble table definitions list
    tables_list = [
        {
            "preamble": preamble_a,
            "style": style_a,
            "data": data_a,
            "title": "Materials Summary Report",
            "sheet_name": "MaterialsSheet"
        },
        {
            "preamble": preamble_b,
            "style": style_b,
            "data": data_b,
            "title": "Tools Inventory Report",
            "sheet_name": "ToolsSheet"
        }
    ]

    # --- HTML MULTITABLE ---
    print("\n[HTML] Rendering Grid Layout...")
    html_grid = tentags.multitable_html(tables_list, layout="grid", cols=2, gap="30px", full_page=True)
    html_output = demo_output_path("multitable_report.html")
    with open(html_output, "w", encoding="utf-8") as f:
        f.write(html_grid)
    print(f"HTML multitable saved as: {html_output}")

    # --- EXCEL MULTITABLE (Sheets Mode) ---
    print("\n[Excel] Generating separate sheets...")
    sheets_output = demo_output_path("multitable_sheets.xlsx")
    tentags.multitable_xlsx(tables_list, sheets_output, mode="sheets")
    print(f"Excel workbook (sheets) saved as: {sheets_output}")

    # --- EXCEL MULTITABLE (Stacked Mode) ---
    print("\n[Excel] Generating stacked sheet...")
    stacked_output = demo_output_path("multitable_stacked.xlsx")
    tentags.multitable_xlsx(tables_list, stacked_output, mode="stacked", gap=3)
    print(f"Excel workbook (stacked) saved as: {stacked_output}")

    # --- PDF MULTITABLE ---
    print("\n[PDF] Generating multi-page document...")
    try:
        pdf_output = demo_output_path("multitable_report.pdf")
        tentags.multitable_pdf(tables_list, pdf_output, page_size="A4", orientation="portrait", page_break_after_each=False )
        print(f"PDF document saved as: {pdf_output}")
    except ImportError as e:
        print(f"Skipping PDF export: {e}")

if __name__ == "__main__":
    test_multitable()
