"""Focused tests for the read-only MyST fleet inventory."""

import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "audit-myst-fleet.py"
SPEC = importlib.util.spec_from_file_location("audit_myst_fleet", SCRIPT)
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


class AuditMystFleetTests(unittest.TestCase):
    def test_toc_excludes_binary_exports_and_deduplicates_pages(self):
        config = """project:
  toc:
    - file: index.md
    - file: chapters/ch-01.md
  exports:
    - file: exports/book.pdf
    - file: chapters/ch-01.md
"""
        self.assertEqual(AUDIT.toc_paths(config), ["index.md", "chapters/ch-01.md"])

    def test_page_reports_missing_alternative_text_with_line_numbers(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            page = root / "index.md"
            page.write_text("""# Title
```{figure} image.png
Figure caption.
```
![ ](other.png)
<img src="third.png">
```{figure} accessible.png
:alt: A useful description
```
```{figure} weak.png
:alt: Caption copied from...
```
""", encoding="utf-8")
            report = AUDIT.inspect_page(page, root)
        self.assertEqual(report["findings"], [
            {"line": 2, "kind": "figure-missing-alt"},
            {"line": 5, "kind": "image-missing-alt"},
            {"line": 6, "kind": "html-image-missing-alt"},
            {"line": 11, "kind": "figure-weak-alt"},
        ])


if __name__ == "__main__":
    unittest.main()
