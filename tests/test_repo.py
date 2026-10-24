"""Repository-wide checks: both languages present, scripts identical,
frontmatter valid, relative links resolve, nothing private leaked."""
import re
import unittest

from helpers import LANGS, ROOT, SKILLS

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
PRIVATE_RE = re.compile(r"/Users/|/home/[a-z]|[\w.+-]+@[\w-]+\.[\w.]+|C:\\\\Users")


def skill_names(lang):
    return sorted(p.name for p in (SKILLS / lang).iterdir() if p.is_dir())


def frontmatter(text):
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    return dict(re.findall(r"^(\w+):\s*(.+)$", m.group(1), re.M)) if m else {}


class RepoTest(unittest.TestCase):
    def test_same_skills_in_both_languages(self):
        self.assertEqual(skill_names("zh"), skill_names("en"))

    def test_same_files_and_identical_scripts(self):
        for name in skill_names("zh"):
            zh, en = SKILLS / "zh" / name, SKILLS / "en" / name
            files = lambda d: sorted(str(p.relative_to(d)) for p in d.rglob("*") if p.is_file())
            with self.subTest(skill=name):
                self.assertEqual(files(zh), files(en))
                for p in (zh / "scripts").glob("*.py"):
                    self.assertEqual(p.read_bytes(), (en / "scripts" / p.name).read_bytes(), p.name)

    def test_frontmatter(self):
        for lang in LANGS:
            for name in skill_names(lang):
                with self.subTest(lang=lang, skill=name):
                    fm = frontmatter((SKILLS / lang / name / "SKILL.md").read_text(encoding="utf-8"))
                    self.assertEqual(fm.get("name"), name)
                    self.assertEqual(fm.get("license"), "MIT")
                    self.assertTrue(10 < len(fm.get("description", "")) <= 1024)

    def test_relative_links_resolve(self):
        for md in ROOT.rglob("*.md"):
            if ".git" in md.parts:
                continue
            for target in LINK_RE.findall(md.read_text(encoding="utf-8")):
                if re.match(r"[a-z]+:|#", target):
                    continue
                with self.subTest(file=str(md.relative_to(ROOT)), link=target):
                    self.assertTrue((md.parent / target.split("#")[0]).exists())

    def test_no_private_paths_or_emails(self):
        for p in ROOT.rglob("*"):
            if p.name == "test_repo.py":
                continue  # holds the pattern itself
            if p.is_file() and ".git" not in p.parts and p.suffix in (".md", ".py", ".yml", ".json"):
                with self.subTest(file=str(p.relative_to(ROOT))):
                    text = p.read_text(encoding="utf-8")
                    self.assertEqual(PRIVATE_RE.findall(text), [])


if __name__ == "__main__":
    unittest.main()
