# End-to-End Workflow

## Contents

1. Reconnaissance
2. Text extraction
3. Translation and terminology
4. Executable patching
5. Fonts and symbols
6. Image localization
7. Display configuration
8. Runtime debugging
9. Packaging

## 1. Reconnaissance

- Hash all files before modification.
- Record PE architecture, imported graphics/text APIs, pack magic, resource paths, and configuration files.
- Search the executable for CP932 strings and direct references.
- Index every KCAP archive before extraction.
- Keep an immutable original, a working copy, and timestamped milestones.

## 2. Text Extraction

Separate text into plain archive text, fixed-width executable strings, text baked into DDS images, configuration UI text, and symbols dependent on source byte encoding.

Assign stable IDs such as `exe::0x00123456` or `pack::PATH::line:42`.

For executable text, store file offset, original CP932 byte capacity, source character count, registration/draw references, translated byte encoding, and padding policy.

## 3. Translation And Terminology

- Create a terminology CSV before full translation.
- Lock names, titles, abilities, card names, difficulty labels, and system vocabulary.
- Compare original and translation together during review.
- Validate omissions, additions, speaker tone, relationships, punctuation, line count, and encoded byte count.
- Keep logical Unicode text separate from final game-byte encoding.

## 4. Executable Patching

- Patch a known working executable, not a repeatedly edited unknown build.
- Verify the existing bytes before replacement.
- Reject translated bytes that exceed the original slot.
- Preserve unrelated title, resolution, charset, and launcher patches.
- Disassemble direct string references when runtime behavior differs from `strlen` expectations.

Use `patch_fixed_strings.py` for deterministic writes. Use `find_pe_xrefs.py` to identify code that registers or draws a string.

## 5. Fonts And Symbols

The game may read CP932 bytes, run under a CP936 locale, pass the resulting ANSI word to `GetGlyphOutlineA`, and select a bundled font by family name. This can turn a source symbol into a Chinese-looking Unicode alias. Preserve the byte pair and map that alias to the intended glyph in the replacement font.

Preserve expected names, include all translated glyphs, protect required characters from compatibility aliases, and test through the same ANSI GDI API and charset as the game.

## 6. Image Localization

- Decode DDS with a format-aware library.
- Keep original width, height, pixel format, mip count, and alpha.
- Detect safe text regions from the original.
- Prevent punctuation-only lines and split name/title combinations.
- Use measured text layout, not fixed character counts.
- Compare output against source and in-game screenshots.

## 7. Display Configuration

- Determine the original logical canvas, often 640x480.
- Keep the aspect ratio when offering higher resolutions.
- Patch launchers and runtime settings consistently.
- Verify windowed and fullscreen behavior.

## 8. Runtime Debugging

Capture exact navigation steps, process responsiveness, Event Viewer/WER records, focus state, screenshots before failure, and binary/resource differences from the last stable build.

Classify failures as crash, hang, render corruption, resource-load failure, or focus/device-reset failure.

## 9. Packaging

Include only runtime-required files, translated packs, launcher, manuals, configuration directories, and a user-facing note. Exclude backups, dumps, screenshots, API keys, extracted source assets, build caches, and old archives. Generate SHA-256 manifests and launch from the final directory.
