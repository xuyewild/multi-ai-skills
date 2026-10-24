import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
import os
LANGS = tuple(os.environ.get("TEST_LANGS", "zh en").split())


def script(lang, skill, name):
    return SKILLS / lang / skill / "scripts" / name


def run(path, *args, cwd=None):
    p = subprocess.run([sys.executable, str(path), *map(str, args)],
                       cwd=cwd, capture_output=True, text=True, encoding="utf-8")
    return p.returncode, p.stdout + p.stderr
