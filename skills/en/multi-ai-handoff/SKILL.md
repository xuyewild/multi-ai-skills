---
name: multi-ai-handoff
description: Use when several AIs (Claude, Codex, ChatGPT, subagents) work on one project. It sets who executes, who checks, and who decides. It hands work over through files, runs an independent review before each handoff, picks the model by task difficulty, logs paid generation before clicking, and asks the human for decisions once, as lettered A/B/C/D options. Fits long tasks that cost money, need rework, or span many conversations, such as AI video, images, or code. Not for one-off Q&A.
license: MIT
metadata:
  version: "0.1.0"
---

# Multi-AI Division of Labor and Handoff

This practice comes from half a year of AI comic-drama production: one director, Claude, Codex, and several subagents, with dozens of paid video generations every day. The core is one sentence: **AIs trust files, not conversation; every handoff gets checked; spending money and making decisions belong to the human alone.**

## 1. Three roles

For every task, write down these three roles first. They can be different sessions of the same model, but they cannot share one context.

| Role | Does | Does not do |
|---|---|---|
| **Executor** | Produces files, runs scripts, operates the browser, submits generations | Never marks its own product "pass" |
| **Checker** | Compares the real product against the requirements and gives a conclusion with evidence | Does not edit the product, approve it, or spend money |
| **Owner (human)** | Approves key products, spends money, sets direction, merges rule changes | — |

Examples from practice (split by tool strengths, not by "which model is smarter"):

| Work | Executor | Checker |
|---|---|---|
| Script enrichment, shot-list writing | Claude | Independent review subagent |
| Generating asset images, operating the generation platform | Codex (built-in image generation, browser) | Claude |
| First look after generation | Codex runs frame-extraction and audio scripts | Claude answers the contact sheet question by question |
| Final acceptance | — | Owner watches the video |

If one tool is unavailable, the other may also act as executor. The check still happens, and the delivery states: "execution and checking were not separated this time".

## 2. Handoff by files only

- Every step's input and output is a **fixed file name** (for example `ep03/03_shot-list.md`). Before starting, the next step checks that the file exists. If it is missing, stop and report "which step, which file is missing". Do not fill in for upstream.
- "Done" or "confirmed" said in conversation does not count. The file counts. Progress = what is in the folder.
- For how to write a handoff package, see [templates/handoff-package.md](templates/handoff-package.md): **give paths, not conclusions**. Do not write "passed" or "should be fine", and do not hand over only the author's own summary.
- When assigning work to another AI, the first line tells it to load the matching skill and the project rule files first. If they conflict, the rule file wins.

For how to organize the project folder and record rules, see the companion skill `project-memory`.

## 3. Independent review before handoff

After the executor's self-check and script checks, and before handing to the next step, open a checker in a **separate, independent context** to review.

