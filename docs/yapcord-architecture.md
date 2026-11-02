# YapCord UI architecture

The first UI pass introduces a small presentation boundary, while continuing to
compile the inherited window and widgets. A fully separate interface remains
future work. Reviewed against upstream `b64b9a7` on November 2, 2026.

## Reuse the existing core

Keep `crates/yapfast-discord` unchanged for authentication, gateway state, HTTP
operations and Discord voice protocol. Reuse `crates/yapfast-core` for sessions,
native media, cached data and application behavior. In particular,
[`Application`](../crates/yapfast-core/src/application.rs) already exposes
`AppState`, `Action` and `Effect`: input goes through `dispatch`, backend events
through `apply`, and the returned effects are executed by the client.

[`Backend`](../crates/yapfast-core/src/backend.rs) owns the native chat actor and
returns its event receiver from `start`. Retain that handle across navigation,
send commands through `send`, report rejected commands through
`Application::backend_failed`, and report a closed event stream through
`Application::stopped`. Keep session, draft, send-retry and voice lifecycle
behavior in the core rather than duplicating it in widgets.

## Current presentation boundary

`ui/yapcord/style.slint` owns navigation, account dock, message, composer,
typography and settings-frame metrics. The caption bar, DM heading, account popover, settings navigation and switch
faces have downstream components beside it. Small bindings in the inherited Slint components use
those values. The popover reuses status controls and existing callbacks; its
user-ID property is populated from the existing `AppState.discord_user`. The
settings shell retains section IDs and page components, and opts in only for
user settings. Server and channel editors keep the inherited frame.
`src/ui/yapcord.rs` selects the presentation at window creation;
`YAPCORD_UI=upstream` retains the inherited metrics for comparison. The adapter
selects the existing Bonfire palette only when no theme has been saved. Saved
appearance choices continue to win.

This deliberately reuses the upstream component tree instead of copying the
entire 4,000-line root window. Newly merged widgets therefore remain reachable
through the existing adapter and exports. The boundary isolates design values,
not every UI component or interaction. Shared widget changes can still conflict.

## Future custom components

Introduce distinct visual components under `ui/yapcord/` as individual areas
are redesigned, with small integration points in the inherited root. Reuse
licensed assets and rendering infrastructure. Do not introduce Discord's
proprietary artwork or fonts.

[`crates/yapfast-ui/build.rs`](../crates/yapfast-ui/build.rs) still compiles
`../../ui/yapfast.slint`, including its `live-preview` path. No second root or
build selector is needed for the first pass. If the layouts later diverge
enough to justify separate roots, normal compilation and live preview must
select the same root and preserve the adapter contract.

Initially, preserve the generated interface contract exported by
[`ui/yapfast.slint`](../ui/yapfast.slint): `YapfastWindow`, its properties and
callbacks, exported row structs, and globals such as `Theme`, `PictureStore`
and `Autoscroll`. Keeping that contract lets the existing adapter drive a
different component layout without renaming crates or rewriting backend code.
Slint-generated structs have module-specific Rust types, so separately compiling
two windows does not automatically make their adapters interchangeable.

## Files that would still need integration changes

| File or area | Likely future change |
| --- | --- |
| `crates/yapfast-ui/build.rs`, its `Cargo.toml`, root `Cargo.toml` | Only if separate roots become necessary: select and propagate the interface option while preserving pins and patches |
| `src/ui.rs` | Connect the selected window and preserve effects, event reception and desktop lifecycle |
| `src/ui/callbacks.rs`, `src/ui/refresh.rs` | Bind new inputs and present newly exposed state when the window contract changes |
| `src/ui/messages.rs`, `pictures.rs`, `theme.rs`, `menus.rs` and related adapter modules | Adjust presentation where layouts, row data or interactions diverge |
| `src/ui/tests.rs`, UI probes under `testing/` | Validate the chosen interface and its accessibility, navigation and interactions |
| Packaging and desktop integration | Audit names, identity, data locations, icons and update URLs before distributing YapCord builds |

The root adapter imports `yapfast_ui::*` and directly uses generated window
types throughout its modules. It is not a framework-neutral presenter today.
Preserving its contract reduces changes but does not eliminate all coupling:
focus, selection, scrolling, list virtualization, popup geometry and picture
delivery also connect Rust and Slint. Those behaviors need explicit regression
checks as components change.

If a later design requires a substantially different contract, introduce a
YapCord adapter module alongside the existing adapter and a narrow selection
in `src/main.rs`. Reuse the core APIs and extract only demonstrably shared
presentation helpers. Avoid copying the whole adapter up front or introducing
a generic abstraction before its requirements are known.

## Keep upstream merges manageable

Concentrate visual changes in `ui/yapcord/`. Keep integration and adapter
edits small, with separate commits for upstream fixes and YapCord presentation.
Keep crate names, paths, feature defaults and dependency versions unless a
specific reviewed change requires otherwise. Preserve the patched Slint code
and native media stack.

Use the [merge-based synchronization process](upstream-sync.md). New upstream
Slint components are references to review and adapt, not replacements to copy
over custom components. A separate UI directory reduces textual conflicts;
behavioral compatibility still needs review and testing.

## Expose new upstream features deliberately

For each upstream feature, trace its path from protocol events and commands to
`Application` state/actions/effects, then to the adapter and Slint contract.
Merge the backend and application changes first as part of the reviewed update.
Add the matching properties, rows, callbacks and visual controls to YapCord's
interface, keeping permission and validation decisions in the shared core.

For example, a new message action needs its shared `Action` and backend command,
an adapter callback, and an accessible menu entry in the custom component.
Pure protocol or security fixes may need no visible control. A backend merge
alone must not be described as custom UI support for a feature.

Retain upstream core tests, add focused adapter checks when behavior changes,
and use the existing preview and fake Discord harness for interface validation.
Run `scripts/check --fast` and, when shared Matrix code changes,
`scripts/check --fast --matrix`. See the inherited
[architecture](architecture.md), [feature workflow](discord/adding-a-feature.md)
and [build guide](building.md) for the current implementation.
