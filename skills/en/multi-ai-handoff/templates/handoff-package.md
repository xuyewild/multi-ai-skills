# Handoff Package Template

Send it as one message when assigning work or dispatching a review. **Give paths, not conclusions.**

```markdown
## Read first
- Load skill: <skill name or path> (version / repo commit: <SHA>)
- Project rules: 00_project/rule-ledger.md#R012,R031 (list only the IDs used this time), run-mode file: <path if any, otherwise write "none">
- On a rule conflict, the rule ledger wins

## Goal
<The owner's exact words, with source and date; list locked items one by one>

## Input
- File to process / review: <path>
- Upstream and downstream files that must be read: <paths>
- Tool report (not a conclusion): <path of the script output>

## Output
- Write to: <path, fixed file name>
- Completion condition: <what counts as done>

## Scope
- Do this time: <...>
- Do not do this time: <...>
- Rework round: round <N>; previous record: <path> (only for revisions)
```

## Do not write

- "Passed", "should be fine", "last round was basically OK"
- Only the author's own summary, without the original file
- Asking the other side to do out-of-scope things "while you're at it"