1. **The reviewer is read-only**: give it only Read, Glob, and Grep (see [templates/independent-reviewer.md](templates/independent-reviewer.md) for the Claude Code subagent definition). Do not self-review in the production session. Do not use fork (a fork inherits the author's line of thinking).
2. **Task package**: the original requirement with its source, the path of the file under review, the upstream and downstream files that must be read, the applicable rules, tool reports (labeled as tool reports), and the scope and completion conditions.
3. **Only four verdicts**: `PASS`; `REVISE` (list the problems; the original executor fixes them); `NEEDS_EVIDENCE` (evidence missing; the controller supplies it and dispatches again); `NEEDS_DECISION` (rule conflict, or the human must decide). Each problem needs a location, a basis, the observed fact, the impact, the fix, and who fixes it.
4. **Check long lists item by item**: for stages where things are easy to miss, give a numbered checklist. The review report has one line per number, with evidence (line number, node number, the observed fact). "Checked" or "meets requirements" is not evidence.
5. **Record and release with a script**: `scripts/review_gate.py record` stores the SHA256 of the review report and of the reviewed files. Before the next step starts, run `check`. If a file changed, the record is automatically invalid (STALE) and needs a new review. For usage see [references/review-gate.md](references/review-gate.md).
6. **Rework has a cap**: beyond the first pass, at most two automatic rework rounds. If the same spot fails 3 rounds in a row, or two rounds in a row show no improvement, stop and hand it to the owner. Do not lower the standard, fake a pass, or rerun forever.
7. **No conclusions on what the reviewer cannot see**: if it only has still frames, it must not judge motion continuity, lip sync, or sound. Write "insufficient evidence, left for the human to watch".
8. **PASS is not approval**: a review only says this version was checked within this scope. Approval still belongs to the owner.

If small edits follow a PASS, do only an **incremental review** (changed sections and what they touch). But before entering paid generation, review the current version once in full.

## 4. Choose the model by difficulty

Split the work into small units that can be accepted on their own. Score each unit, then assign a tier. Do not move the whole project to the top tier for the long term because of one hard point.

`S = 2N + 2K + A + F − 2E`
N originality 0–4 | K condition coupling 0–4 | A uncertainty 0–3 | F cost of error and rework 0–3 | E clarity of an existing solution 0–3

| S | Tier (Claude as the example) |
|---|---|
| A reliable script can do it | Run the script, no model |
| ≤ 1 | Light (Haiku · low): extraction, tidying, format checks, hash and word-list checks |
| 2–7 | Standard (Sonnet · medium) |
| 8–12 | Complex compilation (Sonnet · high): solution is settled, many conditions |
| 13–17 | Design (Opus · medium): core plot, key shots |
| ≥ 18 | Deep (Opus · high or above); write down the difficulty and completion conditions first |

- Missing file, wrong path, platform error, random generation variance: find the cause first. Do not raise the tier.
- A long input is not a hard one. Once the design is settled, compilation and tidying drop back to a low tier.
- Leave one line for every delegation: `unit | S | tier | reason`. Which model was actually used is whatever the interface shows. The model's own claim is not evidence.

For details and the tier agent definitions, see [references/tiering.md](references/tiering.md).

## 5. Paid actions

Generating video, generating images, and calling paid APIs are paid actions. The rules are stricter than for normal tasks:

1. **Ask before running**: before the first submission, list the quantity, model, estimated cost, and retry cap for the owner. Start only when the owner says "run". The owner can authorize "check, then generate directly" in the project rules. The authorization counts only once it is written into the rule ledger.
2. **Log before clicking**: `scripts/ledger.py reserve` reserves the amount → click only once → record the task ID → `settle` with the actual charge. If you clicked but do not know whether it was accepted, record `unknown`. **Reconcile first; do not press again.**
3. **Retries have a cap**: for each unit, the first try + reruns after errors + auto-fixes together must not exceed the cap (3 in practice). Beyond that, hand it to the owner. Redos the human names explicitly are counted separately.
4. **Auto-fix a hard defect once**: only for clear hard defects (missing character, swapped characters, broken proportions, wrong subject). Find the cause first (a wording problem means editing the prompt; a random problem means redrawing). If you can redo only the broken segment, do not redo the whole thing.
5. **AI first look is not acceptance**: the AI lists doubts and the three weakest spots. It does not write "first look passed". The human decides acceptance.
6. **Do not say "confirmed" without verifying**: an effect nobody actually saw or heard cannot be called confirmed. Also, never pay for test clips just to verify a rule.

For the ledger format and commands, see [references/paid-actions.md](references/paid-actions.md).

## 6. Human-only matters

The AI does not do these and does not answer for the human: approving key products (asset images, the final video); spending beyond budget or without authorization, and top-ups; core direction, character relationships, ending, and style tone; changing content the human locked or edited by hand; merging rule or skill changes into the official branch; deleting files; changing global settings or other projects.

The AI never writes "owner confirmed / approved / has seen it". If you are not sure who owns something, treat it as the human's.

## 7. How to ask the human

- Ask only at **stop points**. Decide where each stage stops (for example: plan, key materials, prompts, final video). A stop point gives only the file name and one line of explanation.
- When the human must decide, ask everything at once, at most four questions, each with lettered options and the recommended one first. A reply like "1A 2C" is enough. For the format, see [templates/decision-card.md](templates/decision-card.md).
- Do not ask what can be settled from the rules, records, or usual practice. State the assumption in one sentence at the start of the delivery.
- Apply the human's corrections on the spot, then write them back to the project files by category (see `project-memory`), so they are carried automatically next time.

## 8. Report failure in two things only

Which step, and what is missing. Do not fix other steps for them, and do not write long diagnostic reports.
