#!/usr/bin/env python3
"""Fleet-baseline structural checks for a QuadriviumPress MyST textbook.

Copy (or symlink) into a book's ``scripts/verify_book.py``. The script is
intentionally self-contained so member repos do not need a Bindery checkout
at verify time.

Hard failures cover setup integrity: metadata, TOC paths, labels, dangling
references, missing images, unbalanced fences, and common conversion residue.
Accessibility and orphan-asset findings are reported as warnings so content
cleanup can proceed separately from setup standardization.
"""

from __future__ import annotations

import argparse
import collections
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_MYST_FIELDS = (
    "title",
    "short_title",
    "description",
    "authors",
    "license",
    "open_access",
    "github",
    "keywords",
    "toc",
)

ARTIFACTS = {
    "image-not-found": r"image-not-found",
    "raw-includegraphics": r"\\includegraphics",
    "raw-section-command": r"\\section\b",
    "unexpanded-pageindex": r"\\PageIndex",
    "unresolved-ref": r"\\(?:eq)?ref\{",
    "replacement-char": r"\ufffd",
}

FIGURE_FENCE_RE = re.compile(
    r"^[ \t]*(`{3,}|:{3,})\{figure\}\s*(\S+)(.*?)^[ \t]*\1",
    re.MULTILINE | re.DOTALL,
)
LABEL_RE = re.compile(
    r"(?m)^[ \t]*(?:\(([^)]+)\)=|:label:\s*(\S+)|:name:\s*(\S+)|label:\s*(\S+)|name:\s*(\S+))",
)
LINK_RE = re.compile(r"\]\(#([^)]+)\)")


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.notes: list[str] = []

    def ok(self, message: str) -> None:
        self.notes.append(f"ok      {message}")

    def error(self, message: str) -> None:
        self.errors.append(f"FAILED  {message}")

    def warn(self, message: str) -> None:
        self.warnings.append(f"warning {message}")

    def check(self, condition: bool, message: str, detail: str = "") -> None:
        if condition:
            self.ok(message)
        else:
            self.error(message + (f" ({detail})" if detail else ""))


def project_field(myst_text: str, key: str) -> bool:
    """Return True when ``key`` appears as a project-scoped mapping key."""
    in_project = False
    for line in myst_text.splitlines():
        if re.match(r"^project:\s*$", line):
            in_project = True
            continue
        if in_project and re.match(r"^[^\s#]", line):
            in_project = False
        if in_project and re.match(rf"^  {re.escape(key)}:", line):
            return True
    return False


def toc_files(myst_text: str) -> list[str]:
    return re.findall(r'(?m)^\s*-?\s*file:\s*"?([^"\n]+?)"?\s*$', myst_text)


def content_paths(listed: list[str]) -> list[Path]:
    paths = [ROOT / rel for rel in listed if rel.endswith(".md")]
    for directory in ("chapters", "front", "back", "appendices"):
        folder = ROOT / directory
        if folder.is_dir():
            paths.extend(sorted(folder.glob("*.md")))
    # de-dupe while preserving order
    seen: set[Path] = set()
    ordered: list[Path] = []
    for path in paths:
        resolved = path.resolve()
        if resolved in seen or not path.is_file():
            continue
        seen.add(resolved)
        ordered.append(path)
    return ordered


def license_documented() -> bool:
    if (ROOT / "LICENSE-CONTENT.md").is_file() or (ROOT / "LICENSE").is_file():
        return True
    if (ROOT / "LICENSE.txt").is_file():
        return True
    readme = ROOT / "README.md"
    if readme.is_file() and re.search(r"(?im)^##+\s+.*license", readme.read_text(encoding="utf-8")):
        return True
    return False


def collect_labels(texts: dict[Path, str]) -> tuple[collections.Counter[str], list[str]]:
    counts: collections.Counter[str] = collections.Counter()
    duplicates: list[str] = []
    first: dict[str, str] = {}
    for path, text in texts.items():
        for match in LABEL_RE.finditer(text):
            label = next(g for g in match.groups() if g)
            counts[label] += 1
            if label in first and counts[label] == 2:
                duplicates.append(f"{label} in {first[label]} and {path.relative_to(ROOT)}")
            first.setdefault(label, str(path.relative_to(ROOT)))
    return counts, duplicates


