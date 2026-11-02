# YapCord interface development

The current presentation pass targets the main window's proportions, system
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
user choices. Windows uses its installed Segoe UI font. Other platforms retain
the inherited typeface for now. Discord's proprietary font and artwork are not
bundled. Font rendering will consequently differ. Inline custom emoji still
use the inherited bitmap-font metrics; baseline alignment with the new typeface needs
focused visual review before claiming typography parity.

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
DM home. Folder previews, badges and selection indicators follow those tile
bounds; upstream mode keeps its 48px tiles. The rail remains 72px wide.

The account dock is an inset 60px card with 8px side/bottom margins and a
40px avatar. The microphone, headphone, device menus and settings controls
keep their existing callbacks. The status selector remains the inherited menu;
this is not yet Discord's richer account popover.

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
against the same data directory. The account menu, rich message cards and most settings controls remain
inherited components. Upstream mode retains the original title bar and desktop
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
