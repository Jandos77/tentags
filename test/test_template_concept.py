import sqlite3
import tentags
from demo_paths import demo_output_path

# Demo database. Replace with your own SQLite file.
conn = sqlite3.connect(demo_output_path("sales.db"))
conn.execute("DROP TABLE IF EXISTS sales")
conn.execute("CREATE TABLE sales (product TEXT, q1_sales INT, q2_sales INT, status TEXT)")
conn.executemany(
    "INSERT INTO sales VALUES (?, ?, ?, ?)",
    [
        ("Laptops", 12000, 15000, "Excellent"),
        ("Smartphones", 22000, 24000, "Excellent"),
        ("Headphones", 3000, 3500, "Good"),
    ]
)
conn.commit()

rows = conn.execute("""
SELECT product, q1_sales, q2_sales, status
FROM sales
""").fetchall()

# Dynamically construct a valid TenTags table definition based on row count
# Rows: Title (1) + Header (1) + Data (len(rows))
total_rows = len(rows) + 2
cols = 4

# Format data rows for TenTags with conditional styling
formatted_rows = []
for product, q1, q2, status in rows:
    if status == "Excellent":
        status_cell = (
            "<bg=#dcfce7>"
            "<color=#166534>"
            f"<b><center>{status}</center></b>"
            "</color></bg>"
        )
    else:
        status_cell = (
            "<bg=#fef3c7>"
            "<color=#92400e>"
            f"<center>{status}</center>"
            "</color></bg>"
        )

    formatted_rows.append(
        f"<left>{product}</left>,"
        f"<right>{q1}</right>,"
        f"<right>{q2}</right>,"
        f"{status_cell}"
    )

# Combine rows with semicolons
data_block = ";\n".join([
    "<fs=14><bg=#1e293b><color=white><b><cm>Electronics Sales Report</cm></b></color></bg></fs>",
    "<bg=#f8fafc><b>Product</b></bg>, <bg=#f8fafc><b>Q1 Sales</b></bg>, <bg=#f8fafc><b>Q2 Sales</b></bg>, <bg=#f8fafc><b>Status</b></bg>",
    *formatted_rows
])

table_definition = f"""{total_rows},{cols},1,"#e2e8f0","solid",0,30, data(
{data_block}
)"""

# Render HTML using the correct API
html = tentags.render(table_definition)

print(html)
