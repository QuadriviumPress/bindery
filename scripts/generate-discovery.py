#!/usr/bin/env python3
"""Refresh the fleet homepage and GitHub profile from the repository catalog.

Run from a fleet checkout; --check reports drift without writing files.
"""
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

START = "<!-- BEGIN GENERATED CATALOG -->"
END = "<!-- END GENERATED CATALOG -->"


def grouped_books(catalog: dict) -> dict[str, list[dict]]:
    groups: dict[str, list[dict]] = {"Mathematics": [], "Physics & Astronomy": [], "Music": []}
    for book in catalog["repos"]:
        if not (book["isBook"] and book["status"] == "active" and book["deployedUrl"]):
            continue
        topics = book["subjectTopics"]
        if any(topic.startswith("music") for topic in topics):
            group = "Music"
        elif any(topic in {"mathematics", "math", "calculus", "trigonometry", "differential-equations", "vector-calculus"} for topic in topics):
            group = "Mathematics"
        else:
            group = "Physics & Astronomy"
        groups[group].append(book)
    return {group: sorted(books, key=lambda b: b["displayName"].casefold())
            for group, books in groups.items() if books}


def markdown_text(text: str) -> str:
    return text.replace("\\", "\\\\").replace("[", "\\[").replace("]", "\\]").replace("*", "\\*").replace("_", "\\_")


def render_profile(groups: dict[str, list[dict]]) -> str:
    lines = [START, "", "## Catalog", "",
             "[Browse all books](https://quadriviumpress.com/#catalog) · [Catalog and attribution](https://quadriviumpress.com/bindery/)", ""]
    for group, books in groups.items():
        lines += [f"### {group}", ""]
        for book in books:
            source = book["source"]
            author = f" — {markdown_text(source['author'])}" if source else ""
            lines.append(f"- **[{markdown_text(book['displayName'])}]({book['deployedUrl']})**{author}. "
                         f"[Source](https://github.com/QuadriviumPress/{book['name']})")
        lines.append("")
    return "\n".join(lines + [END])


def render_homepage(groups: dict[str, list[dict]]) -> str:
    lines = [START]
    for group, books in groups.items():
        lines += ['      <div class="group">', f"        <h3>{html.escape(group)}</h3>", '        <ul class="books">']
        for book in books:
            source = book["source"]
            blurb = source["author"] if source else book["description"]
            lines += ['          <li>', f'            <a href="{html.escape(book["deployedUrl"], quote=True)}">',
                      f'              <span class="title">{html.escape(book["displayName"])}</span>',
                      f'              <span class="blurb">{html.escape(blurb)}</span>',
                      '            </a>', '          </li>']
        lines += ['        </ul>', '      </div>', '']
    return "\n".join(lines + [END])


def replace_catalog(text: str, rendered: str) -> str:
    if text.count(START) != 1 or text.count(END) != 1:
        raise ValueError("expected exactly one generated catalog marker pair")
    before, rest = text.split(START)
    _, after = rest.split(END)
    return before + rendered + after


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--catalog", type=Path, default=Path(__file__).resolve().parents[1] / "structure/repos.json")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    groups = grouped_books(json.loads(args.catalog.read_text()))
    targets = [(args.workspace / ".github/profile/README.md", render_profile(groups)),
               (args.workspace / "QuadriviumPress.github.io/index.html", render_homepage(groups))]
    # Validate both targets before writing either one.
    updates = [(path, replace_catalog(path.read_text(), rendered)) for path, rendered in targets]
    stale = False
    for path, updated in updates:
        if updated == path.read_text():
            continue
        stale = True
        if args.check:
            print(f"STALE: {path}")
        else:
            path.write_text(updated)
            print(f"Updated {path}")
    return int(args.check and stale)


if __name__ == "__main__":
    raise SystemExit(main())