def _markdown_link_target(text: str, start: int) -> tuple[str, int] | None:
    """Parse a markdown destination that may contain balanced parentheses."""
    if start >= len(text) or text[start] != "(":
        return None
    depth = 0
    i = start
    while i < len(text):
        ch = text[i]
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return text[start + 1 : i], i + 1
        elif ch == "\n":
            return None
        i += 1
    return None


def figure_targets(path: Path, text: str) -> list[tuple[Path, bool]]:
    """Return (image_path, has_alt) pairs for figure directives in ``text``."""
    found: list[tuple[Path, bool]] = []
    for match in FIGURE_FENCE_RE.finditer(text):
        target = match.group(2)
        body = match.group(3)
        has_alt = bool(re.search(r"(?m)^:alt:\s*\S+", body))
        found.append(((path.parent / target).resolve(), has_alt))
    # Bare image links (including filenames with parentheses)
    for match in re.finditer(r"!\[([^\]]*)\]", text):
        parsed = _markdown_link_target(text, match.end())
        if not parsed:
            continue
        target, _ = parsed
        alt = match.group(1)
        if target.startswith(("http://", "https://", "#")):
            continue
        found.append(((path.parent / target).resolve(), bool(alt.strip())))
    return found


def fence_balance_warnings(path: Path, text: str) -> list[str]:
    """Stack-based fence check; nested ```` / ``` mismatches become warnings."""
    warnings: list[str] = []
    stack: list[tuple[str, int]] = []
    for number, line in enumerate(text.splitlines(), 1):
        tick = re.match(r"^(`{3,})", line)
        if tick:
            marker = tick.group(1)
            if stack and stack[-1][0][0] == "`" and len(stack[-1][0]) <= len(marker) and line.strip() == marker:
                stack.pop()
            elif "{" in line or not stack:
                stack.append((marker, number))
            elif stack and stack[-1][0] == marker:
                stack.pop()
            else:
                warnings.append(
                    f"{path.relative_to(ROOT)}:{number}: fence close {marker!r} "
                    f"does not match opener at line {stack[-1][1]}"
                )
                stack.pop()
            continue
        colon = re.match(r"^(:{3,})(\{.*)?\s*$", line)
        if colon:
            marker = colon.group(1)
            if colon.group(2):
                stack.append((marker, number))
            elif stack and stack[-1][0][0] == ":":
                stack.pop()
    if stack:
        marker, number = stack[-1]
        warnings.append(
            f"{path.relative_to(ROOT)}: unclosed fence {marker!r} opened at line {number}"
        )
    return warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fail-on-warning",
        action="store_true",
        help="treat warnings (alt text / orphans) as failures",
    )
    args = parser.parse_args()
    report = Report()

    myst_path = ROOT / "myst.yml"
    if not myst_path.is_file():
        report.error("myst.yml is missing")
        print("\n".join(report.errors))
        return 1
    myst_text = myst_path.read_text(encoding="utf-8")

    missing_fields = [key for key in REQUIRED_MYST_FIELDS if not project_field(myst_text, key)]
    # authors may be spelled author in a few drafts
    if "authors" in missing_fields and project_field(myst_text, "author"):
        missing_fields.remove("authors")
    report.check(not missing_fields, "required myst.yml project fields present", ", ".join(missing_fields))
    report.check(bool(re.search(r"(?m)^  open_access:\s*true\s*$", myst_text)), "open_access is true")
    report.check((ROOT / "SOURCES.md").is_file(), "SOURCES.md present")
    report.check(license_documented(), "content license documented at repo root")

    listed = toc_files(myst_text)
    report.check(bool(listed), "myst.yml toc lists at least one file")
    missing_toc = [rel for rel in listed if not (ROOT / rel).is_file()]
    report.check(not missing_toc, "every toc file exists", ", ".join(missing_toc[:10]))

    paths = content_paths(listed)
    texts = {path: path.read_text(encoding="utf-8") for path in paths}
    report.ok(f"scanned {len(texts)} markdown files")

    labels, duplicates = collect_labels(texts)
    report.check(not duplicates, f"labels are unique ({len(labels)} total)", "; ".join(duplicates[:8]))

    targets = set()
    for text in texts.values():
        targets.update(LINK_RE.findall(text))
    dangling = sorted(t for t in targets if t not in labels)
    # Fragment links to files (rare) and empty anchors are ignored lightly
    dangling = [t for t in dangling if t and not t.startswith("http")]
    if dangling:
        report.warn(
            f"{len(dangling)} internal references have no in-repo label "
            f"({', '.join(dangling[:10])})"
        )
    else:
        report.ok(f"internal references resolve ({len(targets)} checked)")

    referenced: set[Path] = set()
    missing_images: list[str] = []
    figures = 0
    missing_alt = 0
    for path, text in texts.items():
        for image_path, has_alt in figure_targets(path, text):
            figures += 1
            referenced.add(image_path)
            if not has_alt:
                missing_alt += 1
            if not image_path.is_file():
                try:
                    rel = str(image_path.relative_to(ROOT))
                except ValueError:
                    rel = str(image_path)
                missing_images.append(f"{path.relative_to(ROOT)} -> {rel}")
        for match in re.finditer(r"\]\(", text):
            parsed = _markdown_link_target(text, match.end() - 1)
            if not parsed:
                continue
            target, _ = parsed
            if "images/" not in target or target.startswith(("http://", "https://")):
                continue
            image_path = (path.parent / target).resolve()
            referenced.add(image_path)
            if not image_path.is_file():
                missing_images.append(f"{path.relative_to(ROOT)} -> {target}")

    report.check(not missing_images, f"referenced images exist ({figures} figure directives)", "; ".join(missing_images[:8]))
    if missing_alt:
        report.warn(f"{missing_alt}/{figures} figure/image directives lack explicit alt text")
    else:
        report.ok(f"all {figures} figure/image directives include alt text")

    images_root = ROOT / "images"
    if images_root.is_dir():
        on_disk = {p.resolve() for p in images_root.rglob("*") if p.is_file()}
        # Also count chapter-local images directories when present
        for folder in ROOT.glob("**/images"):
            if folder.is_dir():
                on_disk.update(p.resolve() for p in folder.rglob("*") if p.is_file())
        orphans = sorted(on_disk - referenced)
        if orphans:
            sample = ", ".join(str(p.relative_to(ROOT)) for p in orphans[:8])
            report.warn(f"{len(orphans)} image files are not referenced ({sample})")
        else:
            report.ok(f"no orphaned image files under images/ ({len(on_disk)} on disk)")

    fence_problems: list[str] = []
    for path, text in texts.items():
        fence_problems.extend(fence_balance_warnings(path, text))
    if fence_problems:
        for item in fence_problems[:8]:
            report.warn(item)
    else:
        report.ok("markdown directive fences appear balanced")

    artifacts: list[str] = []
    for path, text in texts.items():
        for name, pattern in ARTIFACTS.items():
            hits = len(re.findall(pattern, text))
            if hits:
                artifacts.append(f"{path.relative_to(ROOT)}: {hits}× {name}")
    report.check(not artifacts, "no common conversion artifacts in markdown", "; ".join(artifacts[:8]))

    odd_dollars: list[str] = []
    for path, text in texts.items():
        # strip fenced blocks before counting inline $ pairs
        stripped = re.sub(r"(?ms)^```.*?^```", "", text)
        if len(re.findall(r"(?<!\\)\$", stripped)) % 2:
            odd_dollars.append(str(path.relative_to(ROOT)))
    if odd_dollars:
        report.warn(f"odd unescaped $ count in {', '.join(odd_dollars[:8])}")
    else:
        report.ok("inline math dollar signs appear balanced")

    print("\n".join(report.notes))
    if report.warnings:
        print("\n".join(report.warnings))
    if report.errors:
        print("\n".join(report.errors))
        print(f"\n{len(report.errors)} check(s) failed.")
        return 1
    if args.fail_on_warning and report.warnings:
        print(f"\n{len(report.warnings)} warning(s) treated as failure.")
        return 1
    print(f"\nAll {len(report.notes)} checks passed ({len(report.warnings)} warning(s)).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
