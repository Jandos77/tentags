import tentags
from demo_paths import demo_output_path

def generate_beautiful_demo():

    expr = '''5,4,1,"#e2e8f0","solid",0,50, data(
        <fs=18><bg=#0f172a><color=#ffffff><b><cm>Compare Plans & Core Features, , , </cm></b></color></bg></fs>;
        <bg=#f8fafc><color=#64748b><b><left>Feature</left></b></color></bg>, <bg=#f8fafc><color=#64748b><b><center>Starter</center></b></color></bg>, <bg=#f8fafc><color=#64748b><b><center>Growth</center></b></color></bg>, <bg=#f8fafc><color=#64748b><b><center>Enterprise</center></b></color></bg>;
        <left>API Access</left>, <color=#ef4444><center>✗</center></color>, <color=#22c55e><b><center>✓</center></b></color>, <color=#22c55e><b><center>✓</center></b></color>;
        <left>Custom Domain</left>, <color=#ef4444><center>✗</center></color>, <color=#ef4444><center>✗</center></color>, <color=#22c55e><b><center>✓</center></b></color>;
        <left>Monthly Price</left>, <color=#64748b><center>Free</center></color>, <bg=#e0f2fe><color=#0369a1><b><center>$49/mo</center></b></color></bg>, <bg=#fef9c3><color=#a16207><b><center>Custom</center></b></color></bg>
    )'''

    table_model = tentags.parse(expr)
    output_filename = demo_output_path("beautiful_report.xlsx")
    tentags.render_xlsx(table_model, output_filename)
    print(f"Excel table generated successfully and saved as: {output_filename}")

if __name__ == "__main__":
    generate_beautiful_demo()


