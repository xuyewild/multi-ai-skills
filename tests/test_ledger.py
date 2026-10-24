import tempfile
import unittest
from pathlib import Path

from helpers import LANGS, run, script


class LedgerTest(unittest.TestCase):
    def run_ledger(self, lang, *args):
        return run(script(lang, "multi-ai-handoff", "ledger.py"), self.path, *args)

    def fresh(self, lang, limit="300", retry="3"):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "ledger.json"
        self.assertEqual(self.run_ledger(lang, "init", "--unit", "credits", "--limit", limit,
                                         "--retry-limit", retry)[0], 0)

    def test_budget(self):
        for lang in LANGS:
            with self.subTest(lang=lang):
                self.fresh(lang)
                self.assertEqual(self.run_ledger(lang, "reserve", "--id", "a1", "--item", "n1", "--cost", "200")[0], 0)
                code, out = self.run_ledger(lang, "reserve", "--id", "a2", "--item", "n2", "--cost", "150")
                self.assertEqual((code, "over budget" in out), (1, True))

    def test_unknown_blocks_reclick(self):
        for lang in LANGS:
            with self.subTest(lang=lang):
                self.fresh(lang)
                self.run_ledger(lang, "reserve", "--id", "a1", "--item", "n1", "--cost", "10")
                self.run_ledger(lang, "unknown", "--id", "a1")
                code, out = self.run_ledger(lang, "reserve", "--id", "a2", "--item", "n1", "--cost", "10", "--kind", "retry")
                self.assertEqual((code, "unknown" in out), (1, True))

    def test_retry_limit_and_human_redo(self):
        for lang in LANGS:
            with self.subTest(lang=lang):
                self.fresh(lang, limit="1000", retry="2")
                for i, kind in enumerate(("first", "retry")):
                    self.run_ledger(lang, "reserve", "--id", f"a{i}", "--item", "n1", "--cost", "10", "--kind", kind)
                    self.run_ledger(lang, "settle", "--id", f"a{i}", "--charge", "10")
                code, out = self.run_ledger(lang, "reserve", "--id", "a9", "--item", "n1", "--cost", "10", "--kind", "autofix")
                self.assertEqual((code, "retry limit" in out), (1, True))
                self.assertEqual(self.run_ledger(lang, "reserve", "--id", "h1", "--item", "n1", "--cost", "10", "--kind", "human")[0], 0)

    def test_init_does_not_overwrite(self):
        for lang in LANGS:
            with self.subTest(lang=lang):
                self.fresh(lang)
                self.assertEqual(self.run_ledger(lang, "init", "--unit", "x", "--limit", "1")[0], 1)


if __name__ == "__main__":
    unittest.main()
