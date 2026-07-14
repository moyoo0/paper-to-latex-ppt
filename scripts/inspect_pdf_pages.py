#!/usr/bin/env python3
"""Render PDF pages to images and emit a basic inspection report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def require_fitz():
    try:
        import fitz  # type: ignore
    except ImportError as exc:
        raise SystemExit(
            "Missing dependency: PyMuPDF. Install with `python3 -m pip install pymupdf`."
        ) from exc
    return fitz


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument(
        "--out",
        type=Path,
        help="Output directory. Defaults to the PDF file directory.",
    )
    parser.add_argument("--dpi", type=int, default=220)
    args = parser.parse_args()

    fitz = require_fitz()
    doc = fitz.open(args.pdf)
    out_dir = args.out or args.pdf.parent
    image_dir = out_dir / "page_images"
    image_dir.mkdir(parents=True, exist_ok=True)

    zoom = args.dpi / 72
    matrix = fitz.Matrix(zoom, zoom)
    pages = []
    warnings = []

    for index, page in enumerate(doc, start=1):
        pix = page.get_pixmap(matrix=matrix, alpha=False)
        image_path = image_dir / f"page_{index:03d}.png"
        pix.save(image_path)
        text = page.get_text("text").strip()
        page_warnings = []
        if len(text) < 10:
            page_warnings.append("very little extracted text; check for blank or image-only page")
        if pix.width < 1200 or pix.height < 700:
            page_warnings.append("rendered page is low resolution")
        if page_warnings:
            warnings.append({"page": index, "warnings": page_warnings})
        pages.append(
            {
                "page": index,
                "image": str(image_path),
                "width_px": pix.width,
                "height_px": pix.height,
                "text_chars": len(text),
                "warnings": page_warnings,
            }
        )

    report = {
        "source_pdf": str(args.pdf),
        "dpi": args.dpi,
        "page_count": doc.page_count,
        "pages": pages,
        "warnings": warnings,
        "manual_review_required": True,
        "review_instruction": "Open the rendered page images and revise slides.tex if any page has overflow, unreadable text, bad crops, dense content, or font issues.",
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / "inspection.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {report_path}")
    print(f"Rendered pages: {len(pages)} into {image_dir}")


if __name__ == "__main__":
    main()
