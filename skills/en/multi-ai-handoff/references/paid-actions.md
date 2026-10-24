# Paid Actions: Ask First, Log First, Click Once

This applies to video generation, image generation, paid APIs, denoise redraw, and any action that costs money or credits each time.

## Confirm once at project start

Model, aspect ratio, resolution, budget unit and total, retry cap per unit, concurrency, and whether to produce a low-resolution sample first. Ask only about what is missing. Write the answers at the top of the generation log, then create the ledger:

```bash
python3 ledger.py 00_project/cost-ledger.json init --unit credits --limit 20000 --retry-limit 3
```

Estimate cost in tiers of "duration × resolution", using the unit price measured at project start. When a setting changes (new model, new resolution), confirm again. Do not quietly lower the spec.

## Every submission

```bash
python3 ledger.py ledger.json reserve --id ep3-n07-a1 --item ep3/n07 --cost 120   # reserve
# ...click generate on the platform only once...
python3 ledger.py ledger.json submitted --id ep3-n07-a1 --task <platform-task-id>
python3 ledger.py ledger.json settle --id ep3-n07-a1 --charge 118                 # settle at the actual charge
```

- If you clicked generate but the page did not respond and you do not know whether it was accepted, record `unknown`. After that, any new reservation for this unit is rejected. **Go reconcile on the platform first**, and continue only after confirming it was not accepted. This one rule blocks the most expensive mistake seen in practice: double clicking.
- When the platform fails and refunds: `refund`. A duplicate refund is recorded only once.

## Retry kinds

| kind | When | Counts toward the cap? |
|---|---|---|
| first | The first attempt | Yes |
| retry | A rerun after a platform error or no output | Yes |
| autofix | The one automatic fix after the AI judges a hard defect | Yes |
| human | A redo the owner names after watching | No, counted separately |

## How to write the AI first look

After a clip comes out, the AI looks first. This only helps the human narrow the scope:

- Extract frames per shot and build a contact sheet. Answer each question with yes / no / not sure, and write the second where the evidence is.
- State how many questions were checked, where the doubts are, and the three weakest spots.
- Do not write "first look passed". For motion, lip sync, and sound, which need playback or listening, write "left for the human".
- When the human finds something the AI missed, add it to the project's "must check when watching" list, and the AI checks those items first next time.

## Auto-fix of hard defects

Fix only clear hard defects: missing character, swapped faces, broken proportions, wrong subject. A subtitle-only issue does not count.

1. First rule out execution problems (wrong image uploaded, wrong parameters, prompt not fully pasted).
2. Locate the shot and the second.
3. Judge the cause: a wording problem means editing the prompt; a random problem means redrawing.
4. If you can redo only the broken segment, redo that segment. Redo the whole clip only when it cannot be cut apart. Write the replacement in the editing notes.
5. If the cause cannot be determined, the fix would change plot or dialogue, or you are unsure whether to redo a segment or the whole clip, ask the human.

## Do not

- Do not pay for extra test clips just to verify a rule.
- Do not switch back to an old model on your own because a new model failed.
- Do not go back and change a product that was already accepted.
