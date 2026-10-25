# multi-ai-skills

[![tests](https://github.com/xuyewild/multi-ai-skills/actions/workflows/tests.yml/badge.svg)](https://github.com/xuyewild/multi-ai-skills/actions/workflows/tests.yml) [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

English | [中文](README.zh-CN.md)

I've been making AI comic dramas with Claude and Codex for about six months. Thousands of clips so far, and I open a few fresh chats every day.

The thing I learned: the problem with AI isn't that it's dumb, it's that it gets messy. Open a new chat and it has no idea where we left off. Worse, it "remembers" things I never said. I tested this once. In the first chat it decided on its own that a scene happens at dusk. In the next chat it treated dusk as my call. Then there's the AI that reviews its own work and says it's fine, and the paid generation that hangs so you can't tell if you just got charged.

This repo is what I ended up doing about it. Two skills.

**multi-ai-handoff** is about who does what. Who does the work, who checks it, who makes the call. Handoffs go through files, and a different AI looks it over first. Paid generations get logged before you click. Pick the model by how hard the job is, don't throw the priciest one at everything.

**project-memory** is about remembering. Progress and rules go in the project folder, so a new chat reads the files and knows what's next. The rule ledger only has things I actually said. AI guesses don't count.

You can install either one alone, but they're better together. English is in `skills/en/`, Chinese in `skills/zh/`, same content.

## Is this for you?

If your project runs for days across a bunch of chats, or you've got several AIs going at once, or generation costs money and redoing stuff hurts, yes. If you're just asking a question or two, you don't need it.

## The rules I stick to now

- Chat history doesn't count. If it's not in a file, it didn't happen.
- Nobody approves their own work. A different AI checks it. The check saves file hashes, so if the file changes, the old "pass" is gone.
- Only I spend money or make decisions. Log the paid action, click once. If you're not sure it went through, go look on the platform. Don't just click again.
- Score the task before picking a model: `S = 2N + 2K + A + F − 2E`. Save the expensive models for work that needs real thinking.
- Rules get copied in my exact words.

## 30-second example

The ledger won't let you click again while the last attempt is in an unknown state:

```console
$ S=skills/en/multi-ai-handoff/scripts/ledger.py
$ python3 $S demo.json init --unit credits --limit 500
ok
$ python3 $S demo.json reserve --id shot1-a1 --item shot1 --cost 120
ok
$ python3 $S demo.json unknown --id shot1-a1      # clicked, not sure it went through
ok
$ python3 $S demo.json reserve --id shot1-a2 --item shot1 --cost 120 --kind retry
REFUSED shot1 has an attempt in state `unknown`; reconcile with the platform first
```

## Install

**Claude Code**: copy the skill folders you want into `~/.claude/skills/` (global) or `.claude/skills/` in your project.

```bash
git clone https://github.com/xuyewild/multi-ai-skills
cp -r multi-ai-skills/skills/en/multi-ai-handoff ~/.claude/skills/
cp -r multi-ai-skills/skills/en/project-memory ~/.claude/skills/
```

If you want the tiered subagents, copy `skills/en/multi-ai-handoff/templates/tier-agents/` and `templates/independent-reviewer.md` into your project's `.claude/agents/`. This repo uses the same agents in [.claude/agents/](.claude/agents/).

**Claude web or desktop app**: zip a skill folder and upload it as a custom skill in settings.

**Other AIs**: a skill is just some Markdown and a few Python scripts. Hand the AI `SKILL.md` and whatever reference files it points to.

## Scripts

Python standard library only, 3.9 or newer.

| Script | What it does |
|---|---|
| `multi-ai-handoff/scripts/review_gate.py` | Records review verdicts with file hashes, and checks before a handoff whether it can go through |
| `multi-ai-handoff/scripts/ledger.py` | Ledger for paid actions: budget, retry cap, and no second click while a state is unknown |
| `project-memory/scripts/check_project.py` | Checks the rule ledger format and the project's key files |

```bash
python -m unittest discover -s tests -v
```

## Feedback

Open an issue if something breaks, especially after you've tried it on a real project. If you think a rule is wrong, tell me what you were doing and what went sideways.

## License

[MIT](LICENSE)
