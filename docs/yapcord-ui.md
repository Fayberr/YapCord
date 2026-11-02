# YapCord interface development

The first presentation pass targets the main window's proportions, system
typography, default palette and composer spacing. It is an initial iteration,
not a claim of pixel or interaction parity with Discord. Message cards,
profile panels, account popovers and the settings navigation still use inherited
components and need their own comparisons.

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
against the same data directory. The title bar, account menu, rich message
cards and most settings controls are still upstream components in this pass.

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
