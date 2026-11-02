# YapCord

A native Discord client, built on [Yapfast](https://github.com/yapfast/yapfast), with a familiar desktop experience as its guiding goal.

YapCord aims to bring Discord's familiar layout, spacing, navigation and interactions to a lightweight application without Electron. It is an independently maintained downstream project that preserves Yapfast's original history and credits its developers for the foundation.

## Why YapCord?

Yapfast provides a substantial native foundation, with careful attention to efficiency and performance. YapCord builds on that work with a specific design direction: an interface that feels as close as reasonably possible to the official Discord desktop client.

That means treating visual hierarchy, predictable navigation and everyday interactions as part of the product, alongside resource usage and responsiveness. The goal is to make a lightweight client feel familiar from the first conversation. This is a different interface direction, with respect for Yapfast's design and the work behind it.

## Project status

**Initial setup.** The YapCord-specific interface has not been implemented. The application currently retains Yapfast's interface, backend, package names and build infrastructure.

The initial YapCord changes, dated November 2, 2026, are limited to this README and developer documentation. A local Windows development build has since been cross-compiled on ARM64 Linux and passed its native Windows build smoke check; see the [build record](docs/windows-arm64-build.md). No prebuilt YapCord downloads or releases are published, and no YapCord performance improvements or benchmarks have been independently verified. Historical tags come from upstream and do not represent YapCord releases.

## Project goals

- A highly authentic Discord-like interface, including layout, spacing and visual hierarchy.
- Lightweight resource usage and responsive performance.
- A native application architecture without Electron.
- Consistent navigation and intuitive interactions.
- Continued integration of Yapfast's features, fixes and protocol updates.
- A maintainable boundary between YapCord's visual components and shared application behavior.

These are development goals, not a list of completed YapCord features.

## Inherited features and architecture

The existing code comes from Yapfast. It includes servers, channels, direct messages, friends, message history and editing, reactions, attachments, threads, forums, polls, search and server administration. Its native media implementation includes voice calls, cameras, screen sharing and stream viewing. Feature support and platform limitations are described in the inherited [Discord documentation](docs/discord/README.md); inclusion here is not a new runtime validation by YapCord.

The application is written in Rust, with a Slint interface rendered through Skia. Its main boundaries are:

| Component | Responsibility |
| --- | --- |
| `crates/yapfast-discord` | Discord authentication, gateway, HTTP API and voice protocol |
| `crates/yapfast-core` | Application state, actions, backend services and native media |
| `crates/yapfast-ui` and `ui/` | Compiled Slint interface and visual components |
| Root executable and `src/ui/` | Desktop integration and the adapter between application state and Slint |

The default build enables desktop Discord support. Matrix remains an optional inherited Cargo feature. No new UI framework or plugin system has been added.

See the inherited [architecture guide](docs/architecture.md) and the proposed [YapCord UI approach](docs/yapcord-architecture.md).

## Build it yourself

There are no published YapCord downloads. Build from source using Yapfast's existing toolchain. The documented Nix development environment targets **x86_64 Linux** and pins Rust 1.97.1, Slint 1.18.1 and the native dependencies. A desktop session is needed to open the window.

```bash
git clone https://github.com/Fayberr/YapCord.git
cd YapCord
git remote add upstream https://github.com/yapfast/yapfast.git

# Preview the inherited interface without an account
nix develop path:./nix --command cargo run --locked -- --preview

# Run the default desktop Discord build
nix develop path:./nix --command cargo run --locked

# Build an optimized executable at target/release/yapfast
nix develop path:./nix --command cargo build --locked --release

# Format check, documentation links, Clippy, tests, build and smoke test
scripts/check --fast
```

The executable is still named `yapfast`; internal names remain unchanged to preserve build compatibility. The first build downloads Rust and native dependencies and compiles C++. On machines with limited memory, the upstream guide recommends `CARGO_BUILD_JOBS=2`.

For Linux builds without Nix, native dependency requirements, optional Matrix support and Windows cross-building, follow [Building](docs/building.md), [Development](docs/development.md) and [Windows builds](docs/windows-beta.md). Packaging still uses upstream names and some upstream download or update locations; it needs a separate audit before any YapCord distribution. No macOS support is claimed.

The [foundation verification record](docs/yapcord-foundation.md) describes the checks performed for this setup and the host limitations.

## Development and upstream updates

Keep backend changes small and independently reviewable. The [UI architecture plan](docs/yapcord-architecture.md) describes how a future YapCord interface could live beside the upstream Slint files while reusing the application model.

Use the [upstream synchronization guide](docs/upstream-sync.md) to merge Yapfast updates without rewriting published history. Git remotes are local configuration, so each new clone needs the `upstream` remote shown above.

## Upstream and acknowledgments

YapCord is based on **[Yapfast](https://github.com/yapfast/yapfast)**. Its original developers and contributors created the existing client, protocol implementation, native media stack, interface and development tools. Their commits, authorship, license files and notices are preserved. Existing Yapfast functionality is their work, not an independent YapCord implementation.

YapCord is a separate GitHub repository rather than a member of GitHub's fork network. This hosting choice does not change its upstream origin or licensing obligations. The intention is to incorporate upstream improvements through reviewed merges over time.

The inherited project also builds on Slint, Skia, LiveKit/WebRTC, DeepFilterNet and the optional Matrix stack, and credits [Discord Userdoccers](https://docs.discord.food) for its community protocol documentation. Dependency and asset licenses remain with their respective files.

## Disclaimer

YapCord is an unofficial third-party client. It is not affiliated with, sponsored by or endorsed by Discord. Discord is a trademark of Discord Inc.

Third-party clients can stop working when Discord changes its services and may involve account restrictions or termination under Discord's terms. Use them with an understanding of those risks. YapCord makes no guarantee of compatibility or account safety.

## License

YapCord continues under the **GNU General Public License, version 3 or later (`GPL-3.0-or-later`)**, as declared by Yapfast's package manifests. The original [LICENSE](LICENSE), copyright notices and bundled license files are preserved.

Dependencies and bundled assets retain their own licenses, including those in `vendor/`, [the fonts](ui/fonts/LICENSE-OFL.txt) and [the icons](ui/icons/LICENSE). Optional Matrix builds include MatrixRTC code offered under AGPL-3.0-only or a separate commercial license; the open-source build uses the AGPL option. Preserve the applicable notices, license texts and source obligations when distributing builds. See [dependency sources](docs/building.md#dependency-sources) and [packaging](docs/packaging.md) for the inherited build and distribution details.
