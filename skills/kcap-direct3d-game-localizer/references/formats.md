# Formats And Schemas

## KCAP Header

Little-endian layout:

```text
4 bytes  magic "KCAP"
4 bytes  entry count
N * 84 bytes directory entries
```

Directory entry:

```text
64 bytes CP932 path, NUL padded
4 bytes  hash1
4 bytes  hash2
4 bytes  payload offset
4 bytes  payload size
4 bytes  flags
```

Preserve directory order, metadata fields, and physical payload order when rebuilding.

## Task Manifest

JSON array:

```json
[
  {
    "id": "exe::0x123456",
    "kind": "exe",
    "offset": "0x123456",
    "source": "source text",
    "source_encoding": "cp932",
    "target_encoding": "cp936",
    "max_bytes": 24,
    "fixed_glyph_count": true
  }
]
```

## Translation Results

JSON Lines:

```json
{"id":"exe::0x123456","target":"translated text"}
```

## Padding Policies

- `nul`: translated bytes followed by `00`; use only when the draw path respects termination.
- `ascii-space`: one-byte `20`; unsafe for fixed double-byte glyph loops.
- `fullwidth-space`: CP936 `A1 A1`; use only after a zero-bitmap GDI test.

## Release Manifest

CSV columns:

```text
relative_path,size,sha256
```
