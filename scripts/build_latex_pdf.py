#!/usr/bin/env python3
"""Compile a LaTeX file into PDF and keep the build log."""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


def find_compiler(engine: str) -> list[str]:
    if engine == "latexmk":
        exe = shutil.which("latexmk")
        if exe:
            return [exe, "-pdf", "-xelatex", "-interaction=nonstopmode", "-halt-on-error"]
    else:
        exe = shutil.which(engine)
        if exe:
            return [exe, "-interaction=nonstopmode", "-halt-on-error"]

    fallback = shutil.which("xelatex")
    if fallback:
        return [fallback, "-interaction=nonstopmode", "-halt-on-error"]
    raise SystemExit("No LaTeX compiler found. Install latexmk or xelatex.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("tex", type=Path)
    parser.add_argument("--out", type=Path, default=Path("output"))
    parser.add_argument("--engine", default="latexmk", choices=["latexmk", "xelatex", "lualatex"])
    parser.add_argument("--passes", type=int, default=2)
    args = parser.parse_args()

    tex = args.tex.resolve()
    if not tex.exists():
        raise SystemExit(f"TeX file not found: {tex}")

    args.out.mkdir(parents=True, exist_ok=True)
    command = find_compiler(args.engine)
    log_path = args.out / "latex_build.log"
    workdir = tex.parent

    runs = 1 if Path(command[0]).name == "latexmk" else max(1, args.passes)
    result = None
    with log_path.open("w", encoding="utf-8", errors="replace") as log:
        for _ in range(runs):
            result = subprocess.run(
                [*command, tex.name],
                cwd=workdir,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            log.write(result.stdout)
            log.write("\n")

    pdf = tex.with_suffix(".pdf")
    target_pdf = args.out / "slides.pdf"
    if result is None or result.returncode != 0 or not pdf.exists():
        raise SystemExit(f"LaTeX build failed. See {log_path}")

    if pdf.resolve() != target_pdf.resolve():
        shutil.copy2(pdf, target_pdf)
    print(f"Wrote {target_pdf}")
    print(f"Build log: {log_path}")


if __name__ == "__main__":
    main()
