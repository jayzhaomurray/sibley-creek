"""Convert a markdown file to PDF using Python-Markdown + Chrome headless."""
import subprocess
import sys
from pathlib import Path
import markdown

if len(sys.argv) != 3:
    print("Usage: py _md_to_pdf.py <input.md> <output.pdf>")
    sys.exit(1)

md_path = Path(sys.argv[1]).resolve()
pdf_path = Path(sys.argv[2]).resolve()
html_path = pdf_path.with_suffix(".html")

md_text = md_path.read_text(encoding="utf-8")
html_body = markdown.markdown(md_text, extensions=["tables", "fenced_code", "toc"])

css = """
@page { size: Letter; margin: 0.75in; }
body { font-family: Georgia, 'Times New Roman', serif; font-size: 11pt; line-height: 1.5; color: #1a1a1a; max-width: 7in; }
h1 { font-size: 22pt; margin-top: 0; border-bottom: 2px solid #1a1a1a; padding-bottom: 6pt; }
h2 { font-size: 16pt; margin-top: 24pt; border-bottom: 1px solid #888; padding-bottom: 3pt; }
h3 { font-size: 13pt; margin-top: 18pt; }
h4 { font-size: 11pt; margin-top: 12pt; font-weight: bold; }
p { margin: 6pt 0; }
ul, ol { margin: 6pt 0; padding-left: 24pt; }
li { margin: 3pt 0; }
strong { font-weight: bold; }
em { font-style: italic; }
table { border-collapse: collapse; margin: 12pt 0; font-size: 10pt; width: 100%; }
th, td { border: 1px solid #888; padding: 4pt 8pt; text-align: left; vertical-align: top; }
th { background-color: #eaeaea; font-weight: bold; }
code { font-family: 'Consolas', 'Courier New', monospace; background-color: #f4f4f4; padding: 1pt 3pt; font-size: 9.5pt; }
pre { background-color: #f4f4f4; padding: 8pt; border-radius: 3pt; overflow-x: auto; font-size: 9.5pt; }
blockquote { border-left: 3px solid #888; padding-left: 12pt; color: #444; margin: 12pt 0; font-style: italic; }
hr { border: 0; border-top: 1px solid #ccc; margin: 18pt 0; }
a { color: #1a1a1a; text-decoration: underline; }
"""

html_full = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>{md_path.stem}</title><style>{css}</style></head>
<body>{html_body}</body></html>"""

html_path.write_text(html_full, encoding="utf-8")

chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
cmd = [
    chrome_path,
    "--headless",
    "--disable-gpu",
    "--no-pdf-header-footer",
    f"--print-to-pdf={pdf_path}",
    f"file:///{html_path.as_posix()}",
]
result = subprocess.run(cmd, capture_output=True, text=True)
if result.returncode != 0:
    print("Chrome stderr:", result.stderr)
    sys.exit(result.returncode)
print(f"PDF written: {pdf_path}")
