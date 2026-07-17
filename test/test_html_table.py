import tentags
import os

def generate_beautiful_demo():

    expr = '''5,4,1,"#e2e8f0","solid",0,50, data(
        <fs=18><bg=#0f172a><color=#ffffff><b><cm>Compare Plans & Core Features, , , </cm></b></color></bg></fs>;
        <bg=#f8fafc><color=#64748b><b><left>Feature</left></b></color></bg>, <bg=#f8fafc><color=#64748b><b><center>Starter</center></b></color></bg>, <bg=#f8fafc><color=#64748b><b><center>Growth</center></b></color></bg>, <bg=#f8fafc><color=#64748b><b><center>Enterprise</center></b></color></bg>;
        <left>API Access</left>, <color=#ef4444><center>✗</center></color>, <color=#22c55e><b><center>✓</center></b></color>, <color=#22c55e><b><center>✓</center></b></color>;
        <left>Custom Domain</left>, <color=#ef4444><center>✗</center></color>, <color=#ef4444><center>✗</center></color>, <color=#22c55e><b><center>✓</center></b></color>;
        <left>Monthly Price</left>, <color=#64748b><center>Free</center></color>, <bg=#e0f2fe><color=#0369a1><b><center>$49/mo</center></b></color></bg>, <bg=#fef9c3><color=#a16207><b><center>Custom</center></b></color></bg>
    )'''
    
    table_model = tentags.parse(expr)
    html = tentags.render_html(table_model)
    print(html)

    html_table = tentags.render(expr)

    # 2. Put it inside a premium, modern dashboard container template
    beautiful_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TenTags Premium Table Showcase</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-gradient: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
            --card-bg: rgba(255, 255, 255, 0.95);
            --text-main: #0f172a;
            --accent: #6366f1;
            --shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.3);
        }}
        
        body {{
            font-family: 'Plus Jakarta Sans', sans-serif;
            background: var(--bg-gradient);
            color: var(--text-main);
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            overflow-x: hidden;
        }}

        .showcase-container {{
            width: 100%;
            max-width: 900px;
            padding: 40px 20px;
            box-sizing: border-box;
        }}

        .header {{
            text-align: center;
            margin-bottom: 40px;
            color: #ffffff;
        }}

        .header h1 {{
            font-size: 36px;
            font-weight: 700;
            margin: 0 0 12px 0;
            letter-spacing: -0.025em;
            background: linear-gradient(to right, #a5b4fc, #e0e7ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .header p {{
            font-size: 16px;
            color: #94a3b8;
            margin: 0;
        }}

        /* Glassmorphism Card containing the table */
        .table-card {{
            background: var(--card-bg);
            border-radius: 24px;
            padding: 32px;
            box-shadow: var(--shadow);
            border: 1px solid rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(16px);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}

        .table-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 30px 60px -20px rgba(99, 102, 241, 0.25);
        }}

        /* Enhance the rendered table styling to fit modern UI specs */
        table {{
            border-collapse: separate !important;
            border-spacing: 0;
            width: 100%;
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid #e2e8f0 !important;
        }}

        td {{
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-size: 14px !important;
            padding: 14px 20px !important;
            border: 1px solid #e2e8f0 !important;
            transition: background-color 0.2s ease;
        }}

        tr:hover td {{
            background-color: rgba(99, 102, 241, 0.03);
        }}

        /* Footer info */
        .footer {{
            text-align: center;
            margin-top: 30px;
            font-size: 13px;
            color: #64748b;
        }}
        
        .badge {{
            display: inline-block;
            padding: 6px 12px;
            border-radius: 9999px;
            font-size: 12px;
            font-weight: 600;
            background: rgba(99, 102, 241, 0.1);
            color: #6366f1;
            margin-bottom: 16px;
        }}
    </style>
</head>
<body>
    <div class="showcase-container">
        <div class="header">
            <span class="badge">TenTags Engine</span>
            <h1>Beautiful HTML Table Generation</h1>
            <p>A declarative rendering demo featuring custom formatting, merges, and layout styles.</p>
        </div>

        <div class="table-card">
            {html_table}
        </div>

        <div class="footer">
            Generated using TenTags library. File saved as <strong>beautiful_report.html</strong>.
        </div>
    </div>
</body>
</html>"""

    filename = "beautiful_report.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(beautiful_html)
    
    print(f"Success! Beautiful HTML page generated and saved to: {os.path.abspath(filename)}")

if __name__ == "__main__":
    generate_beautiful_demo()
