import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import tentags
from demo_paths import demo_output_path


def build_pdf_financial_report_9x5():
    pytest.importorskip("reportlab")

    preamble = '9,5,1,"#64748b","solid-1",0,28'

    style = """
style(

<bg=#1e3a8a><color=#ffffff><b></b></color></bg>,
<bg=#1e3a8a><color=#ffffff><b></b></color></bg>,
<bg=#1e3a8a><color=#ffffff><b></b></color></bg>,
<bg=#1e3a8a><color=#ffffff><b></b></color></bg>,
<bg=#1e3a8a><color=#ffffff><b></b></color></bg>;

<bg=#f8fafc></bg>,
<bg=#f8fafc></bg>,
<bg=#f8fafc></bg>,
<bg=#f8fafc></bg>,
<bg=#dcfce7><color=#166534><b></b></color></bg>;

<bg=#ffffff></bg>,
<bg=#ffffff></bg>,
<bg=#ffffff></bg>,
<bg=#ffffff></bg>,
<bg=#dcfce7><color=#166534><b></b></color></bg>;

<bg=#f8fafc></bg>,
<bg=#f8fafc></bg>,
<bg=#f8fafc></bg>,
<bg=#f8fafc></bg>,
<bg=#dcfce7><color=#166534><b></b></color></bg>;

<bg=#ffffff></bg>,
<bg=#ffffff></bg>,
<bg=#ffffff></bg>,
<bg=#ffffff></bg>,
<bg=#dcfce7><color=#166534><b></b></color></bg>;

<bg=#f8fafc></bg>,
<bg=#f8fafc></bg>,
<bg=#f8fafc></bg>,
<bg=#f8fafc></bg>,
<bg=#dcfce7><color=#166534><b></b></color></bg>;

<bg=#ffffff></bg>,
<bg=#ffffff></bg>,
<bg=#ffffff></bg>,
<bg=#ffffff></bg>,
<bg=#fef3c7><color=#92400e><b></b></color></bg>;

<bg=#f8fafc></bg>,
<bg=#f8fafc></bg>,
<bg=#f8fafc></bg>,
<bg=#f8fafc></bg>,
<bg=#dbeafe><color=#1d4ed8><b></b></color></bg>;

<bg=#dbeafe><b></b></bg>,
<bg=#dbeafe><b></b></bg>,
<bg=#dbeafe><b></b></bg>,
<bg=#dbeafe><b></b></bg>,
<bg=#dbeafe><b></b></bg>

)
"""

    data = """
data(

<center><b>Period</b></center>,
<center><b>Revenue</b></center>,
<center><b>Expenses</b></center>,
<center><b>Profit</b></center>,
<center><b>Status</b></center>;

January,
<right>125000</right>,
<right>82000</right>,
<right><color=#15803d><b>43000</b></color></right>,
<center>Closed</center>;

February,
<right>132500</right>,
<right>87500</right>,
<right><color=#15803d><b>45000</b></color></right>,
<center>Closed</center>;

March,
<right>141200</right>,
<right>91300</right>,
<right><color=#15803d><b>49900</b></color></right>,
<center>Closed</center>;

April,
<right>138000</right>,
<right>94500</right>,
<right><color=#15803d><b>43500</b></color></right>,
<center>Closed</center>;

May,
<right>152400</right>,
<right>98200</right>,
<right><color=#15803d><b>54200</b></color></right>,
<center>Closed</center>;

June,
<right>160750</right>,
<right>104300</right>,
<right><color=#15803d><b>56450</b></color></right>,
<center>Review</center>;

July,
<right>158900</right>,
<right>109100</right>,
<right><color=#15803d><b>49800</b></color></right>,
<center>Review</center>;

August,
<right>171300</right>,
<right>112800</right>,
<right><color=#15803d><b>58500</b></color></right>,
<center>Forecast</center>

)
"""

    model = tentags.compile(preamble, style, data)

    assert model.rows == 9
    assert model.cols == 5
    assert model.cells[0][0].raw_expr == "Period"
    assert model.cells[8][4].raw_expr == "Forecast"

    output = demo_output_path("financial_report_9x5.pdf")
    if output.exists():
        output.unlink()

    tentags.render_pdf(model, str(output))

    pdf_data = output.read_bytes()
    assert pdf_data.startswith(b"%PDF")
    assert len(pdf_data) > 1000
    return output


def test_pdf_financial_report_9x5():
    build_pdf_financial_report_9x5()


if __name__ == "__main__":
    pdf_path = build_pdf_financial_report_9x5()
    print(f"PDF created: {pdf_path}")
