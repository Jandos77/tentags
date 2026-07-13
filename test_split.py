import tentags

# 1. Define table parts in separate variables
preamble = '3, 4, 1, #1977ff, solid-1, 1' # 3 rows, 4 columns, border #1977ff with inner grid
style_part = 'style(<bg=white><center><b><cm>Header details, , , </cm></b></center></bg>; <center><bg=white> , , , </bg></center>)'
data_part = 'data(Item, Qty, Price, Total; Wood, 10, 150, 1500; Metal, 5, 300, 1500)'

print("--- Method 1: Assembling into a single expression string (expr) ---")
# Assemble all parts into a single comma-separated string
full_expr = f"{preamble}, {style_part}, {data_part}"
print("Assembled expression:")
print(full_expr)

# Parse and render to HTML
model1 = tentags.parse(full_expr)
html1 = tentags.render_html(model1)
print("\nRender Method 1 result:")
print(html1)


print("\n--- Method 2: Using tentags.compile() ---")
# Pass separate parts directly into the compiler
model2 = tentags.compile(style=style_part, data=data_part, preamble=preamble)
html2 = tentags.render_html(model2)
print("Render Method 2 result:")
print(html2)
