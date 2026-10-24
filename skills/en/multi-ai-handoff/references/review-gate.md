# Using the Review Gate

`scripts/review_gate.py` does one thing only: **it records "who reviewed which version of the file, when, and with what verdict", and before the next step starts it checks whether the file has changed.** It does not judge whether the content is good. The reviewer does that.

## One complete handoff

```bash
# 1. The executor hands over the product. The controller dispatches an independent reviewer
#    (a read-only subagent) and saves its reply verbatim as r.md
# 2. Record
python3 review_gate.py record --stage shot-list --dir ep03/reviews \
  --report r.md --product ep03/03_shot-list.md \
  --basis ep03/03_enriched-script.md '00_project/asset-registry.md#Lin Wan,old warehouse' \
  --mode independent

# 3. Check before the next step starts (a new conversation will not remember which
#    files were listed, so use --from-record)
python3 review_gate.py check --stage shot-list --dir ep03/reviews --from-record
```

## What to do with each check result

| Status | Meaning | Who handles it |
|---|---|---|
| PASS | Released | — |
| RULED | Released by the owner's ruling | — |
| MISSING | No review record | Controller dispatches a review |
| STALE | File changed after the review | Controller dispatches a new review (an incremental review is fine) |
| REVISE | Problems to fix | Original executor fixes, then dispatch again |
| UNPARSEABLE | No single verdict line found in the report | Controller dispatches again and asks for the required format |
| NEEDS_EVIDENCE | Not enough evidence | Controller supplies evidence (run scripts, extract frames), then dispatches again |
| NEEDS_DECISION | Rule conflict, or the human must decide | Check the rule ledger first; ask the owner only if the ledger cannot answer |
| LIMIT | Three REVISE rounds in a row | Stop and hand to the owner |
| SELF_REVIEW | A PASS from the author's own review | Not released; dispatch an independent review instead |

## Owner's ruling

When the owner says "use it as is" or "I disagree with the review", record their exact words. Do not write a PASS for them:

```bash
python3 review_gate.py ruling --stage shot-list --dir ep03/reviews \
  --quote "Keep node 7, handle it in editing" --source "chat 10-24 14:05" \
  --product ep03/03_shot-list.md
```

If the reviewed file changes again, the ruling is also invalidated.

## Shared big tables count only the relevant rows

For a table shared by the whole project, such as `asset-registry.md`, write `path#keyword1,keyword2`. Only the rows containing those words are hashed. When another episode edits other rows of the table, this episode's record does not become invalid.

## Fill in --mode honestly

- `independent`: a read-only subagent in an independent context.
- `degraded`: no read-only agent was found, so a general agent with prompt constraints was used, without tool isolation.
- `self`: the author reviewed it. It can be recorded, but it cannot release.

## Review report format (for the reviewer)

The whole report may contain only one line starting with `- Verdict:`:

```markdown
### Problems
1. Location: ep03/03_shot-list.md line 88 (node 07)
   Basis: asset register "Lin Wan / casual wear"
   Observed: written as "black trench coat"; the registered image is a gray knit jacket
   Impact: the character changes clothes after generation and does not match neighboring nodes
   Fix: change the appearance words to match the register
   Owner: shot-list
### Item-by-item checks
| ID | Result | Evidence |
|---|---|---|
| S01 | Pass | Lines 12–30, nodes 01–03 compared against scene 2 of the enriched script |
### Review verdict
- Verdict: REVISE
```
