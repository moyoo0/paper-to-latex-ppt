#!/usr/bin/env python3
"""Inject Markdown speaker notes into PPTX speaker-note pages."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape


SLIDE_HEADING_RE = re.compile(r"^\s{0,3}#{1,3}\s*(?:Slide\s*)?(\d+|第?\s*\d+\s*页?)[:：.\s-]*(.*)$", re.I)
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
NOTES_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesSlide"
NOTES_CT = "application/vnd.openxmlformats-officedocument.presentationml.notesSlide+xml"

ET.register_namespace("", REL_NS)
ET.register_namespace("", CT_NS)


def split_notes(markdown: str) -> list[dict]:
    slides: list[dict] = []
    current_title = "Slide 1"
    current_lines: list[str] = []

    for line in markdown.splitlines():
        match = SLIDE_HEADING_RE.match(line)
        if match:
            if current_lines:
                slides.append({"title": current_title, "notes": "\n".join(current_lines).strip()})
                current_lines = []
            number, suffix = match.groups()
            current_title = f"Slide {number.strip()}"
            if suffix.strip():
                current_title += f": {suffix.strip()}"
        else:
            current_lines.append(line)

    if current_lines:
        slides.append({"title": current_title, "notes": "\n".join(current_lines).strip()})
    return slides


def slide_numbers(names: list[str]) -> list[int]:
    numbers = []
    for name in names:
        match = re.fullmatch(r"ppt/slides/slide(\d+)\.xml", name)
        if match:
            numbers.append(int(match.group(1)))
    return sorted(numbers)


def next_rid(root: ET.Element) -> str:
    max_id = 0
    for rel in root:
        rid = rel.attrib.get("Id", "")
        if rid.startswith("rId") and rid[3:].isdigit():
            max_id = max(max_id, int(rid[3:]))
    return f"rId{max_id + 1}"


def ensure_notes_relationship(rels_xml: bytes | None, slide_number: int) -> bytes:
    if rels_xml:
        root = ET.fromstring(rels_xml)
    else:
        root = ET.Element(f"{{{REL_NS}}}Relationships")

    for rel in root.findall(f"{{{REL_NS}}}Relationship"):
        if rel.attrib.get("Type") == NOTES_REL:
            rel.set("Target", f"../notesSlides/notesSlide{slide_number}.xml")
            return ET.tostring(root, encoding="utf-8", xml_declaration=True)

    rel = ET.SubElement(root, f"{{{REL_NS}}}Relationship")
    rel.set("Id", next_rid(root))
    rel.set("Type", NOTES_REL)
    rel.set("Target", f"../notesSlides/notesSlide{slide_number}.xml")
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def ensure_content_types(content_types_xml: bytes, slide_numbers_: list[int]) -> bytes:
    root = ET.fromstring(content_types_xml)
    existing = {
        child.attrib.get("PartName")
        for child in root.findall(f"{{{CT_NS}}}Override")
    }
    for number in slide_numbers_:
        part_name = f"/ppt/notesSlides/notesSlide{number}.xml"
        if part_name not in existing:
            override = ET.SubElement(root, f"{{{CT_NS}}}Override")
            override.set("PartName", part_name)
            override.set("ContentType", NOTES_CT)
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def paragraphs_xml(text: str) -> str:
    lines = [line.rstrip() for line in text.splitlines()]
    paragraphs = []
    for line in lines or [""]:
        if not line.strip():
            paragraphs.append("<a:p/>")
            continue
        paragraphs.append(
            "<a:p>"
            "<a:r>"
            "<a:rPr lang=\"zh-CN\" sz=\"1200\"/>"
            f"<a:t>{escape(line)}</a:t>"
            "</a:r>"
            "</a:p>"
        )
    return "".join(paragraphs)


def notes_slide_xml(slide_number: int, title: str, notes: str) -> bytes:
    body = f"{title}\n\n{notes}".strip()
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:notes xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld>
    <p:spTree>
      <p:nvGrpSpPr>
        <p:cNvPr id="1" name=""/>
        <p:cNvGrpSpPr/>
        <p:nvPr/>
      </p:nvGrpSpPr>
      <p:grpSpPr>
        <a:xfrm>
          <a:off x="0" y="0"/>
          <a:ext cx="0" cy="0"/>
          <a:chOff x="0" y="0"/>
          <a:chExt cx="0" cy="0"/>
        </a:xfrm>
      </p:grpSpPr>
      <p:sp>
        <p:nvSpPr>
          <p:cNvPr id="2" name="Notes Placeholder {slide_number}"/>
          <p:cNvSpPr>
            <a:spLocks noGrp="1"/>
          </p:cNvSpPr>
          <p:nvPr>
            <p:ph type="body" idx="1"/>
          </p:nvPr>
        </p:nvSpPr>
        <p:spPr>
          <a:xfrm>
            <a:off x="685800" y="914400"/>
            <a:ext cx="7772400" cy="4572000"/>
          </a:xfrm>
        </p:spPr>
        <p:txBody>
          <a:bodyPr wrap="square"/>
          <a:lstStyle/>
          {paragraphs_xml(body)}
        </p:txBody>
      </p:sp>
    </p:spTree>
  </p:cSld>
  <p:clrMapOvr>
    <a:masterClrMapping/>
  </p:clrMapOvr>
</p:notes>
""".encode("utf-8")


def inject_notes(pptx: Path, out: Path, slides: list[dict]) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        with zipfile.ZipFile(pptx) as zin:
            zin.extractall(tmp_path)
            names = zin.namelist()

        numbers = slide_numbers(names)
        if not numbers:
            raise SystemExit("No slides found in PPTX.")

        notes_dir = tmp_path / "ppt" / "notesSlides"
        notes_dir.mkdir(parents=True, exist_ok=True)
        rels_dir = tmp_path / "ppt" / "slides" / "_rels"
        rels_dir.mkdir(parents=True, exist_ok=True)

        for index, number in enumerate(numbers, start=1):
            note = slides[index - 1] if index - 1 < len(slides) else {"title": f"Slide {index}", "notes": ""}
            (notes_dir / f"notesSlide{number}.xml").write_bytes(
                notes_slide_xml(number, note["title"], note["notes"])
            )

            rels_path = rels_dir / f"slide{number}.xml.rels"
            rels_xml = rels_path.read_bytes() if rels_path.exists() else None
            rels_path.write_bytes(ensure_notes_relationship(rels_xml, number))

        ct_path = tmp_path / "[Content_Types].xml"
        ct_path.write_bytes(ensure_content_types(ct_path.read_bytes(), numbers))

        out.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as zout:
            for file in sorted(tmp_path.rglob("*")):
                if file.is_file():
                    zout.write(file, file.relative_to(tmp_path).as_posix())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("notes_md", type=Path)
    parser.add_argument("--pptx", type=Path, required=True)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()

    if not args.notes_md.exists():
        raise SystemExit(f"Notes file not found: {args.notes_md}")
    if not args.pptx.exists():
        raise SystemExit(f"PPTX file not found: {args.pptx}")

    markdown = args.notes_md.read_text(encoding="utf-8")
    slides = split_notes(markdown)
    json_path = args.json_out or args.notes_md.with_suffix(".json")
    json_path.write_text(json.dumps({"slides": slides}, ensure_ascii=False, indent=2), encoding="utf-8")

    out = args.out or args.pptx.with_name(args.pptx.stem + "_with_notes.pptx")
    if slides:
        inject_notes(args.pptx, out, slides)
    else:
        shutil.copy2(args.pptx, out)

    print(f"Wrote {json_path}")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
