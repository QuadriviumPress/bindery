import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "lib" / "proofread.py"
SPEC = importlib.util.spec_from_file_location("proofread", MODULE_PATH)
assert SPEC and SPEC.loader
proofread = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = proofread
SPEC.loader.exec_module(proofread)


class ContentDiscoveryTests(unittest.TestCase):
    def test_myst_toc_includes_root_and_unusual_dirs_only_when_referenced(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "modernPhysicsLab"
            (repo / "front-matter").mkdir(parents=True)
            (repo / "experiments").mkdir()
            (repo / "instructor").mkdir()
            (repo / "index.md").write_text("Index\n", encoding="utf-8")
            (repo / "front-matter" / "safety.md").write_text("Safety\n", encoding="utf-8")
            (repo / "experiments" / "exp-01.md").write_text("Experiment\n", encoding="utf-8")
            (repo / "instructor" / "notes.md").write_text("Private\n", encoding="utf-8")
            (repo / "myst.yml").write_text(
                "project:\n"
                "  toc:\n"
                "    - file: index.md\n"
                "    - file: front-matter/safety\n"
                "    - file: experiments/exp-01.md  # student handout\n",
                encoding="utf-8",
            )

            paths = {
                path.relative_to(repo).as_posix()
                for path in proofread.iter_content_files(repo)
            }

            self.assertEqual(
                paths,
                {"index.md", "front-matter/safety.md", "experiments/exp-01.md"},
            )

    def test_differential_equations_uses_only_edition_of_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "differentialEquations"
            source = repo / "trench-distro"
            source.mkdir(parents=True)
            for name in (
                "main.tex",
                "TRENCH_DIFFEQ.tex",
                "TRENCH_DIFFEQ_STUDENT_MANUAL.tex",
                "TRENCH_DIFFEQ_BV.tex",
            ):
                (source / name).write_text(name, encoding="utf-8")

            paths = [
                path.relative_to(repo).as_posix()
                for path in proofread.iter_content_files(repo)
            ]

            self.assertEqual(paths, ["trench-distro/TRENCH_DIFFEQ_BV.tex"])

    def test_conventional_roots_remain_supported_and_deduplicated(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "ordinaryBook"
            (repo / "chapters").mkdir(parents=True)
            chapter = repo / "chapters" / "one.md"
            chapter.write_text("Chapter\n", encoding="utf-8")
            (repo / "myst.yml").write_text(
                "project:\n  toc:\n    - file: chapters/one.md\n",
                encoding="utf-8",
            )

            self.assertEqual(proofread.iter_content_files(repo), [chapter])


class QueueRefreshTests(unittest.TestCase):
    def test_init_requeues_unchanged_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            fleet = Path(tmp)
            repo = fleet / "book"
            state_dir = fleet / ".proofread"
            (repo / ".git").mkdir(parents=True)
            (repo / "chapters").mkdir()
            chapter = repo / "chapters" / "one.md"
            chapter.write_text("Chapter\n", encoding="utf-8")

            catalog = fleet / "repos.json"
            catalog.write_text(
                '{"repos": [{"name": "book", "isBook": true}]}\n',
                encoding="utf-8",
            )
            settings = proofread.Settings(state_dir=state_dir)

            old_fleet_root = proofread.FLEET_ROOT
            old_catalog = proofread.CATALOG
            try:
                proofread.FLEET_ROOT = fleet
                proofread.CATALOG = catalog
                self.assertEqual(proofread.cmd_init(settings), 0)
                state = proofread.ProofreadState(settings)
                queue = state.load_queue()
                queue["jobs"][0]["status"] = "error"
                queue["jobs"][0]["attempts"] = 1
                state.save_queue(queue)

                self.assertEqual(proofread.cmd_init(settings), 0)
                retried = state.load_queue()["jobs"][0]
            finally:
                proofread.FLEET_ROOT = old_fleet_root
                proofread.CATALOG = old_catalog

            self.assertEqual(retried["status"], "pending")
            self.assertEqual(retried["attempts"], 1)


class PacingTests(unittest.TestCase):
    def test_default_budget_is_uncapped(self):
        with tempfile.TemporaryDirectory() as tmp:
            settings = proofread.Settings(state_dir=Path(tmp))
            state = proofread.ProofreadState(settings)
            self.assertEqual(settings.daily_budget_s, 0)
            self.assertEqual(settings.delay_min_s, 0)
            self.assertEqual(settings.delay_max_s, 5)
            self.assertEqual(settings.chunk_chars, 64_000)
            self.assertFalse(proofread.budget_blocks(settings, state))
            self.assertEqual(state.remaining_budget(), float("inf"))

    def test_configured_budget_still_blocks_near_the_cap(self):
        with tempfile.TemporaryDirectory() as tmp:
            settings = proofread.Settings(
                state_dir=Path(tmp),
                daily_budget_s=120,
            )
            state = proofread.ProofreadState(settings)
            self.assertFalse(proofread.budget_blocks(settings, state))
            state.add_active_time(90, "job")
            self.assertTrue(proofread.budget_blocks(settings, state))
            self.assertEqual(state.remaining_budget(), 30)


if __name__ == "__main__":
    unittest.main()
