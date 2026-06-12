# Diagnostics

## White Rectangles After Text

Symptoms:

- one or more white blocks appear after a translated label;
- removing padding creates more blocks;
- the number of blocks tracks source/target glyph-count differences.

Likely cause:

- the renderer draws a fixed number of cached glyph slots;
- ASCII space or `NUL` produces an uninitialized Direct3D texture.

Procedure:

1. Compare source and target glyph counts.
2. Inspect the exact slot bytes.
3. Test candidate blank characters through `GetGlyphOutlineA`.
4. Use one zero-bitmap double-byte character per missing source glyph.
5. For CP936, test fullwidth space `A1 A1`.
6. Recheck every shortened display string, not just the reported example.

## Mojibake Symbol

Symptoms:

- a music note or Japanese punctuation becomes a Chinese character;
- ordinary Chinese displays correctly.

Procedure:

1. Identify the original CP932 bytes.
2. Decode those bytes under the runtime code page to find the alias.
3. Preserve the original bytes in the final resource.
4. Map the alias code point to the intended glyph in the bundled font.
5. Verify through ANSI GDI, not only Unicode font inspection.

## Replay Or Gallery Hang

Check:

- translated image dimensions and DDS headers;
- missing pack entries;
- out-of-range string bytes;
- glyph registration failures;
- blank-slot textures;
- save data compatibility;
- WER `AppHangB1` versus access violation.

If the screen uses many translated labels, repair glyph-slot handling before replacing unrelated graphics code.

## Alt+Tab Hang

Test the exact failing screen with repeated minimize/restore cycles. Monitor process `Responding`, window handle changes, and Direct3D device-reset behavior.

Compare:

- untouched resources for the selected character;
- font and glyph-cache changes;
- windowed/fullscreen configuration;
- whether the failure is actually an unresponsive render loop rather than a crash.

## Stretched Output

- Determine the logical canvas.
- Restrict selectable modes to the same aspect ratio.
- Check both launcher output and runtime viewport.
- Do not solve stretching by resizing UI textures alone.
