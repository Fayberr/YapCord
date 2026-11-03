# UI fonts

YapCord uses DM Sans, selected by the project owner as an open-source
alternative to Discord's custom gg sans. The unmodified variable TTF files
`DMSans[opsz,wght].ttf` and `DMSans-Italic[opsz,wght].ttf` come from
[Google Fonts](https://github.com/google/fonts/tree/5b35b7208dd4100571326fdf37f030b32a524232/ofl/dmsans)
at commit `5b35b7208dd4100571326fdf37f030b32a524232`. They provide upright
and italic faces with variable weights and optical sizes, and are embedded
by Slint. The original copyright and license are preserved in
[LICENSE-OFL-DMSans.txt](LICENSE-OFL-DMSans.txt), the SIL Open Font License 1.1.
Binary packages include the license and this provenance note in `licenses/fonts/`.

No proprietary Discord or Windows font files are bundled. Upstream presentation
mode retains Atkinson Hyperlegible Next and its metrics. DM Sans is an
alternative, not an exact reproduction of gg sans.

Atkinson Hyperlegible Next by the Braille Institute, the UI's typeface: the
static TTF styles Regular, Italic, Medium, Bold, Bold Italic and ExtraBold,
copied unmodified from the googlefonts/atkinson-hyperlegible-next repository at
commit 7925f50f649b3813257faf2f4c0b381011f434f1 (version 2.001, through
nixpkgs' `atkinson-hyperlegible-next`) on 2026-10-07. They're embedded in the
Yapfast binary by the Slint compiler. `LICENSE-OFL.txt` is their SIL Open Font
License 1.1, which permits embedding, modifying and redistributing them,
including in a public repository.

Satoshi by Indian Type Foundry was the second choice. Its ITF Free Font License
2.0 forbids redistributing the files through a public repository, so they
aren't here. To try it, download the static TTF styles Regular, Italic, Medium,
Bold, Bold Italic and Black from Fontshare
(https://www.fontshare.com/fonts/satoshi) into this folder, and follow the
comment at the top of `ui/yapfast.slint`.

## Display name fonts

`DisplayName-*.ttf` are the fonts Discord's client draws display name styles
in, for the ten of its eleven that are redistributable: Sakura (Cherry Bomb
One), Jellybean (Chicle), Modern (MuseoModerno), 8Bit (Pixelify Sans),
Vampyre (Sinistre), Tempo (Zilla Slab), Monkey Bars (Playpen Sans), Mainframe
(Orbitron), Headbang (New Rocker) and Journal (Kalam). Each is an SIL Open
Font License 1.1 font, taken from Discord's web client (the `@font-face`
rules of its stylesheet, `https://discord.com/assets/<hash>.woff2`), whose
name tables carry the copyright lines in
[LICENSE-OFL-DisplayNames.txt](LICENSE-OFL-DisplayNames.txt) and link the
OFL. Discord's copies are renamed where the licence reserves a name and
subset to Latin; they were converted from WOFF2 to TrueType, and Tempo,
Monkey Bars, Headbang and Journal subset further to Basic Latin, Latin-1 and
Latin Extended-A and common punctuation, to keep them to 40 KB or so each
(Monkey Bars, 180 KB). They are embedded by Slint, so they take no memory
until a styled name needs one. A name outside that range falls back to the
usual font, as Discord's client does for scripts the font doesn't cover.

The eleventh, Medieval (Discord's name for Max Lillo's Néo-Castel), is not
bundled: its name table links the OFL, but I could not confirm Max Lillo
publishes it under that licence, and a name styled with it shows in the usual
font. Binary packages include these notes in `licenses/fonts/`.
