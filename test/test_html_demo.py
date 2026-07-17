import tentags

def run_demo():
    # ANSI escape codes for beautiful terminal output formatting
    GREEN = "\033[92m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"
    RESET = "\033[0m"
    BOLD = "\033[1m"

    print(f"{BOLD}{BLUE}=================================================={RESET}")
    print(f"{BOLD}{BLUE}     TenTags HTML Generation & Rendering Demo     {RESET}")
    print(f"{BOLD}{BLUE}=================================================={RESET}\n")

    # 1. Define a beautiful table structure using TenTags syntax
    # Features: Column merge (<cm>), custom colors, alignment, and styling tags
    expr = '''3,4,1,"#475569","solid",0,45, data(
        <fs=16><bg=#0f172a><color=#f8fafc><b><cm>Plan & Pricing Matrix, , , </cm></b></color></bg></fs>;
        <bg=#f1f5f9><b><left>Features</left></b></bg>, <bg=#f1f5f9><b><center>Basic</center></b></bg>, <bg=#f1f5f9><b><center>Pro</center></b></bg>, <bg=#f1f5f9><b><center>Enterprise</center></b></bg>;
        <left>Monthly Price</left>, <color=#475569><center>Free</center></color>, <color=#2563eb><b><center>$19</center></b></color>, <bg=#fef08a><color=#a16207><b><center>Custom</center></b></color></bg>
    )'''

    print(f"{CYAN}[1] Source Expression:{RESET}")
    print(f"--------------------------------------------------")
    print(expr.strip())
    print(f"--------------------------------------------------\n")

    # 2. Render to HTML
    print(f"{CYAN}[2] Rendering to HTML...{RESET}")
    html_output = tentags.render(expr)
    
    # 3. Print HTML with a beautiful, formatted view
    print(f"\n{GREEN}✔ HTML generated successfully!{RESET}")
    print(f"\n{CYAN}[3] Output HTML Code Preview:{RESET}")
    print(f"--------------------------------------------------")
    # Pretty-print by breaking at tags to make it readable in console
    formatted_html = html_output.replace("><tr", ">\n  <tr").replace("><td", "\n    <td").replace("></tr>", "\n  </tr>").replace("></table>", "\n</table>")
    print(formatted_html)
    print(f"--------------------------------------------------\n")

    # 4. Save to file for manual viewing
    filename = "demo_output.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>TenTags Demo</title>
    <style>
        body {{
            font-family: system-ui, -apple-system, sans-serif;
            padding: 40px;
            background-color: #f8fafc;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 80vh;
        }}
    </style>
</head>
<body>
    {html_output}
</body>
</html>""")

    print(f"{MAGENTA}💾 Saved full preview page to:{RESET} {BOLD}{filename}{RESET}")
    print(f"\n{BOLD}{BLUE}=================================================={RESET}")

if __name__ == "__main__":
    run_demo()
