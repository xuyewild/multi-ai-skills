# Folder Layouts: A General Form and Two Examples

## General form

```
project-name/
  00_project/         <- shared: rule-ledger, settled-facts, progress-summary, owner-notes, run-mode, handoff
  <unit-prefix>NN/    <- one folder per unit
    NN_<step-1-output>.md
    NN_<step-2-output>.md
    ...
    reviews/
```

Three rules for choosing file names:

1. **One output file per step.** The name says which step it is and what it is. The next step can then tell from the file name whether the previous step is done.
2. **Start with the unit number** (`03_script.md`). If a file is sent out alone, it is still clear which unit it belongs to.
3. **Keep notes files apart from output files.** Outputs are read by the next step. Notes (what changed, what the owner must decide) are read by the human.

## Example 1: a short-video series (fictional project "Letters from Fog Harbor")

```
Letters from Fog Harbor/
  00_project/
    rule-ledger.md
    settled-facts.md      <- characters: mail carrier Lan, lighthouse keeper Old Zhou; harbor map
    progress-summary.md
    owner-notes.md
    asset-registry.md     <- all recurring assets and status: to generate / generated / approved
    cost-ledger.json
  epNN/
    NN_draft.md           <- from the owner
    NN_script.md          <- step 1
    NN_script-notes.md    <- step 1: what changed, [SETTING] and [PENDING] items
    NN_asset-needs.md     <- step 2
    assets/
    NN_shot-list.md       <- step 3
    NN_generation-log.md  <- step 4: each shot's submission, cost, AI first look
    video/
    reviews/
```

## Example 2: a multi-round document or code project (fictional project "Warehouse Handbook")

```
Warehouse Handbook/
  00_project/
    rule-ledger.md
    settled-facts.md      <- glossary, who the readers are, chapter split
    progress-summary.md
    owner-notes.md
  chNN/
    NN_outline.md
    NN_draft.md
    NN_revision-notes.md
    NN_final.md
    reviews/
```

For a code project, replace `chNN/` with `iterNN/`, and use `NN_requirements.md`, `NN_design.md` and `NN_test-report.md` as outputs. The code itself stays in the repository. Only handoff files go here.
