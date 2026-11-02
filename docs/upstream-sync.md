# Synchronizing with Yapfast

YapCord preserves Yapfast's Git history and uses ordinary merges to incorporate
updates. It is an independent GitHub repository; synchronization does not require
membership in GitHub's fork network.

## Check for existing upstream work

Fetch upstream at the start of each development session. Review new commits
and relevant issues and pull requests before starting an area of work. Merge
reviewed updates before each UI milestone, and prioritize applicable security
and protocol fixes. This is an active development habit, not a scheduled job.

Check what the current implementation already offers before replacing it.
For example, Yapfast already has a Discord-like Bonfire palette and status
menus; a richer account popover may be a visual extension of those facilities.
An upstream PR might supply part of the work, but remains unshipped until it
is merged and verified. Record the decision to reuse, wait, adapt or implement
in the relevant YapCord development notes.

The initial review on November 2, 2026 found
[PR 36](https://github.com/yapfast/yapfast/pull/36) for composer/header/channel
alignment and [issue 29](https://github.com/yapfast/yapfast/issues/29) for UI
polish. Treat these links as a dated snapshot; check their current state before
working on those details. [AGENTS.md](../AGENTS.md) makes this workflow part of
the project's development instructions.

## Remotes

The initial checkout has:

```text
origin    https://github.com/Fayberr/YapCord.git
upstream  https://github.com/yapfast/yapfast.git
```

Remotes are local Git configuration and do not travel with a clone. In a new
clone, configure upstream once:

```bash
git clone https://github.com/Fayberr/YapCord.git
cd YapCord
git remote add upstream https://github.com/yapfast/yapfast.git
git remote -v
```

If `upstream` already exists, inspect its URL before changing anything. Never
push YapCord changes to `upstream`.

## Manual merge

Start with a clean working tree. Commit ongoing work on its own branch or stash
it deliberately. Ensure local `main` is current with `origin/main` first
(`git fetch origin`, then `git switch main` and `git merge --ff-only origin/main`).
If the fast-forward fails, inspect the divergence rather than resetting commits.

For a reviewed, conflict-free upstream update, the basic sequence is:

```bash
git fetch upstream
git switch main
git merge upstream/main
git push origin main
```

Run the applicable checks and review the resulting diff **between the merge
and the push**. At minimum, use `scripts/check --fast` in the supported build
environment. Add `scripts/check --fast --matrix` for changes to shared Matrix
paths, plus relevant fake Discord and UI tests for protocol or interface changes.
The [build guide](building.md#checks) describes the existing checks.

For substantial updates, use a review branch instead of merging straight into
`main`:

```bash
git fetch upstream
git switch -c sync/yapfast-update main
git merge --no-ff upstream/main
# Review, resolve conflicts and run the relevant checks.
git push -u origin sync/yapfast-update
```

Open a pull request into `main` and use a **merge commit**, preserving upstream
ancestry. Do not squash or rebase an upstream synchronization PR: that would
lose the ancestry that makes later merges straightforward. Do not rebase
already-published YapCord history or force-push it.

## Resolving conflicts

Use `git status` and `git diff --name-only --diff-filter=U` to identify conflicts.
Read both changes and the surrounding behavior. Preserve YapCord's README,
planning documents and future custom UI while incorporating relevant upstream
fixes. For shared adapter or core files, reconcile the actual interfaces and
behavior; neither side should be selected wholesale without review.

If upstream changes a metric wrapped by `ClientStyle`, update the inherited
branch of that style value to match the new upstream default. Keep the YapCord
value grounded in its references. Upstream comparison mode should follow
reviewed upstream changes rather than silently freezing old defaults.

After editing each conflicted file, stage that file with `git add <path>`.
Once conflicts are resolved, inspect `git diff --cached`, run the applicable
checks, and complete the merge with `git commit`. Use `git merge --abort` to
abandon an in-progress merge and return to the pre-merge state.

A future `ui/yapcord/` tree is owned by YapCord. New upstream widgets should
inform updates to it, not automatically overwrite it. Review changes to Slint
exports and Rust adapters together, as described in the
[UI architecture plan](yapcord-architecture.md).

Review `Cargo.lock`, pinned native archives and vendored patches as a unit.
Do not run an unrestricted `cargo update` to resolve a merge. Keep copyright,
license and dependency notices, and check new dependencies' licensing before
distribution. Packaging and update endpoints still need a YapCord audit before
publishing binaries.

## Tags and automation

The initial import includes upstream tags unchanged for provenance. They are
not YapCord binary releases. Fetching upstream may bring additional upstream
tags locally; pushing `main` does not publish those tags to origin. Review any
future tag publication explicitly and use a distinct YapCord release policy.

No scheduled synchronization workflow is installed. A future GitHub Actions
workflow could periodically fetch upstream, open or update a synchronization
branch and pull request, run supported checks, and require human review. It
should report conflicts, preserve merge ancestry, use minimal permissions and
never automatically replace custom UI files or merge unreviewed updates.
