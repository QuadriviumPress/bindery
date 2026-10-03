#!/usr/bin/env python3
"""Read-only inventory of the active MyST books in the local fleet checkout.

Usage: python3 scripts/audit-myst-fleet.py [--root WORKSPACE] [--json] [--book NAME]
The output is evidence for editorial review, not a substitute for reading pages.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


CONTENT_DIRS = ("chapters", "content", "experiments", "front", "back", "appendices")
TOC_FILE = re.compile(r"(?m)^\s*-?\s*file:\s*['\"]?([^'\"\n#]+?)['\"]?\s*$")
FIGURE_OPEN = re.compile(r"^\s*(`{3,}|:{3,})\{figure\}\s+(\S+)")
MARKDOWN_IMAGE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
HTML_IMAGE = re.compile(r"<img\b[^>]*>", re.IGNORECASE)
ROLE = re.compile(r"\{(exercise|solution|prf:example|note|important|tip|warning)\}")
WORD = re.compile(r"\b[\w]+(?:[’'-][\w]+)*\b", re.UNICODE)


def toc_paths(config: str) -> list[str]:
    # MyST's TOC uses `file` entries; keep order and exclude external URLs.
    return list(dict.fromkeys(
        match.group(1).strip() for match in TOC_FILE.finditer(config)
        if match.group(1).strip().endswith((".md", ".myst", ".ipynb"))
    ))


def inspect_page(path: Path, root: Path) -> dict:
    lines = path.read_text(encoding="utf-8").splitlines()
    findings: list[dict] = []
    roles: dict[str, int] = {}
    in_figure = False
    figure_fence = ""
    figure_line = 0
    figure_alt = False
    for number, line in enumerate(lines, 1):
        for role in ROLE.findall(line):
            roles[role] = roles.get(role, 0) + 1
        if not in_figure:
            match = FIGURE_OPEN.match(line)
            if match:
                in_figure = True
                figure_fence = match.group(1)
                figure_line = number
                figure_alt = False
        elif line.strip() == figure_fence:
            if not figure_alt:
                findings.append({"line": figure_line, "kind": "figure-missing-alt"})
            in_figure = False
        elif match := re.match(r"^\s*:alt:\s*(\S.*)", line):
            figure_alt = True
            alt = match.group(1).strip()
            if alt.endswith("...") or alt.casefold() in {"image", "figure", "image of the figure"}:
                findings.append({"line": number, "kind": "figure-weak-alt"})
        for match in MARKDOWN_IMAGE.finditer(line):
            if not match.group(1).strip():
                findings.append({"line": number, "kind": "image-missing-alt"})
        for match in HTML_IMAGE.finditer(line):
            if not re.search(r"\balt\s*=", match.group(0), re.IGNORECASE):
                findings.append({"line": number, "kind": "html-image-missing-alt"})
    if in_figure:
        findings.append({"line": figure_line, "kind": "unclosed-figure"})
    content = "\n".join(lines)
    return {
        "path": str(path.relative_to(root)),
        "lines": len(lines),
        "approx_words": len(WORD.findall(content)),
        "roles": roles,
        "findings": findings,
    }


def inspect_book(root: Path, name: str) -> dict:
    book = root / name
    config = (book / "myst.yml").read_text(encoding="utf-8")
    paths = toc_paths(config)
    pages = [inspect_page(book / path, book) for path in paths if (book / path).is_file()]
    missing = [path for path in paths if not (book / path).is_file()]
    source_files = {str(p.relative_to(book)) for directory in CONTENT_DIRS
                    for p in (book / directory).rglob("*.md") if p.is_file()}
    pkg = json.loads((book / "package.json").read_text(encoding="utf-8"))
    scripts = pkg.get("scripts", {})
    capabilities = {
        "pdf": "build:pdf" in scripts or "pdf" in scripts,
        "docx": "build:docx" in scripts or "docx" in scripts,
        "h5p": any(key.startswith("h5p:") for key in scripts),
        "audio": any(key.startswith("audio:") for key in scripts),
        "notation": any(key.startswith("notation:") for key in scripts),
        "execution": "--execute" in scripts.get("check", ""),
    }
    return {
        "book": name,
        "toc_pages": len(paths),
        "existing_pages": len(pages),
        "approx_words": sum(p["approx_words"] for p in pages),
        "missing_toc_files": missing,
        "unlisted_content_files": sorted(source_files.difference(paths)),
        "capabilities": capabilities,
        "roles": {key: sum(p["roles"].get(key, 0) for p in pages)
                  for key in ("exercise", "solution", "prf:example", "note", "important", "tip", "warning")},
        "findings": [{"path": p["path"], **finding} for p in pages for finding in p["findings"]],
        "pages": pages,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--book", help="Inventory only one active MyST book")
    parser.add_argument("--json", action="store_true", help="Print detailed JSON")
    args = parser.parse_args()
    catalog = json.loads((args.root / "bindery/structure/repos.json").read_text(encoding="utf-8"))
    names = [entry["name"] for entry in catalog["repos"] if entry.get("format") == "myst"
             and entry.get("isBook") is True and entry.get("status") == "active"]
    if args.book:
        if args.book not in names:
            parser.error(f"not an active MyST book: {args.book}")
        names = [args.book]
    books = [inspect_book(args.root, name) for name in names]
    if args.json:
        print(json.dumps({"books": books}, indent=2))
        return
    print("| Book | Pages | Approx. words | Alt findings | Unlisted files | PDF | DOCX | H5P |")
    print("| --- | ---: | ---: | ---: | ---: | :---: | :---: | :---: |")
    for book in books:
        cap = book["capabilities"]
        print(f"| {book['book']} | {book['existing_pages']}/{book['toc_pages']} | "
              f"{book['approx_words']:,} | {len(book['findings'])} | "
              f"{len(book['unlisted_content_files'])} | "
              f"{'✓' if cap['pdf'] else '—'} | {'✓' if cap['docx'] else '—'} | "
              f"{'✓' if cap['h5p'] else '—'} |")


if __name__ == "__main__":
    main()
