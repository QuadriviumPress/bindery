import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("discovery", Path(__file__).parents[1] / "generate-discovery.py")
discovery = importlib.util.module_from_spec(spec)
spec.loader.exec_module(discovery)


class DiscoveryTests(unittest.TestCase):
    def book(self, name, topics, **extra):
        return dict(name=name, displayName=name, subjectTopics=topics, isBook=True,
                    status="active", deployedUrl=f"https://quadriviumpress.com/{name}/",
                    source=None, description="Open textbook", **extra)

    def test_groups_and_exclusions(self):
        books = [self.book("Music", ["music-theory"]), self.book("Calculus", ["calculus"]),
                 self.book("Waves", ["physics"])]
        draft = self.book("Draft", ["physics"])
        draft["status"] = "draft"
        mirror = self.book("Mirror", [])
        mirror["isBook"] = False
        unpublished = self.book("Unpublished", [])
        unpublished["deployedUrl"] = None
        groups = discovery.grouped_books({"repos": books + [draft, mirror, unpublished]})
        self.assertEqual({key: [b["name"] for b in value] for key, value in groups.items()},
                         {"Mathematics": ["Calculus"], "Physics & Astronomy": ["Waves"], "Music": ["Music"]})

    def test_matching_read_and_source_links_and_escaping(self):
        book = self.book("edition", ["physics"])
        book["displayName"] = "A < B & C"
        book["source"] = {"author": "Author & Co."}
        groups = {"Physics": [book]}
        page = discovery.render_homepage(groups)
        profile = discovery.render_profile(groups)
        self.assertIn("A &lt; B &amp; C", page)
        self.assertIn("Author &amp; Co.", page)
        self.assertIn(book["deployedUrl"], profile)
        self.assertIn("https://github.com/QuadriviumPress/edition", profile)

    def test_preserves_surrounding_page_and_rejects_missing_markers(self):
        text = f"header\n{discovery.START}\nold\n{discovery.END}\nfooter"
        rendered = discovery.START + "\nnew\n" + discovery.END
        result = discovery.replace_catalog(text, rendered)
        self.assertEqual(result, f"header\n{rendered}\nfooter")
        self.assertEqual(discovery.replace_catalog(result, rendered), result)
        with self.assertRaises(ValueError):
            discovery.replace_catalog("no markers", rendered)


if __name__ == "__main__":
    unittest.main()
