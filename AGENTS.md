# YapCord development

## Check upstream before building a feature

- At the start of each development session, fetch `upstream` and inspect new
  commits. Review and merge suitable updates regularly, before each UI
  milestone and promptly for relevant security or protocol fixes.
- Before implementing an area, inspect Yapfast's current code, documentation,
  open issues and pull requests for that area. Reuse existing work. Record
  whether the work belongs upstream, is awaiting an upstream change, or is
  specific to YapCord's Discord-fidelity interface.
- An open upstream PR is evidence of work in progress, not a shipped feature.
  Review it before deciding to wait or adapt it. Do not automatically merge
  unreviewed branches or repeatedly implement functionality upstream provides.
- Account popovers are one example: check the existing profile/status code and
  upstream plans before writing a replacement.
- Preserve merge ancestry and use the [upstream guide](docs/upstream-sync.md).
  No scheduled synchronization or automatic merging is configured.

## Current development priority

The owner has authorized starting the Discord-fidelity interface. Match the
supplied references in layout, spacing, typography and interactions. Keep
visual differences separate from missing backend capabilities, and preserve
existing functions while changing presentation. Reuse Yapfast's Bonfire
palette rather than duplicating an existing Discord-like theme.

Keep YapCord presentation decisions under `ui/yapcord/` where practical and
keep the integration changes to inherited files small. Preserve an upstream
presentation mode for comparison and regression checks. Do not rename crates,
replace the UI framework or refactor the protocol/backend for visual changes.

## Verification and private references

- Use equal viewport size, scale, content and UI state for visual comparisons.
  Pixel differences guide review; they do not establish interaction parity.
- Owner screenshots contain personal conversations and account settings. Keep
  them and derived comparisons private in ignored local storage. Never add
  them to this public repository or turn their content into test fixtures.
- Use synthetic preview/fake Discord content for automated tests and public
  examples. Do not send messages or modify a real account for UI testing.
- Keep source work in the canonical Linux checkout. Use an authorized build
  host with a prepared toolchain and cache. Native Windows builds are allowed
  when the owner permits them; keep smoke/UI checks lightweight.
- Preserve tests and dependency pins. Use focused checks while iterating and
  run applicable final checks. Document host limitations and existing warnings.
- Do not commit generated binaries, caches, runtime data or credentials.
