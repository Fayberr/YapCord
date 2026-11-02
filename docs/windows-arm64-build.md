# Windows builds from ARM64 Linux

Verified November 2, 2026, against source commit
`4a994c2f5ecfb4bf58567303f37465152eb2724a`. The Windows x64 executable was
compiled on Linux ARM64, packaged, transferred and smoke-tested on Windows.
No application, interface, dependency or vendored source changes were required.

## Build environment

The inherited Windows shell in `nix/flake.nix` hardcodes `x86_64-linux`.
For this build, an ignored local copy used `aarch64-linux` instead and omitted
Wine and Xvfb. These are unnecessary for the portable ZIP; generating the
Inno Setup installer through Wine is a separate task.

Nix 2.35.4 was installed using the official single-user installer. The build
used the repository's unchanged Nix lock and pinned inputs, including Clang
21.1.7, Rust 1.97.1, Slint 1.18.1, Skia 0.153.3 and the Windows WebRTC archive.
The environment supplied native ARM64 tools; the output target was
`x86_64-pc-windows-msvc`. No x86 emulation or Windows compilation was used.

## Recreate the local environment

Run from the project root with Nix and rustup available. This copies the
existing development flake; it does not change the checked-in environment.
Review the substitutions again if upstream changes its flake structure.

```bash
mkdir -p .local/windows/arm64-env
python3 - <<'PY'
from pathlib import Path
import shutil

destination = Path('.local/windows/arm64-env')
for path in Path('nix').iterdir():
    if path.is_file():
        shutil.copy2(path, destination / path.name)

flake = destination / 'flake.nix'
text = flake.read_text()
changes = {
    'system = "x86_64-linux";': 'system = "aarch64-linux";',
    'zip wineWowPackages.stable': 'zip',
    '            xvfb-run\n': '',
}
for old, new in changes.items():
    if text.count(old) != 1:
        raise SystemExit('Upstream flake changed; review the ARM64 adaptation')
    text = text.replace(old, new)
flake.write_text(text)
PY
```

The native Skia helper caches its outputs under `.local/windows`. On a fresh
checkout, the following optional link keeps its large build output under
`target/`, which the workspace's source synchronization excludes. Do not replace
an existing cache directory; reuse it or move it deliberately first.

```bash
mkdir -p target/windows-skia-static-production
ln -s ../../target/windows-skia-static-production \
  .local/windows/skia-static-production
```

Build the Discord-only portable package using the inherited script:

```bash
export PATH="$HOME/.nix-profile/bin:$HOME/.cargo/bin:$PATH"
export NIX_CONFIG='experimental-features = nix-command flakes'
export CARGO_BUILD_JOBS=2

nix develop path:./.local/windows/arm64-env#windows \
  --command scripts/build-windows discord --no-installer
```

The script installs the Windows Rust target, prepares static-CRT Skia,
sources `scripts/release-env`, compiles the locked release build and packages
the executable, dependency notices, licenses and corresponding source.
The first run downloads the toolchain and Microsoft SDK. Skia's native build
uses two jobs; its archive and the Cargo artifacts are reused on later builds.

The verified run took about 17 minutes for Skia and 32 minutes for the
application release build, excluding environment setup and packaging. These
are observations from one four-core ARM64 host with the job limited to two
CPU cores, not performance guarantees. Generated Slint code briefly used
roughly 14 GB of build memory. Keep sufficient memory and disk space available.

## Outputs and development packaging

The inherited script produced:

- `target/x86_64-pc-windows-msvc/release/yapfast.exe`
- `target/dist/discord/Yapfast-0.2.0-windows-x64.zip`
- `target/dist/discord/Yapfast-0.2.0-source.zip`
- `target/dist/discord/SHA256SUMS.txt`

For the private development deployment, the portable package was wrapped as
`YapCord-dev-4a994c2f5ecf-windows-x64.zip`. Its source snapshot was included
inside the package. `SOURCE.txt` identified the YapCord commit and local source
archive instead of claiming an upstream release supplied this build. Build
metadata recorded the downstream commit and ARM64 host, and corrected the
inherited renderer description to software by default, with Direct3D 12 as the
Windows GPU option. The original executable and all dependency licenses were
preserved. This packaging adjustment did not modify application source.

Executable SHA-256:

```text
e0542f5c16a6ba0f1d871f4985178e61f69a6876785d2523eadc41984145fcde
```

The artifacts are local development outputs, not a published release. Before
public distribution, complete the broader packaging and update-location audit
described in the [foundation record](yapcord-foundation.md).

## Windows deployment and checks

The package was transferred as a file, then its archive and executable hashes
were checked on Windows before installation into the versioned directory:

```text
%LOCALAPPDATA%\Programs\YapCord\4a994c2f5ecf\
```

The YapCord Start menu shortcut targets that directory's `yapfast.exe` with:

```text
--data-dir "%LOCALAPPDATA%\YapCord\data"
```

The shortcut stores the expanded user-specific path. A separate data directory
keeps the development build's local files apart from the inherited default.
No existing installation was replaced and no startup task was added.

Native Windows verification:

```text
Yapfast 0.2.0: Tokio, LiveKit, Discord voice build check passed.
```

Formatting, documentation links, optimized compilation, package integrity,
source/license inclusion, transferred executable hash and shortcut target were
checked. The build emitted unused-code warnings in unchanged Windows paths
and LNK4099 warnings for unavailable Microsoft runtime PDB files; it completed
successfully. Those warnings are not a clean Clippy result.

The full test suite and Clippy were not run as part of this cross-build.
The smoke check does not sign in, open audio devices or establish real Discord
calls. Interactive UI, messaging, audio, cameras and screen sharing still need
live verification. See the inherited [Windows guide](windows-beta.md) for
those checks.
