#!/usr/bin/env python3
"""Extract text, image candidates, captions, and equation-like lines from a paper PDF."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def require_fitz():
    try:
        import fitz  # type: ignore
    except ImportError as exc:
        raise SystemExit(
            "Missing dependency: PyMuPDF. Install with `python3 -m pip install pymupdf`."
        ) from exc
    return fitz


CAPTION_RE = re.compile(r"^\s*(fig(?:ure)?|图|table|表)\s*[\.:：]?\s*\d*", re.I)
EQUATION_HINT_RE = re.compile(
    r"(=|\\sum|\\prod|\\arg|\\min|\\max|\\mathbb|\\mathbf|\\frac|≤|≥|∑|∏|∫|≈|∝)"
)


def clean_line(line: str) -> str:
    return re.sub(r"\s+", " ", line).strip()


def extract_assets(pdf_path: Path, out_dir: Path) -> dict:
    fitz = require_fitz()
    doc = fitz.open(pdf_path)
    figures_dir = out_dir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    pages = []
    figures = []
    captions = []
    equations = []

    for page_index, page in enumerate(doc, start=1):
        text = page.get_text("text")
        lines = [clean_line(line) for line in text.splitlines()]
        lines = [line for line in lines if line]
        pages.append({"page": page_index, "text": text})

        for line_index, line in enumerate(lines):
            if CAPTION_RE.search(line):
                captions.append({"page": page_index, "line": line_index, "text": line})
            if 8 <= len(line) <= 240 and EQUATION_HINT_RE.search(line):
                equations.append({"page": page_index, "line": line_index, "text": line})

        for image_index, image in enumerate(page.get_images(full=True), start=1):
            xref = image[0]
            try:
                pix = fitz.Pixmap(doc, xref)
                if pix.n >= 5:
                    pix = fitz.Pixmap(fitz.csRGB, pix)
                image_name = f"page_{page_index:03d}_img_{image_index:02d}.png"
                image_path = figures_dir / image_name
                pix.save(image_path)
                figures.append(
                    {
                        "page": page_index,
                        "index": image_index,
                        "path": str(image_path),
                        "width": pix.width,
                        "height": pix.height,
                    }
                )
            except Exception as exc:  # pragma: no cover - depends on PDF internals
                figures.append(
                    {
                        "page": page_index,
                        "index": image_index,
                        "error": str(exc),
                    }
                )

    return {
        "source_pdf": str(pdf_path),
        "page_count": doc.page_count,
        "pages": pages,
        "captions": captions,
        "equation_candidates": equations,
        "figures": figures,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--out", type=Path, default=Path("output"))
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    assets = extract_assets(args.pdf, args.out)
    out_file = args.out / "paper_assets.json"
    out_file.write_text(json.dumps(assets, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {out_file}")
    print(f"Pages: {assets['page_count']}; figures: {len(assets['figures'])}; captions: {len(assets['captions'])}; equation candidates: {len(assets['equation_candidates'])}")


if __name__ == "__main__":
    main()
