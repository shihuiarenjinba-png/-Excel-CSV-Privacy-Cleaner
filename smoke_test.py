from pathlib import Path
import tempfile
from openpyxl import Workbook, load_workbook

from windows_app import clean_csv, clean_xlsx

with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    csv_src = root / "sample.csv"
    csv_src.write_text("name,email\nAlice,alice@example.com\n", encoding="utf-8")
    csv_out = root / "safe.csv"
    clean_csv(csv_src, csv_out, {"email"}, "mask", "salt")
    text = csv_out.read_text(encoding="utf-8-sig")
    assert "alice@example.com" not in text

    xlsx_src = root / "sample.xlsx"
    wb = Workbook()
    ws = wb.active
    ws.append(["name", "email"])
    ws.append(["Alice", "alice@example.com"])
    hidden = wb.create_sheet("Hidden")
    hidden.sheet_state = "hidden"
    wb.save(xlsx_src)

    xlsx_out = root / "safe.xlsx"
    clean_xlsx(xlsx_src, xlsx_out, {"email"}, "pseudonymize", "salt", True, True)
    out_wb = load_workbook(xlsx_out)
    assert "Hidden" not in out_wb.sheetnames
    assert out_wb.active["B2"].value != "alice@example.com"
print("Excel CSV Privacy Cleaner smoke test: OK")
