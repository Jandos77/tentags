import sqlite3
import tentags
import os
from demo_paths import demo_output_path

def setup_database_and_get_rows():
    db_filename = demo_output_path("company.db")
    
    # Recreate clean SQLite database file for demonstration
    if os.path.exists(db_filename):
        try:
            os.remove(db_filename)
        except OSError:
            pass
            
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()
    
    # Create schema and load sample sales data
    cursor.execute("""
        CREATE TABLE sales (
            product TEXT,
            q1_sales INTEGER,
            q2_sales INTEGER
        )
    """)
    cursor.executemany("""
        INSERT INTO sales VALUES (?, ?, ?)
    """, [
        ("Laptops", 150000, 180000),
        ("Smartphones", 320000, 290000),
        ("Tablets", 90000, 120000)
    ])
    conn.commit()
    
    # Query database and delegate classification logic to SQL
    cursor.execute("""
        SELECT 
            product, 
            q1_sales, 
            q2_sales,
            CASE 
                WHEN q2_sales > q1_sales THEN 'Growth'
                ELSE 'Decline'
            END as status
        FROM sales
    """)
    rows = cursor.fetchall()
    
    conn.close()
    return rows

def get_status_cell(status):
    # Map status value to specific presentation styling
    colors = {
        "Growth": ("#dcfce7", "#166534"),
        "Decline": ("#fee2e2", "#991b1b"),
    }
    bg, fg = colors.get(status, ("white", "black"))
    
    return (
        f"<bg={bg}><color={fg}>"
        f"<b><center>{status}</center></b>"
        f"</color></bg>"
    )

def build_tentags_expression(db_rows):
    num_rows = len(db_rows) + 2  # Title + Header + Data rows
    num_cols = 4
    
    expr_lines = []
    
    # 1. Title Row (merged across all columns)
    expr_lines.append("<fs=14><bg=#1e293b><color=white><b><cm>Electronics Sales Report, , , </cm></b></color></bg></fs>")
    
    # 2. Header Row
    expr_lines.append("<bg=#f8fafc><b><left>Product</left></b></bg>, <bg=#f8fafc><b><center>Q1 Sales</center></b></bg>, <bg=#f8fafc><b><center>Q2 Sales</center></b></bg>, <bg=#f8fafc><b><center>Status</center></b></bg>")
    
    # 3. Dynamic Data Rows
    for product, q1, q2, status in db_rows:
        row_str = (
            f"<left>{product}</left>, "
            f"<right>{q1:,}</right>, "
            f"<right>{q2:,}</right>, "
            f"{get_status_cell(status)}"
        )
        expr_lines.append(row_str)
        
    # Join rows with semicolons inside the data() block
    data_content = ";\n        ".join(expr_lines)
    
    # Return complete TenTags IR formula string
    return f'{num_rows},{num_cols},1,"#e2e8f0","solid",0,45, data(\n        {data_content}\n    )'

def main():
    print("[1] Fetching rows from SQLite database (company.db)...")
    db_rows = setup_database_and_get_rows()
    
    print("[2] Building TenTags IR expression from database rows...")
    expr = build_tentags_expression(db_rows)
    print("\nGenerated TenTags IR:")
    print("-" * 65)
    print(expr)
    print("-" * 65 + "\n")
    
    print("[3] Parsing and rendering output to HTML...")
    table_model = tentags.parse(expr)
    html_output = tentags.render_html(table_model)
    
    output_filename = demo_output_path("db_report.html")
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(html_output)
    print(f"Success! HTML report saved as: {output_filename}")

if __name__ == "__main__":
    main()
