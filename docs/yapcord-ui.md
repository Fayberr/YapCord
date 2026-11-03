# YapCord interface development

The current presentation pass targets the main window's proportions,
typography, default palette, window chrome, navigation and composer spacing.
It also adjusts message grouping and the docked profile's framing. It is an
initial iteration, not a claim of pixel or interaction parity with Discord.
Rich message cards, account popovers and settings navigation still need their
own comparisons.

## Reference and ownership decisions

The owner's November 2026 Windows references place the chat column at about
376 logical pixels from the left: a 72px server rail and a 304px navigation
list. They also show an approximately 60px composer with 8px surrounding space.
These are starting measurements for the supplied scale, not universal values
for every display or Discord version. Saved sidebar widths and themes remain
user choices. YapCord now embeds DM Sans, an open-licensed approximation rather
than Discord's custom gg sans. Default message text and navigation labels use
15px instead of 16px. Explicit small (14px) and large (18px) message choices
remain available. Upstream mode retains Atkinson Hyperlegible Next at 16px.
Font provenance and both licenses are recorded in [the font directory](../ui/fonts/README.md).
No proprietary Discord font or artwork is bundled. Rasterization and glyph
shapes still differ from Discord. Inline custom emoji retain the inherited
bitmap-font metrics, so mixed-text baselines need further visual review.


Reuse Yapfast's existing Bonfire palette. Keep its message, navigation, voice,
settings and account actions connected to the existing adapter. The default
appearance is YapCord's; `YAPCORD_UI=upstream` selects the inherited metrics and
typeface for regression work. This does not turn the downstream tree into an
unmodified upstream build, or override saved preferences.

