# Choose the Model by Difficulty

Goal: spend subscription quota where it is really hard. Use high-tier models for design, and low-tier models for tidying and checking.

## Scoring

Score each unit of work that can be accepted on its own, once:

| Item | Range | What to look at |
|---|---|---|
| N originality | 0–4 | 0 copy and tidy; 4 design the core content from scratch |
| K condition coupling | 0–4 | How many rules and upstream/downstream constraints must hold at once |
| A uncertainty | 0–3 | How much is unclear about requirements, facts, or platform behavior |
| F cost of rework | 0–3 | How much money and time a mistake wastes, and whether it hurts downstream |
| E clarity of solution | 0–3 | Whether a ready solution, template, or example exists |

`S = 2N + 2K + A + F − 2E`

## Assigning a tier (Claude Code subagents as the example)

| S | Tier | Model · thinking | Typical work |
|---|---|---|---|
| — | Script | No model | Hashing, format validation, file comparison |
| ≤ 1 | tier-light | Haiku · low | Extract lists, dedupe, word-list scans, mechanical checks before review |
| 2–7 | tier-standard | Sonnet · medium | Routine writing, ordinary compilation |
| 8–12 | tier-complex | Sonnet · high | Compilation with a settled solution and many conditions |
| 13–17 | tier-design | Opus · medium | Core plot, characters, key shot design |
| ≥ 18 | tier-deep | Opus · high (up to xhigh/max) | A located, major hard problem |

`templates/tier-agents/` holds the definition files for these five subagents. Put them in the project's `.claude/agents/` and they are ready to use.

## A few lessons

- **Give core creative work straight to a high tier.** No need to let a low tier fail first.
- **Give settled-solution, complex compilation to tier-complex.** Do not ask Opus to redesign it.
- **Tool problems do not raise the tier**: missing file, wrong path, permissions, platform error, random generation variance. Find the cause first.
- **Long is not hard**: cut large amounts of simple content into chunks for a low tier.
- **At most one targeted change with real substance for the same problem.** If it still fails, re-judge the cause or change the tier. Do not rerun blindly. Count reasoning rework and paid-generation retries separately.
- **Before using xhigh / max, write down**: what the hard problem is, which non-reasoning causes were ruled out, why it is worth it, and the completion conditions. At most one such unit at a time.

## Recording and verifying

Leave one line for every delegation: `unit | S | tier | reason`.

A model saying "I am Opus" is not evidence. Go by what the interface shows. If you cannot see it, write "unverified".

These environment variables quietly force all subagents onto the same model. Do not set any of them when using tiers: `CLAUDE_CODE_SUBAGENT_MODEL`, `CLAUDE_CODE_SUBAGENT_MODEL_FORCE`, `CLAUDE_CODE_EFFORT_LEVEL`.
