---
name: changelog
description: Create or update CHANGELOG.md in the Colivo root from git commits, one heading per date (newest first). Run manually before merging a branch, and at the end of a session that committed straight to main.
disable-model-invocation: true
allowed-tools: Bash(git log *), Bash(git diff *), Bash(git branch *), Bash(git rev-parse *), Bash(git status *), Bash(git add CHANGELOG.md), Bash(git commit *), Bash(npx prettier *), Read, Edit, Write
---

Keep `CHANGELOG.md` (project root) up to date from git history. Extra
instructions from the user, if any: $ARGUMENTS

## 1. Pick the mode

- **No `CHANGELOG.md`** → **bootstrap**: use the full history:
  `git log --no-merges --date=short --format='%ad%x09%h%x09%s%n%b'`
- **`CHANGELOG.md` exists** → **update**: use every commit since the last one
  that changed the changelog, on `main` or on a branch alike:
  1. `git log -1 --format=%H -- CHANGELOG.md` → `<last>`.
     - If empty, the file exists but was never committed: tell the user and
       stop.
  2. `git log <last>..HEAD --no-merges --date=short --format='%ad%x09%h%x09%s%n%b'`
  - If the range is empty, say there's nothing to add and stop.

Why not `main..HEAD`: Colivo also commits straight to `main` (specs, design),
and those commits would never be logged. Starting after the last changelog
commit covers both, and never logs a commit twice.

## 2. Turn commits into bullets

- Group commits by date (`%ad`, the author date).
- **Skip**: merge commits, formatting-only `style:` commits, and earlier
  `docs: update changelog` / `docs: add changelog` commits.
- Write one bullet per meaningful change, for humans, not raw commit subjects:
  - Past tense, sentence case, ends with a period, one line.
    `feat(accounts): lock log-in after 5 wrong codes` →
    `Locked log-in after five wrong codes.`
  - Use the commit body for context; don't repeat the type prefix or scope.
  - Merge related commits on the same date into one bullet. In Colivo this is
    common: a `docs(specs)` commit plus its `docs(design)` mobile and web
    commits are one change; a backend `feat(<module>)` and its
    `feat(web)` commit for the same behaviour are one change.
  - Name the area when it helps the reader: "In the design, …", "In the
    specs, …", "In the API, …", "On the web, …".
  - When a commit marks a roadmap phase `✅ Complete` in `specs/roadmap.md`,
    add a bullet `Completed Phase N — <name>.`
- Keep bullets in the order the work happened within each date (oldest first).

## 3. Write the file

Format (dates newest first, flat bullet list under each date):

```markdown
# Changelog

All notable changes to Colivo, grouped by date (newest first).

## YYYY-MM-DD

- Added ….
- Changed ….
```

- **Bootstrap**: write the whole file.
- **Update**: add bullets under an existing `## <date>` heading (appended after
  its current bullets) or insert a new date heading in the right position.
- Never rewrite, reorder, or delete existing entries.
- Run `npx prettier --write CHANGELOG.md`.

## 4. Review, then commit

1. Show the user `git diff CHANGELOG.md` (or the new file) and wait for
   approval.
2. After approval, commit only `CHANGELOG.md` as `docs: update changelog`
   (`docs: add changelog` on bootstrap), so it lands on the branch before it is
   merged. No Co-Authored-By or AI attribution lines.
