import tempfile
import unittest
from pathlib import Path

from helpers import LANGS, run, script

PASS = "# Review\n- Verdict: PASS\n"
REVISE = "# 复核\n- 结论：REVISE\n- 问题：……\n"


class ReviewGateTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)
        (self.d / "product.md").write_text("v1\n", encoding="utf-8")
        (self.d / "table.md").write_text("| a | 1 |\n| b | 2 |\n", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def report(self, text):
        p = self.d / "r.md"
        p.write_text(text, encoding="utf-8")
        return p

    def gate(self, lang, *args):
        return run(script(lang, "multi-ai-handoff", "review_gate.py"), *args, cwd=self.d)

    def record(self, lang, text, mode="independent", basis=()):
        return self.gate(lang, "record", "--stage", "s", "--dir", "rev", "--report", self.report(text),
                         "--product", "product.md", "--basis", *basis, "--mode", mode)

    def check(self, lang, *extra):
        return self.gate(lang, "check", "--stage", "s", "--dir", "rev", *extra)

    def test_missing_then_pass_then_stale(self):
        for lang in LANGS:
            with self.subTest(lang=lang):
                self.setUp()
                code, out = self.check(lang, "--from-record")
                self.assertEqual((code, "MISSING" in out), (1, True))
                self.assertEqual(self.record(lang, PASS)[0], 0)
                code, out = self.check(lang, "--product", "product.md")
                self.assertEqual((code, "PASS" in out), (0, True))
                (self.d / "product.md").write_text("v2\n", encoding="utf-8")
                code, out = self.check(lang, "--from-record")
                self.assertEqual((code, "STALE" in out), (1, True))

    def test_self_review_does_not_release(self):
        for lang in LANGS:
            with self.subTest(lang=lang):
                self.setUp()
                self.record(lang, PASS, mode="self")
                code, out = self.check(lang, "--from-record")
                self.assertEqual((code, "SELF_REVIEW" in out), (1, True))

    def test_revise_limit(self):
        for lang in LANGS:
            with self.subTest(lang=lang):
                self.setUp()
                for _ in range(3):
                    self.record(lang, REVISE)
                code, out = self.check(lang, "--from-record")
                self.assertEqual((code, "LIMIT" in out), (1, True))

    def test_unparseable(self):
        for lang in LANGS:
            with self.subTest(lang=lang):
                self.setUp()
                self.record(lang, "- Verdict: PASS\n- Verdict: REVISE\n")
                code, out = self.check(lang, "--from-record")
                self.assertEqual((code, "UNPARSEABLE" in out), (1, True))

    def test_ruling_releases(self):
        for lang in LANGS:
            with self.subTest(lang=lang):
                self.setUp()
                self.record(lang, REVISE)
                code, _ = self.gate(lang, "ruling", "--stage", "s", "--dir", "rev", "--quote", "keep it",
                                    "--source", "chat", "--product", "product.md")
                self.assertEqual(code, 0)
                code, out = self.check(lang, "--from-record")
                self.assertEqual((code, "RULED" in out), (0, True))

    def test_keyword_hash_ignores_unrelated_rows(self):
        for lang in LANGS:
            with self.subTest(lang=lang):
                self.setUp()
                self.record(lang, PASS, basis=("table.md#a",))
                (self.d / "table.md").write_text("| a | 1 |\n| b | 3 |\n", encoding="utf-8")
                self.assertEqual(self.check(lang, "--from-record")[0], 0)
                (self.d / "table.md").write_text("| a | 9 |\n| b | 3 |\n", encoding="utf-8")
                self.assertEqual(self.check(lang, "--from-record")[0], 1)


if __name__ == "__main__":
    unittest.main()
