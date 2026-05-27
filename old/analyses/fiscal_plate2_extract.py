"""Extract Table 1 ($ bn) and Table 2 (% GDP) from FRT 2025 PDF."""
import pdfplumber

LOCAL = r"C:\Users\jayzh\projects\macro-research-department\data\raw\fiscal\frt_2025.pdf"

pdf = pdfplumber.open(LOCAL)
print("PAGES:", len(pdf.pages))

# Walk every page, dump text for ones mentioning Table 1 or Table 2 headers.
for i, p in enumerate(pdf.pages):
    txt = p.extract_text() or ""
    if "Fiscal transactions" in txt or "Table 1" in txt or "Table 2" in txt or "Budgetary balance" in txt or "per cent of GDP" in txt.lower():
        print(f"\n=== PAGE {i+1} ===\n{txt}\n")
