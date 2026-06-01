"""
render_commentary_pages.py

Renders PDF pages 1 and 2 to PNG using PyMuPDF (fitz).
Produces the showcase assets consumed by the splash commentary perspective stack.

Usage:
    python scripts/render_commentary_pages.py <pdf-path> <slug>

Output:
    public/showcase/commentary-<slug>-cover.png  (page 1)
    public/showcase/commentary-<slug>-page2.png  (page 2)

DPI target: 144 dpi — matches the retail-march-2026 reference pair
(1224x1584 for a letter-size page: 8.5in * 144 = 1224, 11in * 144 = 1584).
"""

import sys
import os
import fitz  # PyMuPDF


def render_page(doc, page_index, out_path, dpi=144):
    page = doc.load_page(page_index)
    mat = fitz.Matrix(dpi / 72, dpi / 72)
    pix = page.get_pixmap(matrix=mat, colorspace=fitz.csRGB, alpha=False)
    pix.save(out_path)
    print(f"  wrote {out_path} ({pix.width}x{pix.height})")


def main():
    if len(sys.argv) != 3:
        print("usage: python scripts/render_commentary_pages.py <pdf-path> <slug>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    slug = sys.argv[2]

    if not os.path.exists(pdf_path):
        print(f"ERROR: PDF not found: {pdf_path}")
        sys.exit(1)

    # Derive output dir relative to script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    showcase_dir = os.path.join(project_root, "public", "showcase")

    cover_out = os.path.join(showcase_dir, f"commentary-{slug}-cover.png")
    page2_out = os.path.join(showcase_dir, f"commentary-{slug}-page2.png")

    doc = fitz.open(pdf_path)
    n = doc.page_count
    print(f"[render] PDF: {pdf_path}")
    print(f"[render] Pages: {n}")

    if n < 1:
        print("ERROR: PDF has no pages")
        sys.exit(1)

    print("[render] Rendering page 1 (cover)...")
    render_page(doc, 0, cover_out)

    if n >= 2:
        print("[render] Rendering page 2...")
        render_page(doc, 1, page2_out)
    else:
        print("WARNING: PDF only has 1 page — copying cover to page2 slot")
        import shutil
        shutil.copy(cover_out, page2_out)
        print(f"  copied {page2_out}")

    doc.close()
    print("[render] Done.")


if __name__ == "__main__":
    main()
