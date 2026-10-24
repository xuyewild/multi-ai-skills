# Resuming After a Break: How to Write the Decision Table

Each project writes one "existing files -> where to resume" table. Put it in `run-mode.md` or the project instructions. A new conversation follows the table. It does not rely on memory.

## How to write it

- The left column holds only **conditions that can be judged from files**: whether a file exists, a status in the registry, whether the end of a record has a certain line.
- The right column says **which step to resume at**. For a stop, use the stop point name, such as "Stop 1".
- When several rows match, take the **lowest** row (furthest progress). So order the rows top to bottom in workflow order.
- When "the owner agreed" cannot be judged from files, write "Stop X; if the owner has said yes, go to the next step". Accept only the owner's own words.

## Example (fictional project "Letters from Fog Harbor", see folder-layouts.md)

| Existing files | Resume at |
|---|---|
| Only `NN_draft.md` | Step 1: write the script |
| `NN_script.md` + `NN_script-notes.md`, no asset needs | Stop 1: the owner reads the script notes. If the owner has said yes, go to step 2 |
| `NN_asset-needs.md`, `assets/` incomplete or the registry still has "to generate" | Step 2, fill in only the missing images |
| Registry has "generated" but no "approved" | Stop 2: the owner looks at the images |
| All of this episode's assets are "approved" | Step 3: shot list |
| `NN_shot-list.md`, no video | Stop 3. If the owner has said yes and review passes, go to step 4 |
| Video exists, and the end of `NN_generation-log.md` has no "Unit done" line | Stop 4: the owner watches. Even after everything is watched, ask "Is there anything else to adjust in this episode?" |
| The end of `NN_generation-log.md` has `Unit done: confirmed by owner (date)` | Update settled-facts and progress-summary, do rule evolution, then open the next episode |

## Common pitfalls

- **Judging progress by "it was said in a conversation".** This breaks when the conversation changes. Look only at files.
- **Counting a backup file as progress.** `old_03_script.md` is not `03_script.md`.
- **The AI writes the "Unit done" line itself.** Write this line only after the owner clearly says "this episode has nothing left to adjust", and write the date.
- **Upstream changed and downstream does not know.** If the script changes, the shot list is stale. Review records carry file hashes. A record whose hash no longer matches becomes invalid automatically.
