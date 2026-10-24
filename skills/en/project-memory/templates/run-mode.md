# Run Mode: <project name>

In effect when: this file says it, and the matching entry in `rule-ledger.md` is "active". Anything the ledger does not cover follows the skill default.

## 1. File name table
| Step | Reads | Writes |
|---|---|---|
| 1 | <input file> | <output file> |

## 2. Stop points
| Stop | What the owner looks at | Cancelled in this project? | Ledger ID |
|---|---|---|---|
| 1 | <file> | No | — |

A cancelled stop point is replaced by review release (`review_gate.py check` returns 0).

## 3. Spending
- Budget: <total / cap per unit>
- Ask before each unit: <yes / no, ledger ID>
- Retry limit: <how many retries after the first try>

## 4. Not cancelled by this file
Spending over budget, deleting files, changing locked content, changing the core direction, merging rule changes.

## 5. Resume decision table
<See how to write it in references/resume-rules.md>