Before changing each area, follow [the upstream review workflow](upstream-sync.md).
At the initial review, [upstream PR 36](https://github.com/yapfast/yapfast/pull/36)
was open and proposed header, channel and composer alignment adjustments.
Do not duplicate its channel indentation work in this pass. The composer
spacing here is measured for YapCord and overlaps that proposal; reconcile the
small integration hook when it lands. No account-popover backend replacement
is part of this pass. The larger composer metrics apply to the main chat field;
thread and forum editors keep their inherited sizing until reviewed separately.

## Window and conversation presentation

The second pass uses a 32px integrated caption bar on Windows by default,
with minimize, maximize/restore, close, drag and double-click actions routed
through the inherited adapter. `ui/yapcord/window-bar.slint` owns its appearance.
The existing Appearance setting can restore the system title bar. Explicit
saved choices win; Linux keeps its existing desktop detection and other
platforms retain their inherited frame policy. Closing still follows the
existing tray/quit behavior. Native resizing uses the inherited edge handlers.

The rail uses 40px rounded server tiles, 8px row gaps and a separator below
the pinned DM home. A leading divider from the inherited model is hidden
in YapCord mode. A divider after unread DMs remains, separating them from
servers. Folder previews, badges and selection indicators follow those tile
bounds; upstream mode keeps its 48px tiles. The rail remains 72px wide.

The account dock is an inset 60px card with 8px side/bottom margins and a
40px avatar. The microphone, headphone, device menus and settings controls
keep their existing callbacks. The account menu now uses the downstream popover described below.

On the DM home, the existing room filter moves into the 48px header. Its
label says what it actually searches: conversations. Friends and Requests stay
available, followed by a Direct Messages heading with the existing new-message
and add-friend actions. `ui/yapcord/dm-heading.slint` owns that heading. Only
implemented destinations appear; there are no placeholder shop or Nitro links.
DM rows use a 44px height and reduce the selected name's weight. The main
composer relies on its existing Enter/Shift+Enter handling instead of a
persistent send button in YapCord mode.

Message groups have a 16px leading gap, while the author and body share a
compact vertical rhythm. Timestamps use a smaller caption size. Attachment,
reply, selection and menu behavior remain inherited. The 320px docked profile
column leaves a 304px card after its 8px margins, with an inset rounded surface
and an explicit View Full Profile action that invokes
the existing profile callback. Its content remains scrollable above that action.
Colors continue to come from the chosen theme; no user banner or decoration
is invented.

Upstream was fetched again for this pass on November 2, 2026. Main remained
at `b64b9a7`; PR 36 was still open. No shipped upstream account-popover or
caption-bar replacement was found. These changes are downstream presentation
work, while protocol, media, core state and dependency pins remain unchanged.

## Account popover and user settings

The third pass follows the owner's additional Discord references. The account
popover lives in `ui/yapcord/account-popover.slint`: a 300px card with an 80px
avatar, the account name, available custom status and game activity, and grouped
profile, presence and settings actions. Status choices reuse `StatusOption`;
opening the card resets the expanded status list. Changing presence, editing
profiles and custom status keep their existing callbacks. Copy User ID uses
`AppState.discord_user` through one adapter property and the inherited clipboard
function. It is omitted when no ID is available. The card scrolls within the
space above the account dock on shorter windows.

The header uses a neutral theme surface. The account summary does not provide
banner, biography, pronoun or badge data, so those fields are absent. There are
no placeholder subscription, account-switching or billing actions. Fetching a
richer own profile remains future work and should reuse upstream profile APIs.

User settings now use a 1400px modal with a 72px vertical outer inset at the
reference viewport. The 266px sidebar contains the account identity, existing
profile editor action, a case-insensitive filter over supported page names and
40px navigation rows. A 48px page header holds the title and close action;
the body centers a column up to 696px wide. Navigation and content scroll
independently. Switch faces move to the right and use 48px by 24px bounds,
while their focus, disabled and controlled-state behavior remains upstream.

`SettingsFrame` opts into this shell only through `SettingsScreen`. Server and
channel settings keep their existing frame and content-bar coordinates. The
section IDs, settings page contents, device refresh and Escape handling remain
inherited. Adding an upstream settings page requires adding its destination to
`ui/yapcord/settings-nav.slint` and its header title in `SettingsScreen`; merging
a backend feature alone does not create a new custom navigation entry.

Upstream was checked again before this work: main remained at `b64b9a7`, PR 36
was still open, and no open PR supplied this account/settings replacement.
[Issue 64](https://github.com/yapfast/yapfast/issues/64) discusses Discord design
parity and had no answer at the time of review. This is not evidence that
upstream has ruled out similar work; check again before the next milestone.

## Screenshot comparison

Install Pillow in your development environment if it is not already available.
The comparison tool takes existing screenshots and never resizes them:

```bash
python3 scripts/compare-ui.py reference.png candidate.png \
  --output .local/visual/comparison
```

It writes a 50 percent overlay, a difference image and a JSON report. The
report includes mean absolute channel error and the fraction of unmasked
pixels whose largest channel difference exceeds the threshold (16 by default).
Those values describe the images, not usability or an overall fidelity score.

For meaningful comparisons, use the same viewport dimensions, display scale,
window state, theme, locale, scroll position and synthetic content. Freeze
animations and allow loading to finish. Capture the app window only. Compare
regions such as navigation, header and composer separately when content cannot
be normalized. Different text, avatars or scroll positions dominate a whole
window pixel difference even when the layout is close. Check that captures
contain the rendered application before comparing: Windows capture APIs can
return a correctly sized blank frame while a window is starting or resizing.
Retry the capture rather than interpreting that as a client regression.

Optional masks exclude unstable or private regions from both images and from
the metric denominator. Supply a JSON array of integer `[x, y, width, height]`
rectangles inside the image:

```bash
python3 scripts/compare-ui.py reference.png candidate.png \
  --mask .local/visual/mask.json --threshold 16 \
  --output .local/visual/comparison
```

Masks are exclusions from analysis, not a redaction/export feature. Keep the
input screenshots and all derived output private. Owner-provided references
contain personal messages and account details and must never enter Git history.
Use ignored `.local/visual/` storage; use synthetic preview or fake Discord
content for public fixtures. Do not declare a zero-difference gate between
native and Discord text renderers. Review geometry, contrast, focus, keyboard
navigation and working actions alongside the images.

The comparison tool's known-pixel tests run independently of Rust:

```bash
python3 -m unittest discover -s testing -p 'test_visual_compare.py'
```

## Upstream appearance on Windows

For an isolated comparison, launch the same executable with synthetic content
and a separate data directory. This leaves your signed-in profile alone:

```powershell
$env:YAPCORD_UI = 'upstream'
.\yapfast.exe --preview --data-dir .\preview-upstream
Remove-Item Env:YAPCORD_UI
```

Run a second preview without that environment variable and with a different
empty data directory for YapCord's defaults. Do not run two normal sessions
against the same data directory. Rich message cards and most settings controls
remain inherited components. Upstream mode also retains the original status
menu, settings navigation, title bar and desktop
frame policy as well as the original widget metrics.

## Build and verification limits

Development uses the inherited `fast` profile. Its Slint code is unoptimized;
use `measure` or a release build for runtime performance comparisons. Switching
to a profile for the first time creates a separate Cargo cache even if a
release build already exists. Subsequent edits reuse that profile's cache.

The native `scripts/check --fast` entry point needs the upstream x86_64 Linux
Nix shell. On this ARM64 host it fails before running checks because the flake
does not expose `devShells.aarch64-linux.default`. Windows checks use the
[local ARM64 cross-build environment](windows-arm64-build.md) instead; record
which checks were actually run rather than calling that a native Linux pass.


## Existing Windows test limitations

The baseline executable, before the presentation patch, has four failing
unignored tests on this cross-build setup:

- `paste::tests::reads_local_files_from_a_uri_list`: Windows file URI handling.
- `protocol::windows::tests::recognises_its_own_registered_command`: command quoting.
- Two `ui::pictures` animation tests read a fixture using the embedded Linux
  `CARGO_MANIFEST_DIR`, which does not exist on the Windows test machine.

Five desktop integration tests remain intentionally ignored by the upstream
suite because they change registry entries, access the clipboard or type into
the desktop. Do not enable those as part of visual testing. The inherited
synthetic preview also displays a connection-stopped banner. These findings
are separate from interface fidelity and do not constitute account, voice or
screensharing validation.


Cross-target Clippy with `-D warnings` is also blocked by inherited Windows
unused-code errors: `Style.text` and `body` in `src/notify.rs`, and `PICTURES` in
`src/paste.rs`. Those files are unchanged from upstream. Keep the strict gate;
do not suppress these warnings to describe this development build as clean.
Appearance-only tests use `Layout::apply_appearance` to avoid changing
process-wide microphone and speaker gains while volume tests run in parallel.


## Second-pass verification record

The Windows cross-target test build completed on ARM64 Linux in 8 minutes
29 seconds with cached dependencies. The final rail/profile correction rebuilt
the UI tests in 8 minutes 48 seconds, followed by a 43-second application build.
Windows executed the tests without compiling: 167 passed, four
baseline tests failed as listed above, and five integration tests stayed
ignored. All six YapCord-specific tests passed, including the caption controls,
inset account controls, DM-heading actions and the docked full-profile action.
The comparison tool's four known-pixel tests also passed. Native Windows
preview checks verified integrated-frame geometry and maximize, restore,
minimize and close actions. Synthetic DM, server and settings captures were
reviewed at the reference viewport. Pointer dragging/resizing and OS snapping
still need interactive review.

These checks exercise the inherited UI callback contract and the presentation
changes. They do not validate real-account messages, voice, screen sharing,
Discord policy compatibility or a complete Discord replica.

## Third-pass local verification

The next pass was developed and reviewed entirely on ARM64 Linux. An isolated
Slint 1.18.1 interpreter harness loaded the actual interface with the patched
core and a headless software renderer, using synthetic account data. Before
the implementation, the reference-position Appearance action and the new
account-settings destination failed their checks. Afterward, local scenarios
verified settings navigation and filtering, device refresh, Escape and header
close, profile editing, status selection, user-ID clipboard contents and switch
state/callbacks. The inherited status-menu actions also passed.

Both overlays were reviewed at 1920x1080 and the application's 800x560 minimum.
An equal-state settings capture in upstream mode matched the pre-pass image
with zero changed pixels. This is one Linux-rendered state, not complete
regression coverage or a Windows screenshot comparison. Owner references and
all derived comparisons remain private.

Two production Rust UI regression tests cover navigation/search/close and
account-menu clipboard/settings behavior. Windows execution is deferred for
this pass under the owner's temporary local-only rule. The earlier Windows
suite results above belong to the second pass. Linux software previews do
not establish Windows font rendering, native frame behavior or real-account
compatibility for these changes.

The production Windows-target test executable cross-compiled successfully on
Linux in 8 minutes 33 seconds after clearing only the generated UI incremental
cache. A retained-cache attempt had been stopped after sustained memory
reclaim. Rust dependency and native-library caches were preserved. The build
reported the same inherited Windows unused-code and missing CRT PDB warnings;
it did not execute the Windows tests.

The application executable then cross-compiled in 40 seconds. Strict
cross-target Clippy was attempted and remains blocked by the same three
inherited unused-code errors in `src/notify.rs` and `src/paste.rs` listed above.
Those files are unchanged, and the warning gate was not weakened. Formatting,
documentation links, visual-tool tests, diff checks and vibe-check passed.


## Font and rail follow-up

The owner reported oversized, different typography, a duplicate rail separator
and stutter when scrolling servers. The font and line changes above address
the first two reports. The home button remains pinned by design. The rail is
still virtualized and uses the inherited wheel animation; no separate input
smoothing, backend changes or speculative renderer patches were added.

The initial review found upstream at `b64b9a7`. The next-day check found
`73a4316`, which adds camera and OBS virtual-camera Go Live sources. It was
merged without conflicts before final validation; its backend and sharing-menu
changes are inherited upstream work. [Font customization issue 7](https://github.com/yapfast/yapfast/issues/7)
discusses future work but has no shipped implementation in that revision.
The downstream default does not add a competing font-settings system.

The installed development build used `fast`, which deliberately compiles
`yapfast-ui` without optimization. A synthetic Skia software benchmark is
available for checking the cost of that choice. Compile it on the build host:

```bash
cargo test --locked --profile fast --bin yapfast \
  --features i-slint-backend-testing/renderer-skia --no-run
```

Run the resulting test executable with:

```bash
<test-executable> yapcord_server_rail_scroll_snapshot_benchmark \
  --ignored --nocapture --test-threads=1
```

For a comparison that optimizes only the generated UI, add
`--config 'profile.fast.package.yapfast-ui.opt-level=3'` to the compilation
command. Use the same source, machine and benchmark fixture for both builds.
The test draws 240 full-window snapshots at 2560x1440 while scrolling a
500-server synthetic model and the existing fictional preview conversation.
It measures CPU-side snapshot throughput, not
compositor presentation or the owner's live-client frame rate. Normal
`release` builds already optimize the UI. Keep `fast` for iteration and use
an optimized artifact when judging interactive smoothness.

A separate Windows title-bar artifact remains unresolved: resizing cleared a
white strip in the owner's session. That observation suggests incomplete
repainting, but does not establish its cause. This pass makes no native frame
or renderer changes to address it.
