import tempfile
import unittest
from pathlib import Path

from helpers import LANGS, ROOT, run, script

ZH = """## 优先序
负责人最新原话 > skill 默认
| 编号 | 规则 | 原话 | 出处 | 日期 | 状态 | 替代 | 落地位置 |
|---|---|---|---|---|---|---|---|
| R001 | a \\| b | “x” | 对话 | 2026-01-01 | 已替代 | R002 | 跑法.md |
| R002 | c | “y” | 决策卡 | 2026-01-02 | **现行** | — | 跑法.md |
"""
EN = """## Priority
owner > skill default
| ID | Rule | Quote | Source | Date | Status | Replaced by | Where it lives |
|---|---|---|---|---|---|---|---|
| R001 | a | "x" | chat | 2026-01-01 | replaced | R002 | run-mode.md |
| R002 | b | "y" | card | 2026-01-02 | active | — | run-mode.md |
"""
BAD = """## Priority
| ID | Rule | Quote | Source | Date | Status | Replaced by | Where it lives |
|---|---|---|---|---|---|---|---|
| R001 | a | "x" | chat | 2026-01-01 | replaced | R009 | - |
| R002 | b | — | card | 2026-01-02 | active | — | - |
| R002 | c | "z" | card | 2026-01-02 | dropped | — | - |
"""


class CheckProjectTest(unittest.TestCase):
    def project(self, shared, ledger_name, text):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        (root / shared).mkdir()
        (root / shared / ledger_name).write_text(text, encoding="utf-8")
        return root

    def check(self, lang, root, *args):
        return run(script(lang, "project-memory", "check_project.py"), "--project", root, *args)

    def test_good_ledgers(self):
        for lang in LANGS:
            for shared, name, text in (("00_项目", "规则台账.md", ZH), ("00_project", "rule-ledger.md", EN)):
                with self.subTest(lang=lang, layout=shared):
                    code, out = self.check(lang, self.project(shared, name, text))
                    self.assertEqual(code, 0, out)

    def test_bad_ledger(self):
        for lang in LANGS:
            with self.subTest(lang=lang):
                root = self.project("00_project", "rule-ledger.md", BAD)
                (root / "00_project" / "progress-summary.md").write_bytes(b"")
                (root / "00_project" / "broken.md").write_bytes(b"\xff\xfe")
                code, out = self.check(lang, root)
                self.assertEqual(code, 1)
                for needle in ("R009", "duplicate id R002", "without quote", "dropped", "empty file", "not UTF-8"):
                    self.assertIn(needle, out)

    def test_no_shared_folder(self):
        for lang in LANGS:
            with self.subTest(lang=lang):
                with tempfile.TemporaryDirectory() as d:
                    self.assertEqual(self.check(lang, d)[0], 2)

    def test_templates_pass(self):
        for lang, shared, name in (("zh", "00_项目", "规则台账.md"), ("en", "00_project", "rule-ledger.md")):
            with self.subTest(lang=lang):
                tpl = ROOT / "skills" / lang / "project-memory" / "templates" / "rule-ledger.md"
                root = self.project(shared, name, tpl.read_text(encoding="utf-8"))
                code, out = self.check(lang, root)
                self.assertEqual(code, 0, out)


if __name__ == "__main__":
    unittest.main()
