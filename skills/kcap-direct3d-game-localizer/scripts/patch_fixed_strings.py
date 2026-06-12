#!/usr/bin/env python3
"""Patch fixed-capacity executable strings from task and result manifests."""
from __future__ import annotations
import argparse,json
from pathlib import Path
def load_results(path):
    rows={}
    with path.open(encoding="utf-8-sig") as stream:
        for line in stream:
            if line.strip(): row=json.loads(line); rows[row["id"]]=row["target"]
    return rows
def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--input",type=Path,required=True); parser.add_argument("--tasks",type=Path,required=True); parser.add_argument("--results",type=Path,required=True); parser.add_argument("--output",type=Path,required=True); parser.add_argument("--default-target-encoding",default="cp936"); parser.add_argument("--padding",choices=("nul","ascii-space","fullwidth-space"),default="nul"); args=parser.parse_args()
    tasks=json.loads(args.tasks.read_text(encoding="utf-8-sig")); results=load_results(args.results); data=bytearray(args.input.read_bytes()); changes=[]
    for task in tasks:
        if task.get("kind")!="exe": continue
        task_id=task["id"]
        if task_id not in results: raise ValueError(f"Missing result: {task_id}")
        offset=int(str(task["offset"]),0); source_encoding=task.get("source_encoding","cp932"); target_encoding=task.get("target_encoding",args.default_target_encoding); capacity=int(task.get("max_bytes",len(task["source"].encode(source_encoding)))); target=results[task_id]; encoded=target.encode(target_encoding)
        if len(encoded)>capacity: raise ValueError(f"Byte overflow at {task_id}: {len(encoded)} > {capacity}")
        policy=task.get("padding",args.padding)
        if policy=="fullwidth-space":
            source_glyphs=int(task.get("source_glyph_count",len(task["source"]))); missing=source_glyphs-len(target)
            if missing<0: raise ValueError(f"Glyph overflow at {task_id}")
            encoded+="\u3000".encode(target_encoding)*missing
        elif policy=="ascii-space": encoded+=b" "*(capacity-len(encoded))
        if len(encoded)>capacity: raise ValueError(f"Padded byte overflow at {task_id}")
        data[offset:offset+capacity]=encoded+b"\0"*(capacity-len(encoded)); changes.append({"id":task_id,"offset":f"0x{offset:X}","capacity":capacity,"written":len(encoded),"padding":policy})
    args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_bytes(data); print(json.dumps({"changes":changes},ensure_ascii=False))
if __name__=="__main__": main()
