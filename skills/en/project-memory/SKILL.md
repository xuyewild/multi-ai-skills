---
name: project-memory
description: Use for long projects that span many conversations and several AIs. The project folder is the memory. File names are fixed, and progress is whatever the files show. Human corrections are written back by type, and rules the owner has set go into a rule ledger. A new conversation reads the files to decide where to pick up. Fits series, video series, long documents and multi-round code work that run for many days. Not for one-off Q&A.
license: MIT
metadata:
  version: "0.1.0"
---

# Project Memory and Context Management

This method comes from six months of AI manga-drama production: dozens of episodes, hundreds of paid generations, and several new conversations every day. Conversations get compressed, models get swapped, and people take over. "We talked about it last time" does not hold up. The core idea is one sentence: **the project folder is the memory. What was said in a conversation does not count. What is written in a file counts. Rules the owner set are recorded in their own words. AI guesses are not recorded.**

The companion skill `multi-ai-handoff` covers who executes, who checks, who decides, and how to hand off. This skill covers where things live, what to record, and how to pick up after a break.

## 1. The project folder is the memory

```
project-name/
  00_project/              <- shared by the whole project, across units
    rule-ledger.md         <- rules the owner has set (section 4)
    settled-facts.md       <- confirmed facts: characters, world, interfaces, terms
    progress-summary.md    <- three to five lines after each unit is done
    owner-notes.md         <- the owner's corrections and preferences (section 3)
    run-mode.md            <- optional: how this project runs, which stops are cancelled (section 7)
    handoff.md             <- optional: takeover notes for a new conversation or person (section 8)
  epNN/                    <- one folder per unit (episode, chapter, iteration, batch)
    NN_input.md
    NN_output.md
    NN_notes.md            <- what changed this time, what the owner must decide
    reviews/               <- review records
```

- **File names are fixed.** Each step trusts file names, not conversation context. At the start of work, check that the files to read exist. If one is missing, stop and report "which step, which file is missing". Do not fill in for upstream.
- **Progress = what is in the folder.** Do not keep a separate "run status" file. Do not trust a "done" from an old conversation.
- Backups renamed to `old_*` or `*_before_*` do not count when judging progress.
- Shared files go in `00_project/`. Unit outputs go in their own folders. They never overwrite each other.

File names can change per project. If you change them, write one table in `run-mode.md` or the project instructions, and do not change them again. The general layout and two fictional examples are in [references/folder-layouts.md](references/folder-layouts.md).

## 2. Four kinds of things, four places

| What it is | Where it goes | Who can change it |
|---|---|---|
| Confirmed facts (who is who, settings, interfaces) | `settled-facts.md` | Updated in order when a unit is done. Ask the owner before changing an existing entry |
| Where things stand, what happened | `progress-summary.md` | Append one paragraph when each unit is done |
| The owner's corrections and preferences for this project | `owner-notes.md` | Record whenever the owner says it |
| Rules the owner has set (with priority order) | `rule-ledger.md` | Only the controller (or someone the controller assigns) edits it |

**Record only what the owner said or clearly approved.** Methods the AI guessed, suggestions that were not adopted, and one-off implementation details do not become entries. A paraphrase may narrow a rule. It may never widen it.

## 3. Fix it on the spot, then write it back by type

When the owner says "wrong", "you missed this", "too long" or "this doesn't work": finish the fix first. Then decide which type of correction it is, and write it back so it applies next time.

| The correction is about | Where it goes |
|---|---|
| Facts, settings, character relationships | List it as [SETTING] in the unit notes. After the owner confirms, it goes into `settled-facts.md` |
| How this project is written, preferences (opening too long, some approach does not work) | Append one line to `owner-notes.md`: `date | unit | gist of the quote | scope (this unit / whole project)` |
| A general rule that would hold in any project | Do not change the skill in the middle of a unit. Write it down and hold it for "Rule evolution" in section 10, where the skill is changed only when the conditions are met |

When a new entry overturns an old one, mark the old one "replaced". Do not delete it.

## 4. The rule ledger

`00_project/rule-ledger.md` is the only source of rules in the project. When files, conversations and skill wording conflict, the priority order written in the ledger decides.

```markdown
## Priority
Owner's latest words > run-mode.md > project instructions > skill defaults

## Rules
| ID | Rule | Quote | Source | Date | Status | Replaced by | Where it lives |
|---|---|---|---|---|---|---|---|
| R001 | Ask before each episode whether to run | "Ask me before every episode" | conversation | 2026-03-02 | replaced | R014 | run-mode.md |
| R014 | After checking against budget, generate directly | Decision card option "Check, then generate directly" | decision card | 2026-04-10 | active | — | run-mode.md section 2 |
```

- **Copy the quote exactly.** If the owner only tapped a decision card, write the option text on the card. A rule with no findable quote is not active. Mark it "pending".
- Status uses only three words: `active`, `replaced`, `pending`. Replaced rules are not deleted. The "Replaced by" column points to the new ID.
- "Where it lives" says which files and sections hold this rule. After a rule or skill upgrade, use it to check each rule is still carried.
- A new project with no ledger starts by collecting the settled rules from project instructions, notes and chat decisions. Rules that contradict each other and have no findable quote are marked "pending". Ask the owner.

