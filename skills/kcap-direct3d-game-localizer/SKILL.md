---
name: kcap-direct3d-game-localizer
description: Localize legacy Windows games that store assets in KCAP archives and render ANSI text through Direct3D/GDI. Use when Codex needs to inspect, extract, translate, repack, or debug a KCAP-based game; patch fixed-width Shift-JIS/CP932 strings in a PE executable; replace an embedded font; localize DDS UI images; preserve aspect ratio; diagnose white glyph blocks, mojibake, missing music-note symbols, or focus/replay hangs; and assemble a verified release without distributing original copyrighted assets.
---

# KCAP Direct3D Game Localizer

Work from backups and preserve a byte-for-byte original. Never patch the only copy.

## Route The Task

1. Identify the executable, KCAP packs, configuration launcher, font entry, image entries, text files, save/config files, and runtime DLLs.
2. Read [references/workflow.md](references/workflow.md) before a full localization.
3. Read [references/diagnostics.md](references/diagnostics.md) when text renders as blocks, symbols become mojibake, or the game hangs.
4. Read [references/formats.md](references/formats.md) before generating task/result manifests or rebuilding archives.

## Core Workflow

1. Create timestamped backups and hash every original.
2. Index all packs with `scripts/kcap_tool.py index`.
3. Extract only the resources needed for analysis. Do not publish extracted game assets.
4. Detect source encoding independently for each resource class. Typical combinations are CP932 source text, CP936 translated bytes, and ANSI GDI rendering.
5. Build a translation task manifest with stable IDs, source text, byte limits, line limits, and file offsets.
6. Translate against a terminology table. Validate byte lengths before writing.
7. Patch executable string slots with `scripts/patch_fixed_strings.py`.
8. Rebuild the font only when required. Preserve the family name expected by `CreateFontIndirectA`, and test glyphs through `scripts/gdi_glyph_probe.py`.
9. Re-render DDS text at the original canvas dimensions, pixel format, alpha mode, and aspect ratio.
10. Rebuild KCAP from the latest working pack, replacing only intended entries.
11. Test title, launcher, 4:3 scaling, menus, gameplay, replay/gallery screens, focus loss, Alt+Tab, and clean exit.
12. Assemble a clean release directory without backups, debug captures, source game archives, or API credentials.

## Fixed-Slot Rules

- Treat byte capacity and rendered glyph count as separate constraints.
- Do not assume `NUL` stops every draw loop. Some engines cache or draw the original number of glyph slots.
- When translated text is shorter and blank slots render as white rectangles, fill each missing double-byte glyph slot with a tested zero-bitmap character. For Simplified Chinese ANSI rendering this is commonly CP936 fullwidth space `A1 A1`, but verify it through GDI first.
- Do not use single-byte ASCII spaces to fill double-byte source slots.
- Record every offset, original capacity, replacement bytes, and padding policy.

## Font And Symbol Rules

- Determine the exact ANSI code received by `GetGlyphOutlineA`.
- Preserve special source symbols when semantically meaningful.
- If a Shift-JIS symbol decodes as mojibake under CP936, encode the original byte pair deliberately and map the resulting Unicode alias in the replacement font.
- Test the real font family, charset, height, quality, and API path used by the game. A successful Unicode cmap lookup alone is insufficient.

## Image And Resolution Rules

- Preserve original image dimensions unless code analysis proves the renderer supports another size.
- Keep the original display aspect ratio. Scale 640x480 content only to 4:3 modes such as 800x600, 960x720, or 1280x960.
- Avoid stretching 4:3 content into 16:9.
- Preserve DDS format, mip count, alpha semantics, and archive path.

## Validation Gate

Do not declare completion until replacement entries hash correctly, untouched pack entries match the selected base, executable diffs stay inside documented patches, translated bytes decode as intended, zero-bitmap padding has no visible bitmap, the packaged game launches, focus-loss tests pass, and the release includes a manifest and restoration instructions.

## Publication Safety

Publish scripts, schemas, documentation, and synthetic tests only. Exclude original executables, packs, fonts, music, voices, images, dialogue, translated game distributions, secrets, and proprietary SDK files.
