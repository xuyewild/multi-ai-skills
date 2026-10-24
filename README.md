# multi-ai-skills

English | [中文](README.zh-CN.md)

Two skills that keep long projects sane when several AIs (Claude, Codex, ChatGPT, subagents) work on them together, and keep paid generation from burning money. They come from half a year of AI comic-drama production: one director, a few AIs, dozens of episodes, dozens of paid video generations a day, and several fresh conversations every day.

| Skill | What it solves |
|---|---|
| [multi-ai-handoff](skills/en/multi-ai-handoff/SKILL.md) | Who executes, who checks, who decides; handoff through files; independent review before every handoff; pick the model by difficulty; log paid generation before clicking |
| [project-memory](skills/en/project-memory/SKILL.md) | The project folder is the memory; human corrections are written back by type; a rule ledger holds only rules the owner set; a new conversation reads the files to know where to resume |

Each skill works on its own; they work best together. Every skill ships in English (`skills/en/`) and Chinese (`skills/zh/`). Both versions have the same content and each installs on its own.

## Who it is for

- You use AI for video, images, long documents or multi-round code, and a project runs for days across many conversations.
- You use two or more AIs at once, or split work across subagents.
- You pay for generation, so rework is expensive.

Not useful for one-off Q&A.

## The core ideas

- **AIs trust files, not conversation.** Progress is whatever is in the folder.
- **Every handoff gets an independent check.** Authors never pass their own work. Review records carry file hashes and expire as soon as a file changes.
- **Money and decisions belong to the human.** Paid actions are reserved, clicked once, then settled. If you are not sure a click went through, reconcile first; never click again.
- **Pick the tier by difficulty.** `S = 2N + 2K + A + F − 2E`. Spend top-tier models only on design.
- **Record only rules the owner set, in their exact words.** AI guesses never become rules.

## Install

**Claude Code**: copy the skill folders you want into `~/.claude/skills/` (global) or `.claude/skills/` in your project.

```bash
git clone https://github.com/Vsuperdouble/multi-ai-skills
cp -r multi-ai-skills/skills/en/multi-ai-handoff ~/.claude/skills/
cp -r multi-ai-skills/skills/en/project-memory ~/.claude/skills/
```

For tiered subagents, copy `skills/en/multi-ai-handoff/templates/tier-agents/` and `templates/independent-reviewer.md` into your project's `.claude/agents/`. This repo uses the same agents in [.claude/agents/](.claude/agents/).

**Claude web or desktop app**: zip a skill folder and upload it as a custom skill in settings.

**Other AIs**: a skill is just Markdown plus Python scripts. Give the AI `SKILL.md` and the reference files it points to.

## Scripts

Python standard library only, 3.9+.

| Script | What it does |
|---|---|
| `multi-ai-handoff/scripts/review_gate.py` | Records review verdicts with file hashes; checks before a handoff whether it may proceed |
| `multi-ai-handoff/scripts/ledger.py` | Ledger for paid actions: budget, retry cap, no re-click while a state is unknown |
| `project-memory/scripts/check_project.py` | Checks the rule ledger format and the project's key files |

```bash
python -m unittest discover -s tests -v
```

## Contributing

Issues and PRs are welcome, especially problems you hit after using these in your own project. When proposing a rule change, describe the situation where things went wrong.

## License

[MIT](LICENSE)