The full template is [templates/rule-ledger.md](templates/rule-ledger.md). `scripts/check_project.py` can check the ledger format and key files (section 9).

## 5. Picking up after a break

When the user says "continue", opens a new conversation, or switches AI:

1. Read `00_project/handoff.md` (if present) and `rule-ledger.md` first.
2. List the standard files in the current unit folder. Use the "existing files -> where to resume" table. If several rows match, take the one with the furthest progress. Each project writes its own table. How to write it, with an example, is in [references/resume-rules.md](references/resume-rules.md).
3. "Confirmed" means only the owner's own words. If unsure, treat it as not confirmed and stop at that stop point.

**Half-finished work and rollback**

- Output is only half done: fill in from the gap. Keep what exists. Do not rerun the whole step.
- The owner names one item to roll back: rerun only the step that item belongs to. Do not touch upstream. After the fix, stop at the same stop point.
- An upstream file was changed: every output after that step is stale. Resume from the step after the changed one. Review records whose hash no longer matches become invalid automatically (see the review gate in `multi-ai-handoff`).
- Optional files to read (the previous unit's summary, the notes) do not exist yet in the first unit. Skip them. They are not "missing".

## 6. Parallel units and shared files

- By default, finish one unit before opening the next. Later changes may touch upstream, and the next unit must read the final version.
- Units can run in parallel when the owner asks. If the earlier unit later changes shared content, tell the owner where the next unit may be affected.
- **Only one place writes a shared file at a time.** When several units need to write it, write in unit-number order.
- Each unit's folder can move forward in a different conversation. Before starting, read the latest version of the shared files in `00_project/`.

## 7. Run mode and authorization

Default stop points and "ask before each step" are written in each skill. The owner may want to loosen them (for example, cancel a stop point, move on once review passes, or generate directly within budget). A loosening takes effect only when both are true:

1. It is written in `00_project/run-mode.md` or the project instructions.
2. `rule-ledger.md` has a matching active entry with the owner's quote.

With only one of the two, or a ledger status that is not "active", follow the skill default. Loosening never cancels any of these: spending over budget, deleting files, changing locked content, changing the core direction, merging rule changes. Only the owner decides which run mode a project uses. An AI does not cite an old project's authorization for a new project. Template: [templates/run-mode.md](templates/run-mode.md).

## 8. Handoff file for switching conversations or people

When a conversation is about to end, or work goes to another AI, write `00_project/handoff.md`. The new conversation's first instruction is to read it. Write only these blocks:

1. Background: one or two paragraphs on why the work exists.
2. Settled: confirmed in the owner's own words, with dates.
3. Pending: what to ask the owner, with a recommendation for each.
4. Progress: a checklist, down to file paths.
5. Asset locations: a path plus one line of explanation.
6. The owner's working habits: a few things to follow.

Keeping "settled" and "pending" apart is the most important point in a handoff. The AI taking over most often treats a suggestion as settled, or asks again about something already settled. Template: [templates/handoff-file.md](templates/handoff-file.md).

## 9. Check

Run it at project start, before each unit starts, after a rule or skill upgrade, and when wording conflicts:

```bash
python3 scripts/check_project.py --project <root> [--require settled-facts.md progress-summary.md] [--out 00_project/check-report.md]
```

It checks: the ledger exists, it has a priority section, each entry has an ID and a valid status, "replaced" entries point to an existing ID, and active entries have a quote. It checks that key files under `00_project/` are missing (warning) or 0 bytes (problem). It checks that files are UTF-8 (problem). Exit code 0 means no problems, 1 means problems found, 2 means bad arguments. The script cannot tell whether rules contradict each other. Read the files to judge that, and state which file and which line you read.

## 10. Rule evolution

After finishing a unit, before opening the next, look back once:

1. **Look back**: the owner's rollbacks and comments at stop points, new entries in the notes, reasons for rework, cost.
2. **Record first**: the symptom, the cause, and what to do next time, in an experience file. Mark anything seen only once as "to verify".
3. **Change rules only when a condition is met**: the same problem has appeared twice; or the owner clearly said so; or a "to verify" item has a result. Meeting any one of the three is enough. When you change a rule, delete the old wording it replaces. Do not just pile new text on top.
4. **Ask the owner first about**: stop points, cost and retry limits, delivery format, requirements the owner has set, style and tone.
5. Do not change rules or switch versions in the middle of a unit. Do not spend money just to test a rule. Do not go back and change outputs already adopted.

## 11. Do not

- Do not treat a "done" or "confirmed" in a conversation as fact. Files and the owner's own words decide.
- Do not keep a status file that duplicates the folder.
- Do not write "confirmed" or "approved" on the owner's behalf.
- Do not turn a one-off approach into a long-term rule.
