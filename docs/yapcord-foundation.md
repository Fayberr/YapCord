# Initial foundation and verification

Recorded November 2, 2026. This is a documentation-only downstream setup;
it does not certify a runnable build or a redesigned interface.

Follow-up: a Windows development build was subsequently cross-compiled on
ARM64 Linux and passed the native Windows smoke check. The
[build and deployment record](windows-arm64-build.md) describes that result.
The original setup checks and limitations below remain a historical record.

## Provenance and scope

- Upstream: <https://github.com/yapfast/yapfast>.
- Imported `main`: `70f9369f394e1875cad8ef9e56782e06c93cc796`.
- The full clone contains 621 original commits and nine upstream tags.
  All original branch tips are reachable from the imported `main`.
- YapCord adds a rewritten README, a future UI architecture plan, a manual
  upstream synchronization guide and this verification record.
- Source code, UI files, manifests, lockfiles, build scripts, tests, vendored
  code, packaging, license files and existing notices remain unchanged.
- The original README is retained in Git history at the imported commit.
  Upstream tags retain their original objects and authorship; they do not
  imply any published YapCord binaries.

The repository is created independently through GitHub's repository creation
API, not its fork API. The local checkout uses `origin` for YapCord and
`upstream` for Yapfast. New clones must configure upstream themselves; see
[upstream synchronization](upstream-sync.md).

## Checks performed

| Check | Result |
| --- | --- |
| `cargo fmt --all -- --check` | Passed with the pinned Rust 1.97.1 toolchain |
| `scripts/check-doc-links` | Passed for the README and developer documentation |
| `git diff --check` | Passed |
| `vibe-check` on each changed Markdown file | Passed |
| Source and license comparison to the imported commit | No changes outside the four intended documentation files |
| Git ancestry, original branch tips and tag objects | Preserved without rewriting commits |
| GitHub metadata after push | Public, default branch `main`, `fork: false`, no parent or source repository |
| Upstream fetch and merge on the initial YapCord commit | Fetch succeeds; merge reports already up to date |

## Build and test limitations

The verification host is Linux ARM64 (`aarch64`). It has no usable `nix`
executable or `rustup` command on PATH. `cargo fmt` nevertheless located and
installed the pinned toolchain through its formatter proxy and completed.
The inherited `nix/flake.nix` development shell targets `x86_64-linux` and
supplies pinned native media and renderer dependencies.

`scripts/check --fast` exited with status 126 before running its checks:

```text
scripts/check: line 13: exec: nix: cannot execute: Is a directory
```

There is no usable Nix executable on PATH; the repository has a directory
named `nix`. The diagnostic is a host prerequisite failure, not a passing
build or test result.

A fallback attempt with
`cargo test --locked --offline --workspace --exclude feature-union` exited
with status 101 before compilation. Cargo could not check out the uncached
Git dependency `const_panic` at
`e0b317a9a7bde2d48a7d15b6a60d70e4a41d3b5f` in offline mode. This does not
show that the dependency is unavailable online or that a test failed.

Clippy, compilation, runtime smoke checks, fake Discord integration tests,
and interactive interface, voice and screen-sharing checks were not completed.
Run the inherited checks in the supported x86_64 Linux environment before
claiming a verified build. No application launch, account sign-in or binary
release was performed during this setup.

## Follow-up boundaries

The future Slint interface remains a [proposal](yapcord-architecture.md).
Packaging and desktop identity still refer to Yapfast, including some update
or download locations. Audit those paths, distribution licenses and release
behavior before publishing YapCord binaries. The inherited Nightly workflow
is manually triggered and remains unchanged; no scheduled upstream sync or
new release workflow was introduced.
